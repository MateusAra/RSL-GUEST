from fastapi.testclient import TestClient

from backend.api import app
from tests.helpers import create_execution, save_search_string


RIS_ONE = b"""TY  - JOUR
TI  - Explainable Multi-Agent Systems
AU  - Doe, Jane
PY  - 2024
JO  - Journal of XAI
DO  - 10.1234/xai.2024.1
AB  - Explanations in multi-agent systems.
KW  - XAI
ER  -
"""

BIBTEX_DUPLICATE = b"""@article{doe2024,
    title = {Unrelated Title for DOI Verification},
  author = {Doe, Jane},
  year = {2024},
  journal = {Journal of XAI},
  doi = {10.1234/xai.2024.1},
  abstract = {Explanations in multi-agent systems.},
  keywords = {XAI}
}"""


def _project(client: TestClient, token: str) -> dict:
    response = client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Busca de teste",
            "objective": "Testar importação e deduplicação.",
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


def _login(client: TestClient) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rsl.local", "password": "admin123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def _execution(client: TestClient, project_id: str, token: str, base: str) -> str:
    return create_execution(
        client,
        project_id,
        {"Authorization": f"Bearer {token}"},
        base,
        "(XAI) AND (multi-agent)",
        fields=["title", "abstract", "doi"],
    )["id"]


def test_import_archives_raw_result_and_dedup_keeps_human_decision():
    with TestClient(app) as client:
        token = _login(client)
        project = _project(client, token)
        headers = {"Authorization": f"Bearer {token}"}
        first_execution = _execution(client, project["id"], token, "scopus")
        first_import = client.post(
            f"/api/v1/search-executions/{first_execution}/imports",
            headers=headers,
            files={"file": ("results.ris", RIS_ONE, "application/octet-stream")},
        )
        assert first_import.status_code == 201, first_import.text
        assert first_import.json()["imported_count"] == 1
        assert len(first_import.json()["raw_sha256"]) == 64

        second_execution = _execution(client, project["id"], token, "web_of_science")
        second_import = client.post(
            f"/api/v1/search-executions/{second_execution}/imports",
            headers=headers,
            files={"file": ("results.bib", BIBTEX_DUPLICATE, "application/x-bibtex")},
        )
        assert second_import.status_code == 201
        assert second_import.json()["imported_count"] == 1

        dedup = client.post(
            f"/api/v1/projects/{project['id']}/deduplication/run",
            headers=headers,
        )
        assert dedup.status_code == 200
        candidates = dedup.json()["candidates"]
        assert len(candidates) == 1
        assert candidates[0]["match_type"] == "doi_exact"
        assert candidates[0]["decision"] == "duplicate"
        assert candidates[0]["method"] == "automatic"

        decision = client.post(
            f"/api/v1/duplicate-candidates/{candidates[0]['id']}/decision",
            headers=headers,
            json={
                "decision": "duplicate",
                "canonical_study_id": candidates[0]["study_ids"][0],
                "justification": "Mesmo DOI e mesma publicação.",
            },
        )
        assert decision.status_code == 200
        assert decision.json()["decision"] == "duplicate"

        repeated = client.post(
            f"/api/v1/projects/{project['id']}/deduplication/run",
            headers=headers,
        )
        assert repeated.status_code == 200
        assert len(repeated.json()["candidates"]) == 1
        studies = client.get(
            f"/api/v1/projects/{project['id']}/studies",
            headers=headers,
        )
        assert studies.status_code == 200
        assert len(studies.json()) == 2


def test_import_requires_project_role_and_supported_format():
    with TestClient(app) as client:
        token = _login(client)
        project = _project(client, token)
        execution_id = _execution(client, project["id"], token, "scopus")
        observer_login = client.post(
            "/api/v1/auth/login",
            json={"email": "observer@rsl.local", "password": "observer123"},
        ).json()
        no_permission = client.post(
            f"/api/v1/search-executions/{execution_id}/imports",
            headers={"Authorization": f"Bearer {observer_login['access_token']}"},
            files={"file": ("results.ris", RIS_ONE, "application/octet-stream")},
        )
        assert no_permission.status_code == 403

        unsupported = client.post(
            f"/api/v1/search-executions/{execution_id}/imports",
            headers={"Authorization": f"Bearer {token}"},
            files={"file": ("unsupported.txt", b"data", "text/plain")},
        )
        assert unsupported.status_code == 422


def test_search_query_and_google_scholar_limit_are_validated():
    with TestClient(app) as client:
        token = _login(client)
        project = _project(client, token)
        url = f"/api/v1/projects/{project['id']}/search-executions"
        headers = {"Authorization": f"Bearer {token}"}

        invalid_query = save_search_string(client, project["id"], headers, "scopus", "(XAI AND MAS")
        assert invalid_query.status_code == 422

        assert save_search_string(client, project["id"], headers, "google_scholar").status_code == 201
        over_limit = client.post(
            url,
            headers=headers,
            json={"base": "google_scholar", "reported_result_count": 300, "result_limit": 301},
        )
        assert over_limit.status_code == 422

        valid = client.post(
            url,
            headers=headers,
            json={"base": "google_scholar", "reported_result_count": 300, "result_limit": 300},
        )
        assert valid.status_code == 201
        assert valid.json()["result_limit"] == 300