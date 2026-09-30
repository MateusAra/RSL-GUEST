from fastapi.testclient import TestClient

from backend.api import app


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _create_project(client: TestClient, token: str) -> dict:
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Projeto de configuração",
            "objective": "Testar configuração versionada.",
            "study_type": "systematic_literature_review",
            "members": [
                {"email": "reviewer@rsl.local", "role": "revisor"},
                {"email": "reviewer2@rsl.local", "role": "revisor"},
                {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
            ],
        },
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_protocol_is_versioned_and_frozen_versions_remain_unchanged():
    with TestClient(app) as client:
        admin_token = _login(client, "admin@rsl.local", "admin123")
        project = _create_project(client, admin_token)
        url = f"/api/v1/projects/{project['id']}/configuration/protocol/protocolo-v4"
        headers = {"Authorization": f"Bearer {admin_token}"}

        first = client.post(
            url,
            headers=headers,
            json={"data": {"text": "Versão 4.0\nObjetivo inicial", "description": "Carga do protocolo v4.0", "frozen": True}},
        )
        second = client.post(
            url,
            headers=headers,
            json={"data": {"text": "Versão 4.1\nObjetivo revisado", "description": "Ajuste aprovado", "frozen": True}},
        )

        assert first.status_code == 201
        assert first.json()["version"] == 1
        assert second.status_code == 201
        assert second.json()["version"] == 2
        assert "-Objetivo inicial" in second.json()["diff"]

        versions = client.get(
            f"/api/v1/projects/{project['id']}/configuration?kind=protocol",
            headers=headers,
        )
        assert [version["data"]["text"] for version in versions.json()] == [
            "Versão 4.0\nObjetivo inicial",
            "Versão 4.1\nObjetivo revisado",
        ]


def test_configuration_validates_glossary_picoc_hypotheses_and_verdicts():
    with TestClient(app) as client:
        admin_token = _login(client, "admin@rsl.local", "admin123")
        project = _create_project(client, admin_token)
        headers = {"Authorization": f"Bearer {admin_token}"}
        prefix = f"/api/v1/projects/{project['id']}/configuration"

        invalid_glossary = client.post(
            f"{prefix}/glossary/MAS",
            headers=headers,
            json={"data": {"definition": "Sistema multiagente."}},
        )
        assert invalid_glossary.status_code == 422

        glossary = client.post(
            f"{prefix}/glossary/MAS",
            headers=headers,
            json={"data": {"definition": "Sistema multiagente.", "criteria_links": ["CI1"]}},
        )
        assert glossary.status_code == 201

        invalid_picoc = client.post(
            f"{prefix}/picoc/main",
            headers=headers,
            json={"data": {"elements": {"population": "MAS"}}},
        )
        assert invalid_picoc.status_code == 422

        picoc = client.post(
            f"{prefix}/picoc/main",
            headers=headers,
            json={"data": {"elements": {
                "population": "MAS", "intervention": "XAI", "comparison": "Trust clássico",
                "outcome": "Transparência", "context": "Ecossistemas agênticos",
            }, "subquestions": ["Q1"]}},
        )
        assert picoc.status_code == 201

        hypothesis = client.post(
            f"{prefix}/hypothesis/H1",
            headers=headers,
            json={"data": {
                "independent_variables": ["integração XAI"],
                "dependent_variables": ["transparência"],
                "operational_criteria": ["evidência textual"],
            }},
        )
        assert hypothesis.status_code == 201

        verdicts = ["suporta", "parcialmente suporta", "refuta", "inconclusivo"]
        verdict_config = client.post(
            f"{prefix}/verdict_rules/default",
            headers=headers,
            json={"data": {"verdicts": verdicts}},
        )
        assert verdict_config.status_code == 201


def test_project_role_controls_configuration_and_deviation_logging():
    with TestClient(app) as client:
        admin_token = _login(client, "admin@rsl.local", "admin123")
        project = _create_project(client, admin_token)
        reviewer_token = _login(client, "reviewer@rsl.local", "reviewer123")
        prefix = f"/api/v1/projects/{project['id']}"

        reviewer_read = client.get(
            f"{prefix}/configuration",
            headers={"Authorization": f"Bearer {reviewer_token}"},
        )
        assert reviewer_read.status_code == 200

        reviewer_write = client.post(
            f"{prefix}/configuration/protocol/protocolo-v4",
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json={"data": {"text": "Alteração", "description": "Não permitida"}},
        )
        assert reviewer_write.status_code == 403

        missing_justification = client.post(
            f"{prefix}/deviations",
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json={"stage": "busca", "description": "Mudança sem justificativa", "justification": "", "affected_section": "§5"},
        )
        assert missing_justification.status_code == 422

        deviation = client.post(
            f"{prefix}/deviations",
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json={"stage": "busca", "description": "Ajuste de execução", "justification": "Base alterou a sintaxe aceita.", "affected_section": "§5.1"},
        )
        assert deviation.status_code == 201
        assert deviation.json()["author_user_id"] == "u-r1"