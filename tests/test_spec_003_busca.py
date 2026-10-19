"""Critérios de aceite da spec 003 — Busca, importação, snowballing e deduplicação (CT-BUS-01..10)."""

import os
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.exc import DBAPIError

from backend.api import app
from rsl_foundation.database import (
    DuplicateDecisionRecord,
    RawImportRecord,
    SearchExecutionRecord,
    StudyRecord,
    build_engine,
)
from tests.helpers import (
    REVIEWER_ONE,
    REVIEWER_TWO,
    auth,
    configure,
    configure_complete_protocol,
    create_execution,
    create_project,
    deviation,
    import_file,
    login,
    ris,
    save_search_string,
)

BASES = ["web_of_science", "scopus", "ieee", "acm", "google_scholar", "arxiv"]
SEMINALS = {
    "SX15": {"title": "Explainable agents and robots: a systematic review", "doi": "10.1000/sx15", "year": 2019},
    "SX21": {"title": "Trustworthy multi-agent systems with explanations", "doi": "10.1000/sx21", "year": 2021},
    "SX22": {"title": "Responsible AI for agentic ecosystems", "doi": "10.1000/sx22", "year": 2022},
    "SX23": {"title": "Explainability in LLM-based multi-agent collaboration", "doi": "10.1000/sx23", "year": 2023},
}


def _setup(client: TestClient) -> tuple[str, dict]:
    headers = auth(login(client))
    project_id = create_project(client, login(client), "Busca")["id"]
    return project_id, headers


def test_ca_01_invalid_string_is_rejected_with_position_and_valid_string_is_versioned():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        unbalanced = save_search_string(client, project_id, headers, "master", '("XAI" AND (MAS OR agent)')
        assert unbalanced.status_code == 422
        assert "position 0" in unbalanced.json()["detail"]
        dangling = save_search_string(client, project_id, headers, "master", "XAI AND (MAS OR)")
        assert dangling.status_code == 422
        assert "position 15" in dangling.json()["detail"]

        first = save_search_string(client, project_id, headers, "master", '"explainable AI" AND ("multi-agent")')
        second = save_search_string(client, project_id, headers, "master", '"explainable AI" AND ("multi-agent" OR agentic)')
        assert (first.json()["version"], second.json()["version"]) == (1, 2)
        assert second.json()["data"]["justification"]
        assert "+\"explainable AI\" AND (\"multi-agent\" OR agentic)" in second.json()["diff"]


def test_ca_02_six_bases_with_window_and_scholar_limit_and_no_execution_without_adapted_string():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        bases = client.get(f"/api/v1/projects/{project_id}/search-bases", headers=headers).json()["bases"]
        assert [base["base"] for base in bases] == BASES
        assert all((base["year_from"], base["year_to"]) == (2016, 2026) for base in bases)
        assert next(base for base in bases if base["base"] == "google_scholar")["result_limit"] == 300

        blocked = client.post(
            f"/api/v1/projects/{project_id}/search-executions",
            headers=headers,
            json={"base": "ieee", "reported_result_count": 10},
        )
        assert blocked.status_code == 422
        assert "no adapted search string" in blocked.json()["detail"]


def test_ca_03_raw_result_is_hashed_and_immutable_and_new_execution_creates_new_record():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        first = create_execution(client, project_id, headers, "scopus", reported_result_count=1)
        imported = import_file(client, first["id"], headers, "scopus.ris", ris({"title": "A", "year": 2024}))
        assert len(imported.json()["raw_sha256"]) == 64

        engine = build_engine(os.environ["RSL_DATABASE_URL"])
        immutable = [
            update(RawImportRecord).where(RawImportRecord.id == imported.json()["id"]).values(file_name="x.ris"),
            update(SearchExecutionRecord).where(SearchExecutionRecord.id == first["id"]).values(reported_result_count=9),
            update(StudyRecord).where(StudyRecord.id == imported.json()["study_ids"][0]).values(title="editado"),
            update(DuplicateDecisionRecord).values(justification="editado"),
        ]
        for statement in immutable:
            with engine.begin() as connection, pytest.raises(DBAPIError):
                connection.execute(statement)
        engine.dispose()

        second = create_execution(client, project_id, headers, "scopus", reported_result_count=2)
        assert second["id"] != first["id"]
        assert second["search_string_version"] == 2


def test_ca_04_ris_with_1000_records_maps_95_percent_and_lists_anomalies():
    records = [
        {"title": f"Explainable multi-agent study {index}", "year": 2016 + index % 10, "doi": f"10.1000/{index}",
         "authors": [f"Author {index}"]}
        for index in range(980)
    ]
    records += [{"title": f"Untitled authors {index}", "authors": [], "year": 2020} for index in range(15)]
    records += [{"title": "", "year": 2021} for _ in range(5)]
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        execution = create_execution(client, project_id, headers, "scopus", reported_result_count=1000)
        started = time.perf_counter()
        response = import_file(client, execution["id"], headers, "big.ris", ris(*records))
        elapsed = time.perf_counter() - started

        assert response.status_code == 201, response.text
        body = response.json()
        assert elapsed <= 60
        assert body["source_count"] == 1000
        assert body["imported_count"] == 995
        assert body["skipped_count"] == 5
        complete = body["source_count"] - len(body["anomalies"])
        assert complete / body["source_count"] >= 0.95
        assert {issue for anomaly in body["anomalies"] for issue in anomaly["issues"]} == {
            "missing_title", "missing_authors",
        }


def _seminal_project(client: TestClient, missing: dict[str, str] | None = None) -> tuple[str, dict]:
    project_id, headers = _setup(client)
    configure_complete_protocol(client, project_id, headers)
    for seminal_id, data in SEMINALS.items():
        assert configure(client, project_id, headers, "seminal", seminal_id, data).status_code == 201
    for base in BASES:
        execution = create_execution(client, project_id, headers, base, reported_result_count=4)
        retrieved = [data for seminal_id, data in SEMINALS.items() if (missing or {}).get(base) != seminal_id]
        assert import_file(client, execution["id"], headers, f"{base}.ris", ris(*retrieved)).status_code == 201
    assert client.post(f"/api/v1/projects/{project_id}/gates/0/confirm", headers=headers, json={}).status_code == 201
    return project_id, headers


def test_ca_05_missing_seminal_alerts_study_and_base_and_blocks_gate_one():
    with TestClient(app) as client:
        project_id, headers = _seminal_project(client, missing={"ieee": "SX21"})
        validation = client.get(f"/api/v1/projects/{project_id}/search-validation", headers=headers).json()
        assert validation["ok"] is False
        assert validation["alerts"] == ["SX21 não recuperado em ieee"]

        gate = client.post(f"/api/v1/projects/{project_id}/gates/1/confirm", headers=headers, json={})
        assert gate.status_code == 422
        assert "SX21 não recuperado em ieee" in gate.json()["detail"]

        complete_id, complete_headers = _seminal_project(client)
        assert client.get(f"/api/v1/projects/{complete_id}/search-validation",
                          headers=complete_headers).json()["ok"] is True
        assert client.post(f"/api/v1/projects/{complete_id}/gates/1/confirm",
                           headers=complete_headers, json={}).status_code == 201


def test_edge_seminal_outside_window_can_be_waived_with_deviation_and_string_change_needs_deviation():
    with TestClient(app) as client:
        project_id, headers = _seminal_project(client, missing={"arxiv": "SX15"})
        configure(client, project_id, headers, "search_base", "arxiv", {"year_from": 2020, "year_to": 2026})
        validation = client.get(f"/api/v1/projects/{project_id}/search-validation", headers=headers).json()
        assert validation["bases"][-1]["missing"] == [{"seminal_id": "SX15", "outside_window": True}]
        assert client.post(f"/api/v1/projects/{project_id}/gates/1/confirm",
                           headers=headers, json={}).status_code == 422
        deviation_id = deviation(client, project_id, headers, "§5.1")
        assert client.post(f"/api/v1/projects/{project_id}/gates/1/confirm",
                           headers=headers, json={"deviation_id": deviation_id}).status_code == 201

        # Spec 002 regra 2 / spec 003 regra 2: string changes after the gates need a deviation.
        assert save_search_string(client, project_id, headers, "scopus", "XAI AND agents").status_code == 422
        assert save_search_string(client, project_id, headers, "scopus", "XAI AND agents",
                                  deviation_id=deviation_id).status_code == 201


def _vote(client: TestClient, project_id: str, study_id: str, credentials: tuple[str, str], vote: str, phase: int):
    response = client.post(
        f"/api/v1/projects/{project_id}/studies/{study_id}/triage-votes",
        headers=auth(login(client, *credentials)),
        json={"phase": phase, "vote": vote, "confirm": True, "expected_version": 0},
    )
    assert response.status_code == 201, response.text


def _snowball_import(client: TestClient, round_id: str, headers: dict, direction: str, title: str):
    response = client.post(
        f"/api/v1/snowball-rounds/{round_id}/imports",
        headers=headers,
        data={"direction": direction, "base": "scopus"},
        files={"file": ("refs.ris", ris({"title": title, "year": 2022}), "application/octet-stream")},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_ca_06_round_two_follows_stopping_criterion_and_round_three_is_blocked():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        rounds_url = f"/api/v1/projects/{project_id}/snowball-rounds"
        first = client.post(rounds_url, headers=headers).json()
        _snowball_import(client, first["id"], headers, "backward", "Backward candidate without inclusion")
        assert client.post(f"/api/v1/snowball-rounds/{first['id']}/close", headers=headers).status_code == 200
        blocked = client.post(rounds_url, headers=headers)
        assert blocked.status_code == 422
        assert "stopping criterion" in blocked.json()["detail"]

        other_id, _ = _setup(client)
        other_url = f"/api/v1/projects/{other_id}/snowball-rounds"
        round_one = client.post(other_url, headers=headers).json()
        candidate = _snowball_import(client, round_one["id"], headers, "forward", "Forward candidate included")
        for credentials in (REVIEWER_ONE, REVIEWER_TWO):
            _vote(client, other_id, candidate["study_ids"][0], credentials, "incluir", 2)
        closed = client.post(f"/api/v1/snowball-rounds/{round_one['id']}/close", headers=headers).json()
        assert closed["summary"]["by_direction"]["forward"]["included"] == 1
        round_two = client.post(other_url, headers=headers)
        assert round_two.status_code == 201
        assert client.post(f"/api/v1/snowball-rounds/{round_two.json()['id']}/close", headers=headers).status_code == 200
        third = client.post(other_url, headers=headers)
        assert third.status_code == 422
        assert "at most 2 rounds" in third.json()["detail"]


def test_ca_07_obvious_doi_duplicates_are_marked_automatically_and_intermediate_go_to_manual_queue():
    # Random hex titles keep unrelated records far apart; each copy shares only the DOI.
    originals = [{"title": uuid.uuid4().hex, "doi": f"10.2000/{index}", "year": 2020} for index in range(100)]
    copies = [{"title": uuid.uuid4().hex, "doi": f"10.2000/{index}", "year": 2020} for index in range(100)]
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        scopus = create_execution(client, project_id, headers, "scopus", reported_result_count=102)
        wos = create_execution(client, project_id, headers, "web_of_science", reported_result_count=101)
        # Similarity 0.8986: below the 0.90 suggestion threshold, inside the manual-review band.
        import_file(client, scopus["id"], headers, "a.ris", ris(*originals, {"title": "Trust models for agent societies"}))
        import_file(client, wos["id"], headers, "b.ris", ris(*copies, {"title": "Trust model for agent society reviews"}))

        candidates = client.post(f"/api/v1/projects/{project_id}/deduplication/run", headers=headers).json()["candidates"]
        automatic = [item for item in candidates if item["method"] == "automatic"]
        manual = [item for item in candidates if item["match_type"] == "manual_review"]
        assert len(automatic) >= 90
        assert len(manual) == 1
        assert manual[0]["decision"] is None
        summary = client.get(f"/api/v1/projects/{project_id}/deduplication/summary", headers=headers).json()
        assert summary["duplicates"] == 100
        assert summary["pending_review"] == 1
        assert sum(item["duplicates"] for item in summary["executions"]) == 100


def test_ca_08_journal_version_is_suggested_canonical_and_study_counts_once():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        execution = create_execution(client, project_id, headers, "scopus", reported_result_count=2)
        import_file(client, execution["id"], headers, "versions.ris", ris(
            {"type": "CONF", "title": "Explainable coordination in multi-agent systems", "venue": "AAMAS", "year": 2021},
            {"type": "JOUR", "title": "Explainable coordination in multi-agent systems (extended)",
             "venue": "JAAMAS", "year": 2023, "abstract": "Extended version."},
        ))
        candidates = client.post(f"/api/v1/projects/{project_id}/deduplication/run", headers=headers).json()["candidates"]
        assert len(candidates) == 1
        studies = {study["id"]: study for study in client.get(f"/api/v1/projects/{project_id}/studies", headers=headers).json()}
        journal_id = next(study_id for study_id, study in studies.items() if study["publication_type"] == "journal")
        assert candidates[0]["suggested_canonical_study_id"] == journal_id

        decision = client.post(
            f"/api/v1/duplicate-candidates/{candidates[0]['id']}/decision",
            headers=auth(login(client, *REVIEWER_ONE)),
            json={"decision": "duplicate", "canonical_study_id": journal_id,
                  "justification": "Versão estendida em periódico."},
        )
        assert decision.status_code == 200
        studies = client.get(f"/api/v1/projects/{project_id}/studies", headers=headers).json()
        assert len(studies) == 2
        assert [study["duplicate_of"] for study in studies if study["id"] != journal_id] == [journal_id]
        summary = client.get(f"/api/v1/projects/{project_id}/deduplication/summary", headers=headers).json()
        assert summary["unique_studies"] == 1
        assert summary["groups"] == [{"canonical_study_id": journal_id, "study_ids": sorted(studies_id["id"] for studies_id in studies)}]


def test_ca_09_snowball_candidate_enters_triage_with_its_origin():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        round_one = client.post(f"/api/v1/projects/{project_id}/snowball-rounds", headers=headers).json()
        imported = _snowball_import(client, round_one["id"], headers, "backward", "Cited seminal work on XAI")
        study = client.get(f"/api/v1/projects/{project_id}/studies", headers=headers).json()[0]
        assert study["origin"] == "snowball/backward"
        assert study["snowball_round_id"] == round_one["id"]
        _vote(client, project_id, imported["study_ids"][0], REVIEWER_ONE, "incluir", 1)


def test_ca_10_manual_search_requires_swept_period():
    with TestClient(app) as client:
        project_id, headers = _setup(client)
        url = f"/api/v1/projects/{project_id}/manual-searches"
        missing_period = client.post(url, headers=headers, json={"venue": "JAAMAS", "year_from": 2016})
        assert missing_period.status_code == 422
        saved = client.post(url, headers=headers, json={
            "venue": "JAAMAS", "year_from": 2016, "year_to": 2026, "unswept_editions": ["2018 v32"],
        })
        assert saved.status_code == 201
        listing = client.get(url, headers=headers).json()
        assert listing["venues"][0]["unswept_editions"] == ["2018 v32"]
        assert "JAAMAS" not in listing["protocol_venues_missing"]
        assert listing["meets_minimum"] is False
