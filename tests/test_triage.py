from fastapi.testclient import TestClient
import pytest

from backend.api import app
from tests.helpers import create_execution
from rsl_foundation import classify_triage_pair


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ("incluir", "incluir", ("A", "included")),
        ("incluir", "incerto", ("B", "advances")),
        ("incerto", "incerto", ("C", "advances")),
        ("incluir", "excluir", ("D", "consensus_required")),
        ("incerto", "excluir", ("E", "consensus_required")),
        ("excluir", "excluir", ("F", "excluded")),
    ],
)
def test_protocol_vote_matrix(first, second, expected):
    assert classify_triage_pair(first, second) == expected
    assert classify_triage_pair(second, first) == expected


def test_peer_vote_is_hidden_until_both_reviewers_confirm():
    with TestClient(app) as client:
        admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        ).json()
        admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
        project_response = client.post(
            "/api/v1/projects",
            headers=admin_headers,
            json={
                "title": "Projeto de triagem",
                "objective": "Validar votos independentes.",
                "study_type": "systematic_literature_review",
                "members": [
                    {"email": "reviewer@rsl.local", "role": "revisor"},
                    {"email": "reviewer2@rsl.local", "role": "revisor"},
                    {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
                ],
            },
        )
        project_id = project_response.json()["id"]
        criterion = client.post(
            f"/api/v1/projects/{project_id}/configuration/criteria/CI1",
            headers=admin_headers,
            json={"data": {"text": "Aborda MAS."}},
        )
        assert criterion.status_code == 201

        execution = create_execution(client, project_id, admin_headers)
        imported = client.post(
            f"/api/v1/search-executions/{execution['id']}/imports",
            headers=admin_headers,
            files={"file": ("study.ris", b"TY  - JOUR\nTI  - A Study of XAI in MAS\nAU  - Doe\nPY  - 2024\nER  -\n", "application/octet-stream")},
        )
        assert imported.status_code == 201
        study_id = imported.json()["study_ids"][0]

        reviewer_one = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer@rsl.local", "password": "reviewer123"},
        ).json()
        reviewer_two = client.post(
            "/api/v1/auth/login",
            json={"email": "reviewer2@rsl.local", "password": "reviewer2123"},
        ).json()
        reviewer_one_headers = {"Authorization": f"Bearer {reviewer_one['access_token']}"}
        reviewer_two_headers = {"Authorization": f"Bearer {reviewer_two['access_token']}"}
        vote_url = f"/api/v1/projects/{project_id}/studies/{study_id}/triage-votes"

        first_vote = client.post(
            vote_url,
            headers=reviewer_one_headers,
            json={"phase": 1, "vote": "incluir", "confirm": True, "expected_version": 0},
        )
        assert first_vote.status_code == 201, first_vote.text

        private_status = client.get(
            f"/api/v1/projects/{project_id}/studies/{study_id}/triage-status?phase=1",
            headers=reviewer_two_headers,
        )
        assert private_status.status_code == 200
        assert private_status.json()["peer_status"] == "confirmed"
        assert "peer_vote" not in private_status.json()

        second_vote = client.post(
            vote_url,
            headers=reviewer_two_headers,
            json={"phase": 1, "vote": "incluir", "confirm": True, "expected_version": 0},
        )
        assert second_vote.status_code == 201

        visible_status = client.get(
            f"/api/v1/projects/{project_id}/studies/{study_id}/triage-status?phase=1",
            headers=reviewer_one_headers,
        )
        assert visible_status.status_code == 200
        assert visible_status.json()["matrix_letter"] == "A"
        assert visible_status.json()["result"] == "included"
        assert visible_status.json()["peer_vote"]["vote"] == "incluir"