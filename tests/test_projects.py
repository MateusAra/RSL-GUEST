from fastapi.testclient import TestClient

from backend.api import app


def _login(client: TestClient, email: str = "admin@rsl.local") -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "admin123" if email == "admin@rsl.local" else "reviewer123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_create_project_requires_protocol_team_and_assigns_project_roles():
    with TestClient(app) as client:
        admin_token = _login(client)
        response = client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Estudo de teste",
                "objective": "Validar o cadastro de projeto no MVP.",
                "study_type": "systematic_literature_review",
                "members": [
                    {"email": "reviewer@rsl.local", "role": "revisor"},
                    {"email": "reviewer2@rsl.local", "role": "revisor"},
                    {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
                ],
            },
        )

        assert response.status_code == 201, response.text
        project = response.json()
        assert project["title"] == "Estudo de teste"
        assert len(project["members"]) == 4
        assert {member["role"] for member in project["members"]} == {
            "admin",
            "revisor",
            "terceiro_revisor",
        }

        fetched = client.get(
            f"/api/v1/projects/{project['id']}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert fetched.status_code == 200
        assert fetched.json()["id"] == project["id"]


def test_project_creation_rejects_incomplete_reviewer_team():
    with TestClient(app) as client:
        admin_token = _login(client)
        response = client.post(
            "/api/v1/projects",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "title": "Equipe incompleta",
                "objective": "Este projeto deve ser recusado.",
                "study_type": "systematic_literature_review",
                "members": [{"email": "reviewer@rsl.local", "role": "revisor"}],
            },
        )

        assert response.status_code == 422


def test_project_endpoints_require_authentication():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/projects",
            json={
                "title": "Sem autenticação",
                "objective": "Não pode criar.",
                "study_type": "systematic_literature_review",
                "members": [],
            },
        )

        assert response.status_code == 401