"""Critérios de aceite da spec 005 — Avaliação de qualidade (CT-QA-01..10)."""

import random

import pytest
from fastapi.testclient import TestClient

from backend.api import app
from rsl_foundation.quality import (
    QA_V4_INSTRUMENT,
    QUALITY_OUTCOMES,
    calculate_quality_scores,
    calculate_weighted_kappa,
    classify_quality_score,
)
from tests.helpers import (
    REVIEWER_ONE,
    REVIEWER_TWO,
    THIRD_REVIEWER,
    auth,
    configure,
    create_execution,
    create_project,
    import_file,
    login,
    ris,
)

CRITERIA = [f"Q{index}" for index in range(1, 11)]


def _project_with_studies(client: TestClient, count: int = 1) -> tuple[str, list[str], dict]:
    headers = auth(login(client))
    project_id = create_project(client, login(client), "QA")["id"]
    execution = create_execution(client, project_id, headers, "scopus", reported_result_count=count)
    imported = import_file(client, execution["id"], headers, "qa.ris",
                           ris(*({"title": f"QA study {index:03d} {random.random()}", "year": 2024} for index in range(count))))
    assert imported.status_code == 201
    return project_id, imported.json()["study_ids"], headers


def _submit(client, project_id, study_id, credentials, scores, *, confirm=True, expected_version=0, justification="Conferido no texto."):
    return client.post(
        f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments",
        headers=auth(login(client, *credentials)),
        json={
            "scores": [
                {"criterion_id": criterion_id, "score": score, "justification": justification}
                for criterion_id, score in zip(CRITERIA, scores)
            ],
            "confirm": confirm,
            "expected_version": expected_version,
        },
    )


def _status(client, project_id, study_id, credentials):
    return client.get(
        f"/api/v1/projects/{project_id}/studies/{study_id}/quality-status",
        headers=auth(login(client, *credentials)),
    ).json()


def test_ca_01_instrument_outside_protocol_requires_deviation_justification():
    instrument = {"criteria": QA_V4_INSTRUMENT["criteria"][:9], "min_applicable": 7}
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        rejected = configure(client, project_id, headers, "qa_instrument", "default", instrument)
        assert rejected.status_code == 422
        assert "deviation_justification" in rejected.json()["detail"]

        accepted = configure(client, project_id, headers, "qa_instrument", "default",
                             {**instrument, "deviation_justification": "Q10 coberta pela extração."})
        assert accepted.status_code == 201
        assert accepted.json()["warnings"] == ["instrument has 9 criteria instead of 10"]
        deviations = client.get(f"/api/v1/projects/{project_id}/deviations", headers=headers).json()
        assert deviations[0]["affected_section"] == "§7.4"
        assert accepted.json()["data"]["deviation_id"] == deviations[0]["id"]

        current = client.get(f"/api/v1/projects/{project_id}/quality/instrument", headers=headers).json()
        assert (current["source"], len(current["criteria"])) == ("project", 9)


def test_ca_02_not_applicable_items_leave_the_denominator():
    scores = dict(zip(CRITERIA, [1, 1, 1, 1, 1, None, None, 1, 0, 0]))
    result = calculate_quality_scores(scores)
    assert result["score"] == 7.5
    assert result["not_applicable_count"] == 2


def test_ca_03_scored_criterion_requires_justification():
    with TestClient(app) as client:
        project_id, (study_id,), _ = _project_with_studies(client)
        assert _submit(client, project_id, study_id, REVIEWER_ONE, [1] * 10, justification=" ").status_code == 422
        assert _submit(client, project_id, study_id, REVIEWER_ONE, [1] * 10).status_code == 201


def test_ca_04_peer_ratings_stay_hidden_until_both_confirm():
    with TestClient(app) as client:
        project_id, (study_id,), _ = _project_with_studies(client)
        _submit(client, project_id, study_id, REVIEWER_ONE, [1] * 10)
        hidden = _status(client, project_id, study_id, REVIEWER_TWO)
        assert hidden["peer_status"] == "confirmed"
        assert "peer_assessment" not in hidden


@pytest.mark.parametrize(("score", "outcome"), [(7.0, "aprovado"), (6.9, "ressalva"), (3.9, "excluido_qualidade")])
def test_ca_05_cutoff_bands(score, outcome):
    assert QUALITY_OUTCOMES[classify_quality_score(score)] == outcome


def test_ca_06_low_score_excludes_study_with_reason_and_updates_prisma_count():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project_with_studies(client)
        low = [0.5, 0, 0.5, 0, 0.5, 0, 0, 0.5, 0, 0.5]
        _submit(client, project_id, study_id, REVIEWER_ONE, low)
        _submit(client, project_id, study_id, REVIEWER_TWO, low)
        summary = client.get(f"/api/v1/projects/{project_id}/quality/summary", headers=headers).json()
        assert summary["excluded"] == [
            {"study_id": study_id, "title": summary["studies"][0]["title"], "reason": "qualidade", "final_score": 2.5}
        ]
        assert summary["counts"]["excluido_qualidade"] == 1
        studies = client.get(f"/api/v1/projects/{project_id}/studies", headers=headers).json()
        assert [study["id"] for study in studies] == [study_id]


def _manual_linear_weighted_kappa(first: list[float], second: list[float]) -> float:
    """Independent reference: Cohen's kappa with linear weights over the 0/0.5/1 scale."""
    categories = [0, 0.5, 1]
    size = len(first)
    observed = [[0.0] * 3 for _ in categories]
    for left, right in zip(first, second):
        observed[categories.index(left)][categories.index(right)] += 1 / size
    row = [sum(values) for values in observed]
    column = [sum(observed[i][j] for i in range(3)) for j in range(3)]
    weight = [[abs(i - j) / 2 for j in range(3)] for i in range(3)]
    disagreement = sum(weight[i][j] * observed[i][j] for i in range(3) for j in range(3))
    expected = sum(weight[i][j] * row[i] * column[j] for i in range(3) for j in range(3))
    return 1 - disagreement / expected


def test_ca_07_project_weighted_kappa_over_20_studies_matches_manual_reference():
    generator = random.Random(7)
    with TestClient(app) as client:
        project_id, study_ids, headers = _project_with_studies(client, 20)
        first_all, second_all = [], []
        for study_id in study_ids:
            first = [generator.choice([0, 0.5, 1]) for _ in CRITERIA]
            second = [value if generator.random() < 0.7 else generator.choice([0, 0.5, 1]) for value in first]
            assert _submit(client, project_id, study_id, REVIEWER_ONE, first).status_code == 201
            assert _submit(client, project_id, study_id, REVIEWER_TWO, second).status_code == 201
            first_all.extend(first)
            second_all.extend(second)
        summary = client.get(f"/api/v1/projects/{project_id}/quality/summary", headers=headers).json()
        kappa = summary["initial_weighted_kappa"]
        assert kappa["studies"] == 20
        assert kappa["rated_items"] == 200
        assert kappa["value"] == pytest.approx(_manual_linear_weighted_kappa(first_all, second_all), abs=0.001)
        assert kappa["value"] == pytest.approx(calculate_weighted_kappa(first_all, second_all), abs=0.001)


def test_ca_08_large_item_difference_goes_to_third_reviewer_and_small_one_is_averaged():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project_with_studies(client)
        _submit(client, project_id, study_id, REVIEWER_ONE, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        _submit(client, project_id, study_id, REVIEWER_TWO, [0, 0.5, 1, 1, 1, 1, 1, 1, 1, 1])

        status = _status(client, project_id, study_id, REVIEWER_ONE)
        assert status["disputed_criteria"] == ["Q1"]
        assert status["status"] == "awaiting_arbitration"
        summary = client.get(f"/api/v1/projects/{project_id}/quality/summary", headers=headers).json()
        assert summary["arbitration_queue"] == [{"study_id": study_id, "criteria": ["Q1"]}]

        arbitration_url = f"/api/v1/projects/{project_id}/studies/{study_id}/quality-arbitrations"
        payload = {"criterion_id": "Q1", "score": 0.5, "justification": "Objetivo presente mas impreciso."}
        assert client.post(arbitration_url, headers=auth(login(client, *REVIEWER_ONE)), json=payload).status_code == 403
        assert client.post(arbitration_url, headers=auth(login(client, *THIRD_REVIEWER)),
                           json={**payload, "criterion_id": "Q2"}).status_code == 422
        assert client.post(arbitration_url, headers=auth(login(client, *THIRD_REVIEWER)), json=payload).status_code == 201

        final = _status(client, project_id, study_id, REVIEWER_TWO)
        assert final["status"] == "final"
        # Q1 = 0.5 (R3), Q2 = mean(1, 0.5) = 0.75, Q3..Q10 = 1 -> 9.25
        assert final["final_score"] == 9.25
        assert final["final_outcome"] == "aprovado"


def test_ca_09_change_after_confirmation_requires_reopening_and_is_audited():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project_with_studies(client)
        first = _submit(client, project_id, study_id, REVIEWER_ONE, [1] * 10)
        assert _submit(client, project_id, study_id, REVIEWER_ONE, [0.5] * 10, expected_version=1).status_code == 409

        reopen_url = f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments/reopen"
        reviewer = auth(login(client, *REVIEWER_ONE))
        assert client.post(reopen_url, headers=reviewer, json={"justification": " "}).status_code == 422
        reopened = client.post(reopen_url, headers=reviewer, json={"justification": "Releitura da seção 4."})
        assert reopened.status_code == 200
        changed = _submit(client, project_id, study_id, REVIEWER_ONE, [0.5] * 10,
                          expected_version=reopened.json()["version"])
        assert changed.status_code == 201

        events = [event for event in client.get("/api/v1/audit-events", headers=headers).json()
                  if event["entity_id"] == first.json()["id"]]
        latest = events[0]
        assert latest["action"] == "quality_assessment_confirmed"
        assert latest["previous_value"]["score"] == 10.0
        assert latest["new_value"]["score"] == 5.0
        assert latest["new_value"]["justification"] == "Releitura da seção 4."
        assert latest["actor_user_id"] == "u-r1"
        assert "quality_assessment_reopened" in {event["action"] for event in events}


def test_ca_10_category_scores_are_reported_separately_from_total():
    with TestClient(app) as client:
        project_id, (study_id,), _ = _project_with_studies(client)
        response = _submit(client, project_id, study_id, REVIEWER_ONE, [1, 1, 1, 1, 0.5, 0.5, 0, 1, 1, 1])
        body = response.json()
        assert body["category_scores"]["reporting"] == 10.0
        assert body["category_scores"]["rigor"] == 5.0
        assert body["score"] == 8.0


def test_rule_11_initial_kappa_is_not_overwritten_after_resolution():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project_with_studies(client)
        _submit(client, project_id, study_id, REVIEWER_ONE, [1, 1, 1, 1, 1, 1, 1, 0, 0, 0.5])
        _submit(client, project_id, study_id, REVIEWER_TWO, [1, 0.5, 1, 0, 1, 1, 0.5, 0, 0, 0.5])
        before = client.get(f"/api/v1/projects/{project_id}/quality/summary", headers=headers).json()

        reviewer = auth(login(client, *REVIEWER_TWO))
        reopened = client.post(
            f"/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments/reopen",
            headers=reviewer, json={"justification": "Consenso após discussão."},
        ).json()
        _submit(client, project_id, study_id, REVIEWER_TWO, [1, 1, 1, 1, 1, 1, 1, 0, 0, 0.5],
                expected_version=reopened["version"])
        after = client.get(f"/api/v1/projects/{project_id}/quality/summary", headers=headers).json()
        assert after["initial_weighted_kappa"] == before["initial_weighted_kappa"]
        assert after["studies"][0]["status"] == "final"


def test_edge_not_applicable_disagreement_goes_to_arbitration():
    with TestClient(app) as client:
        project_id, (study_id,), _ = _project_with_studies(client)
        _submit(client, project_id, study_id, REVIEWER_ONE, [1, 1, 1, 1, 1, None, 1, 1, 1, 1])
        _submit(client, project_id, study_id, REVIEWER_TWO, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
        assert _status(client, project_id, study_id, REVIEWER_ONE)["pending_arbitration"] == ["Q6"]
