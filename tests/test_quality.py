from fastapi.testclient import TestClient
import pytest

from backend.api import app
from tests.helpers import create_execution
from rsl_foundation import calculate_weighted_kappa


@pytest.mark.parametrize(
    ("first", "second", "expected"),
    [
        ([0, 0.5, 1], [0, 0.5, 1], 1.0),
        ([0, 0, 0.5, 0.5], [0, 0.5, 0, 0.5], 0.0),
        ([0, 0, 0.5, 1], [0, 0.5, 1, 1], 0.5),
    ],
)
def test_weighted_kappa_matches_three_manual_reference_cases(first, second, expected):
    assert calculate_weighted_kappa(first, second) == pytest.approx(expected, abs=0.001)


def _login(client: TestClient, email: str, password: str) -> str:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _project_and_study(client: TestClient) -> tuple[str, str, str]:
    admin_token = _login(client, "admin@rsl.local", "admin123")
    project = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Projeto QA",
            "objective": "Testar avaliação de qualidade.",
            "study_type": "systematic_literature_review",
            "members": [
                {"email": "reviewer@rsl.local", "role": "revisor"},
                {"email": "reviewer2@rsl.local", "role": "revisor"},
                {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
            ],
        },
    ).json()
    execution = create_execution(client, project['id'], {"Authorization": f"Bearer {admin_token}"})
    imported = client.post(
        f"/api/v1/search-executions/{execution['id']}/imports",
        headers={"Authorization": f"Bearer {admin_token}"},
        files={"file": ("study.ris", b"TY  - JOUR\nTI  - A Study of XAI in MAS\nAU  - Doe\nPY  - 2024\nER  -\n", "application/octet-stream")},
    )
    assert imported.status_code == 201
    return project["id"], imported.json()["study_ids"][0], admin_token


def _assessment(scores: list[float | None], confirm: bool = True, expected_version: int = 0) -> dict:
    return {
        "scores": [
            {"criterion_id": f"Q{index + 1}", "score": score, "justification": "Conferido no texto do estudo."}
            for index, score in enumerate(scores)
        ],
        "confirm": confirm,
        "expected_version": expected_version,
    }


def test_quality_scoring_applies_allowed_na_and_reports_categories():
    with TestClient(app) as client:
        project_id, study_id, admin_token = _project_and_study(client)
        reviewer_token = _login(client, "reviewer@rsl.local", "reviewer123")
        response = client.post(
            f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments",
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json=_assessment([1, 1, 1, 1, 1, None, None, 1, 0, 0]),
        )

        assert response.status_code == 201, response.text
        assert response.json()["score"] == 7.5
        assert response.json()["classification"] == "alta"
        assert response.json()["category_scores"]["reporting"] == 10.0


def test_quality_peer_ratings_are_hidden_until_both_confirm_and_kappa_warns():
    with TestClient(app) as client:
        project_id, study_id, _ = _project_and_study(client)
        first_token = _login(client, "reviewer@rsl.local", "reviewer123")
        second_token = _login(client, "reviewer2@rsl.local", "reviewer2123")
        endpoint = f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments"

        first = client.post(
            endpoint,
            headers={"Authorization": f"Bearer {first_token}"},
            json=_assessment([1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),
        )
        assert first.status_code == 201

        hidden = client.get(
            f"/api/v1/projects/{project_id}/studies/{study_id}/quality-status",
            headers={"Authorization": f"Bearer {second_token}"},
        )
        assert hidden.status_code == 200
        assert "peer_assessment" not in hidden.json()

        second = client.post(
            endpoint,
            headers={"Authorization": f"Bearer {second_token}"},
            json=_assessment([0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        )
        assert second.status_code == 201

        visible = client.get(
            f"/api/v1/projects/{project_id}/studies/{study_id}/quality-status",
            headers={"Authorization": f"Bearer {first_token}"},
        )
        assert visible.status_code == 200
        assert visible.json()["peer_assessment"]["score"] == 0.0
        assert visible.json()["weighted_kappa"] < 0.6
        assert visible.json()["kappa_warning"] is True


def test_quality_rejects_ineligible_na_and_missing_justification():
    with TestClient(app) as client:
        project_id, study_id, _ = _project_and_study(client)
        reviewer_token = _login(client, "reviewer@rsl.local", "reviewer123")
        endpoint = f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments"
        invalid_na = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        invalid_na[0] = None
        rejected_na = client.post(
            endpoint,
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json=_assessment(invalid_na),
        )
        assert rejected_na.status_code == 422

        missing_justification = _assessment([1] * 10)
        missing_justification["scores"][0]["justification"] = ""
        rejected_reason = client.post(
            endpoint,
            headers={"Authorization": f"Bearer {reviewer_token}"},
            json=missing_justification,
        )
        assert rejected_reason.status_code == 422