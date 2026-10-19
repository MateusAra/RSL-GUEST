"""Critérios de aceite da spec 004 tocados por RF26 — consenso D/E e terceiro revisor (CT-TRI-03, 07, 11)."""

import pytest
from fastapi.testclient import TestClient

from backend.api import app
from rsl_foundation.triage import resolve_conflict
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


def _project(client: TestClient, studies: int = 1) -> tuple[str, list[str], dict]:
    headers = auth(login(client))
    project_id = create_project(client, login(client), "Triagem")["id"]
    for key, text in (("CI1", "Aborda MAS."), ("CE4", "Agente isolado."), ("CE5", "Não aborda XAI.")):
        assert configure(client, project_id, headers, "criteria", key, {"text": text}).status_code == 201
    execution = create_execution(client, project_id, headers, "scopus", reported_result_count=studies)
    imported = import_file(client, execution["id"], headers, "t.ris",
                           ris(*({"title": f"Triage study {index}", "year": 2024} for index in range(studies))))
    return project_id, imported.json()["study_ids"], headers


def _vote(client, project_id, study_id, credentials, vote, phase=1, criterion=None):
    response = client.post(
        f"/api/v1/projects/{project_id}/studies/{study_id}/triage-votes",
        headers=auth(login(client, *credentials)),
        json={"phase": phase, "vote": vote, "criterion_id": criterion, "confirm": True, "expected_version": 0},
    )
    assert response.status_code == 201, response.text


def _resolve(client, project_id, study_id, credentials, stage, decision, phase=1, criterion=None,
             justification="Discutido na reunião de consenso."):
    return client.post(
        f"/api/v1/projects/{project_id}/studies/{study_id}/triage-{stage}",
        headers=auth(login(client, *credentials)),
        json={"phase": phase, "decision": decision, "criterion_id": criterion, "justification": justification},
    )


def _conflicts(client, project_id, credentials, phase=1):
    response = client.get(f"/api/v1/projects/{project_id}/triage/conflicts?phase={phase}",
                          headers=auth(login(client, *credentials)))
    assert response.status_code == 200, response.text
    return response.json()


@pytest.mark.parametrize(
    ("positions", "arbitration", "expected"),
    [
        ([], None, ("awaiting_consensus", None)),
        (["incluir"], None, ("awaiting_consensus", None)),
        (["incluir", "incluir"], None, ("resolved_by_consensus", "included")),
        (["excluir", "excluir"], None, ("resolved_by_consensus", "excluded")),
        (["incluir", "excluir"], None, ("escalated", None)),
        (["sem_consenso", "sem_consenso"], None, ("escalated", None)),
        (["incluir", "excluir"], "excluir", ("resolved_by_arbitration", "excluded")),
    ],
)
def test_resolve_conflict_rules(positions, arbitration, expected):
    assert resolve_conflict(positions, arbitration) == expected


def test_ca_03_double_exclusion_leaves_pool_and_d_goes_to_conflict_queue():
    with TestClient(app) as client:
        project_id, (excluded_id, conflict_id), _ = _project(client, 2)
        for credentials in (REVIEWER_ONE, REVIEWER_TWO):
            _vote(client, project_id, excluded_id, credentials, "excluir", criterion="CE5")
        _vote(client, project_id, conflict_id, REVIEWER_ONE, "incluir")
        _vote(client, project_id, conflict_id, REVIEWER_TWO, "excluir", criterion="CE4")

        status = client.get(f"/api/v1/projects/{project_id}/studies/{excluded_id}/triage-status?phase=1",
                            headers=auth(login(client, *REVIEWER_ONE))).json()
        assert (status["matrix_letter"], status["final_result"]) == ("F", "excluded")
        queue = _conflicts(client, project_id, REVIEWER_ONE)
        assert [(item["study_id"], item["matrix_letter"], item["status"]) for item in queue] == [
            (conflict_id, "D", "awaiting_consensus")
        ]
        assert queue[0]["final_result"] == "consensus_required"


def test_ca_07_consensus_closes_conflict_and_is_audited():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project(client)
        _vote(client, project_id, study_id, REVIEWER_ONE, "incerto", criterion="CI1")
        _vote(client, project_id, study_id, REVIEWER_TWO, "excluir", criterion="CE4")

        partial = _resolve(client, project_id, study_id, REVIEWER_ONE, "consensus", "incluir")
        assert partial.status_code == 201, partial.text
        assert partial.json()["status"] == "awaiting_consensus"
        final = _resolve(client, project_id, study_id, REVIEWER_TWO, "consensus", "incluir")
        assert final.json()["status"] == "resolved_by_consensus"
        assert final.json()["final_result"] == "included"
        assert _conflicts(client, project_id, REVIEWER_ONE)[0]["status"] == "resolved_by_consensus"

        events = client.get("/api/v1/audit-events", headers=headers).json()
        recorded = [event for event in events if event["action"] == "triage_consensus_recorded"
                    and event["new_value"]["study_id"] == study_id]
        assert {event["actor_user_id"] for event in recorded} == {"u-r1", "u-r2"}
        assert all(event["new_value"]["justification"] for event in recorded)


def test_ca_07_no_consensus_escalates_to_third_reviewer_who_arbitrates_with_author_and_date():
    with TestClient(app) as client:
        project_id, (study_id,), headers = _project(client)
        _vote(client, project_id, study_id, REVIEWER_ONE, "incluir")
        _vote(client, project_id, study_id, REVIEWER_TWO, "excluir", criterion="CE4")

        # Rule 6: before the consensus attempt the third reviewer neither sees nor arbitrates.
        assert _conflicts(client, project_id, THIRD_REVIEWER) == []
        early = _resolve(client, project_id, study_id, THIRD_REVIEWER, "arbitration", "incluir")
        assert early.status_code == 409

        _resolve(client, project_id, study_id, REVIEWER_ONE, "consensus", "incluir")
        escalated = _resolve(client, project_id, study_id, REVIEWER_TWO, "consensus", "sem_consenso")
        assert escalated.json()["status"] == "escalated"
        queue = _conflicts(client, project_id, THIRD_REVIEWER)
        assert [item["study_id"] for item in queue] == [study_id]
        assert queue[0]["votes"][1]["criterion_id"] == "CE4"

        assert _resolve(client, project_id, study_id, REVIEWER_ONE, "arbitration", "incluir").status_code == 403
        missing_ce = _resolve(client, project_id, study_id, THIRD_REVIEWER, "arbitration", "excluir")
        assert missing_ce.status_code == 422
        arbitration = _resolve(client, project_id, study_id, THIRD_REVIEWER, "arbitration", "excluir",
                               criterion="CE4", justification="Agente isolado, sem interação MAS.")
        assert arbitration.status_code == 201, arbitration.text
        body = arbitration.json()
        assert (body["status"], body["final_result"]) == ("resolved_by_arbitration", "excluded")
        assert body["arbitration"]["user_id"] == "u-r3"
        assert body["arbitration"]["created_at"]
        assert _resolve(client, project_id, study_id, THIRD_REVIEWER, "arbitration", "incluir").status_code == 409

        events = client.get("/api/v1/audit-events", headers=headers).json()
        assert any(event["action"] == "triage_arbitration_recorded" and event["actor_user_id"] == "u-r3"
                   for event in events)


def test_ca_11_e_combination_in_either_order_goes_to_conflict_queue():
    with TestClient(app) as client:
        project_id, (first_id, second_id), _ = _project(client, 2)
        _vote(client, project_id, first_id, REVIEWER_ONE, "incerto", criterion="CI1")
        _vote(client, project_id, first_id, REVIEWER_TWO, "excluir", criterion="CE5")
        _vote(client, project_id, second_id, REVIEWER_ONE, "excluir", criterion="CE5")
        _vote(client, project_id, second_id, REVIEWER_TWO, "incerto", criterion="CI1")
        queue = _conflicts(client, project_id, REVIEWER_TWO)
        assert sorted(item["study_id"] for item in queue) == sorted([first_id, second_id])
        assert {item["matrix_letter"] for item in queue} == {"E"}


def test_consensus_rules_reject_invalid_registrations():
    with TestClient(app) as client:
        project_id, (agreed_id, conflict_id), _ = _project(client, 2)
        for credentials in (REVIEWER_ONE, REVIEWER_TWO):
            _vote(client, project_id, agreed_id, credentials, "incluir")
        assert _resolve(client, project_id, agreed_id, REVIEWER_ONE, "consensus", "incluir").status_code == 422

        _vote(client, project_id, conflict_id, REVIEWER_ONE, "incluir")
        _vote(client, project_id, conflict_id, REVIEWER_TWO, "excluir", criterion="CE4")
        assert _resolve(client, project_id, conflict_id, REVIEWER_ONE, "consensus", "incluir",
                        justification=" ").status_code == 422
        assert _resolve(client, project_id, conflict_id, REVIEWER_ONE, "consensus", "excluir",
                        criterion="CI1").status_code == 422
        assert _resolve(client, project_id, conflict_id, REVIEWER_ONE, "consensus", "incluir").status_code == 201
        assert _resolve(client, project_id, conflict_id, REVIEWER_ONE, "consensus", "excluir",
                        criterion="CE4").status_code == 409
        assert _resolve(client, project_id, conflict_id, THIRD_REVIEWER, "consensus", "incluir").status_code == 403


def test_snowball_counts_a_phase_two_conflict_resolved_by_consensus_as_included():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client), "Snowball consenso")["id"]
        configure(client, project_id, headers, "criteria", "CE4", {"text": "Agente isolado."})
        round_one = client.post(f"/api/v1/projects/{project_id}/snowball-rounds", headers=headers).json()
        imported = client.post(
            f"/api/v1/snowball-rounds/{round_one['id']}/imports",
            headers=headers,
            data={"direction": "backward", "base": "scopus"},
            files={"file": ("refs.ris", ris({"title": "Candidate in conflict", "year": 2022}), "application/octet-stream")},
        ).json()
        study_id = imported["study_ids"][0]
        _vote(client, project_id, study_id, REVIEWER_ONE, "incluir", phase=2)
        _vote(client, project_id, study_id, REVIEWER_TWO, "excluir", phase=2, criterion="CE4")
        rounds = client.get(f"/api/v1/projects/{project_id}/snowball-rounds", headers=headers).json()
        assert rounds["rounds"][0]["counts"]["pending"] == 1

        for credentials in (REVIEWER_ONE, REVIEWER_TWO):
            assert _resolve(client, project_id, study_id, credentials, "consensus", "incluir", phase=2).status_code == 201
        rounds = client.get(f"/api/v1/projects/{project_id}/snowball-rounds", headers=headers).json()
        assert rounds["rounds"][0]["counts"]["included"] == 1
