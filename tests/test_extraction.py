from fastapi.testclient import TestClient

from backend.api import app


RIS_STUDY = b"""TY  - JOUR
TI  - Explainability in multi-agent systems
AU  - Doe, Jane
PY  - 2024
DO  - 10.1234/extraction.2024
ER  -
"""


def _create_project_and_study(client: TestClient) -> tuple[str, str]:
    admin_login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rsl.local", "password": "admin123"},
    ).json()
    headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
    project = client.post(
        "/api/v1/projects",
        headers=headers,
        json={
            "title": "Projeto de extração",
            "objective": "Testar cadeia de evidência.",
            "study_type": "systematic_literature_review",
            "members": [
                {"email": "reviewer@rsl.local", "role": "revisor"},
                {"email": "reviewer2@rsl.local", "role": "revisor"},
                {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
            ],
        },
    ).json()
    execution = client.post(
        f"/api/v1/projects/{project['id']}/search-executions",
        headers=headers,
        json={"base": "scopus", "query": "XAI AND MAS", "fields": ["title"]},
    ).json()
    imported = client.post(
        f"/api/v1/search-executions/{execution['id']}/imports",
        headers=headers,
        files={"file": ("study.ris", RIS_STUDY, "application/octet-stream")},
    )
    assert imported.status_code == 201
    return project["id"], imported.json()["study_ids"][0]


def test_substantive_extraction_requires_exact_quote_and_page():
    with TestClient(app) as client:
        project_id, study_id = _create_project_and_study(client)
        reviewer = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer@rsl.local", "password": "reviewer123"},
        ).json()
        headers = {"Authorization": f"Bearer {reviewer['access_token']}"}
        endpoint = f"/api/v1/projects/{project_id}/studies/{study_id}/extractions"

        missing_evidence = client.post(
            endpoint,
            headers=headers,
            json={"field_id": "Q-B1", "value": "MAS clássico", "expected_version": 0},
        )
        assert missing_evidence.status_code == 422

        missing_page = client.post(
            endpoint,
            headers=headers,
            json={"field_id": "Q-B1", "value": "MAS clássico", "quote": "Agents interact in a decentralized system.", "expected_version": 0},
        )
        assert missing_page.status_code == 422


def test_extraction_verification_requires_a_different_reviewer():
    with TestClient(app) as client:
        project_id, study_id = _create_project_and_study(client)
        first_login = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer@rsl.local", "password": "reviewer123"},
        ).json()
        second_login = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer2@rsl.local", "password": "reviewer2123"},
        ).json()
        first_headers = {"Authorization": f"Bearer {first_login['access_token']}"}
        second_headers = {"Authorization": f"Bearer {second_login['access_token']}"}
        created = client.post(
            f"/api/v1/projects/{project_id}/studies/{study_id}/extractions",
            headers=first_headers,
            json={
                "field_id": "Q-B1",
                "value": "MAS clássico",
                "quote": "Agents interact in a decentralized system.",
                "page_reference": "p. 2",
                "expected_version": 0,
            },
        )
        assert created.status_code == 201, created.text

        self_verify = client.post(
            f"/api/v1/extractions/{created.json()['id']}/verification",
            headers=first_headers,
            json={"decision": "verified", "justification": "Conferi no PDF."},
        )
        assert self_verify.status_code == 403

        verified = client.post(
            f"/api/v1/extractions/{created.json()['id']}/verification",
            headers=second_headers,
            json={"decision": "verified", "justification": "Citação e página conferidas."},
        )
        assert verified.status_code == 201
        assert verified.json()["status"] == "verified"


def test_identification_field_needs_no_evidence_and_catalog_is_closed():
    with TestClient(app) as client:
        project_id, study_id = _create_project_and_study(client)
        reviewer = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer@rsl.local", "password": "reviewer123"},
        ).json()
        headers = {"Authorization": f"Bearer {reviewer['access_token']}"}
        endpoint = f"/api/v1/projects/{project_id}/studies/{study_id}/extractions"

        title = client.post(
            endpoint,
            headers=headers,
            json={"field_id": "Q-O1", "value": "Explainability in multi-agent systems", "expected_version": 0},
        )
        assert title.status_code == 201

        unknown = client.post(
            endpoint,
            headers=headers,
            json={"field_id": "Q-Z1", "value": "Unknown", "expected_version": 0},
        )
        assert unknown.status_code == 422