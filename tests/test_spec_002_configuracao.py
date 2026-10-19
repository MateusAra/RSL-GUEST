"""Critérios de aceite da spec 002 — Configuração do estudo (CT-CFG-01..10)."""

import csv
import io
import json
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import update
from sqlalchemy.exc import DBAPIError

from backend.api import app
from rsl_foundation.database import ProjectDocumentRecord, build_engine
from tests.helpers import (
    SUBSTANTIVE_FIELDS,
    VERDICTS,
    auth,
    configure,
    configure_complete_protocol,
    create_project,
    deviation,
    login,
    research_question,
)


def test_ca_01_project_requires_two_reviewers_and_third_reviewer():
    with TestClient(app) as client:
        headers = auth(login(client))
        response = client.post(
            "/api/v1/projects",
            headers=headers,
            json={
                "title": "Equipe incompleta",
                "objective": "CA-01",
                "study_type": "systematic_literature_review",
                "members": [
                    {"email": "reviewer@rsl.local", "role": "revisor"},
                    {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
                ],
            },
        )
        assert response.status_code == 422
        assert "two reviewers" in response.json()["detail"]


def test_ca_02_frozen_protocol_version_stays_intact_and_diff_is_shown():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        first = configure(client, project_id, headers, "protocol", "protocolo",
                          {"text": "Versão 3.0\nCritérios originais", "description": "v3.0", "frozen": True})
        second = configure(client, project_id, headers, "protocol", "protocolo",
                           {"text": "Versão 3.1\nCritérios revisados", "description": "v3.1", "frozen": True})
        assert (first.json()["version"], second.json()["version"]) == (1, 2)

        diff = client.get(
            f"/api/v1/projects/{project_id}/configuration/protocol/protocolo/diff?from_version=1&to_version=2",
            headers=headers,
        )
        assert diff.status_code == 200
        assert "-Critérios originais" in diff.json()["diff"]
        assert "+Critérios revisados" in diff.json()["diff"]

        engine = build_engine(os.environ["RSL_DATABASE_URL"])
        with engine.begin() as connection, pytest.raises(DBAPIError):
            connection.execute(
                update(ProjectDocumentRecord)
                .where(ProjectDocumentRecord.id == first.json()["id"])
                .values(data={"text": "editado"})
            )
        engine.dispose()
        versions = client.get(f"/api/v1/projects/{project_id}/configuration?kind=protocol", headers=headers).json()
        assert versions[0]["data"]["text"] == "Versão 3.0\nCritérios originais"


def test_ca_03_deviation_requires_justification_and_section_and_is_exportable():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        url = f"/api/v1/projects/{project_id}/deviations"
        base = {"stage": "triagem", "description": "Mudança de critério", "justification": "Ambíguo",
                "affected_section": "§6.1"}
        assert client.post(url, headers=headers, json={**base, "justification": " "}).status_code == 422
        assert client.post(url, headers=headers, json={**base, "affected_section": ""}).status_code == 422
        assert client.post(url, headers=headers, json=base).status_code == 201

        exported_csv = client.get(f"{url}/export?format=csv", headers=headers)
        assert exported_csv.status_code == 200
        assert exported_csv.headers["content-type"].startswith("text/csv")
        rows = list(csv.DictReader(io.StringIO(exported_csv.text)))
        assert rows[0]["affected_section"] == "§6.1"
        exported_json = client.get(f"{url}/export?format=json", headers=headers)
        assert json.loads(exported_json.text)[0]["justification"] == "Ambíguo"


def test_ca_04_unlinked_glossary_term_is_pending_and_blocks_gate_zero():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure_complete_protocol(client, project_id, headers)
        for index in range(9):
            assert configure(client, project_id, headers, "glossary", f"T{index}",
                             {"definition": f"Termo {index}", "criteria_links": ["CI1"]}).status_code == 201
        unlinked = configure(client, project_id, headers, "glossary", "XAI", {"definition": "IA explicável."})
        assert unlinked.status_code == 201

        integrity = client.get(f"/api/v1/projects/{project_id}/configuration-integrity", headers=headers).json()
        assert integrity["glossary_terms"] == 11
        assert integrity["glossary_pending"] == ["XAI"]
        gate = client.post(f"/api/v1/projects/{project_id}/gates/0/confirm", headers=headers, json={})
        assert gate.status_code == 422
        assert "glossary" in gate.json()["detail"]


def test_ca_05_research_question_requires_easterbrook_classification_and_justification():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        without_class = configure(client, project_id, headers, "research_question", "RQ1",
                                  research_question(classification=""))
        without_justification = configure(client, project_id, headers, "research_question", "RQ1",
                                          research_question(classification_justification=""))
        assert without_class.status_code == 422
        assert without_justification.status_code == 422
        assert configure(client, project_id, headers, "research_question", "RQ1",
                         research_question()).status_code == 201


def test_ca_06_picoc_requires_all_five_elements():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        response = configure(client, project_id, headers, "picoc", "main", {"elements": {
            "population": "MAS", "intervention": "XAI", "comparison": "", "outcome": "Confiança", "context": "LLM",
        }})
        assert response.status_code == 422


def test_ca_07_verdicts_and_weighting_are_readable_and_required_for_gate_zero():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        assert configure(client, project_id, headers, "verdict_rules", "default",
                         {"verdicts": VERDICTS[:3]}).status_code == 422

        configure_complete_protocol(client, project_id, headers)
        analysis = client.get(f"/api/v1/projects/{project_id}/analysis-configuration", headers=headers).json()
        assert sorted(analysis["hypotheses"]) == ["H1", "H2"]
        assert analysis["verdicts"] == VERDICTS
        assert analysis["quality_weighting"] == {
            "high": {"min_score": 7.0, "weight": 1.0},
            "moderate": {"min_score": 4.0, "weight": 0.5},
        }

        other_id = create_project(client, login(client))["id"]
        configure_complete_protocol(client, other_id, headers)
        # A project without verdicts cannot cross Portão 0.
        bare_id = create_project(client, login(client))["id"]
        gate = client.post(f"/api/v1/projects/{bare_id}/gates/0/confirm", headers=headers, json={})
        assert gate.status_code == 422
        assert "verdicts" in gate.json()["detail"]
        assert client.post(f"/api/v1/projects/{other_id}/gates/0/confirm", headers=headers, json={}).status_code == 201


def test_ca_08_research_question_revision_keeps_history_with_previous_and_new_text():
    with TestClient(app) as client:
        token = login(client)
        headers = auth(token)
        project_id = create_project(client, token)["id"]
        configure(client, project_id, headers, "research_question", "RQ2", research_question(text="Texto antigo"))
        revised = configure(client, project_id, headers, "research_question", "RQ2", research_question(text="Texto novo"))
        assert revised.status_code == 201
        assert "-Texto antigo" in revised.json()["diff"]
        assert "+Texto novo" in revised.json()["diff"]

        events = client.get("/api/v1/audit-events", headers=headers).json()
        event = next(item for item in events if item["entity_id"] == revised.json()["id"])
        assert event["previous_value"]["data"]["text"] == "Texto antigo"
        assert event["new_value"]["data"]["text"] == "Texto novo"
        assert event["actor_user_id"] == "u-admin"
        assert event["performed_at"]


def test_ca_09_integrity_reports_zero_orphans_and_fails_on_unlinked_field():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure_complete_protocol(client, project_id, headers)
        integrity = client.get(f"/api/v1/projects/{project_id}/configuration-integrity", headers=headers).json()
        assert integrity["ok"] is True
        assert integrity["rqs_without_fields"] == []
        assert integrity["fields_without_rq"] == []

        configure(client, project_id, headers, "research_question", "RQ1",
                  research_question(field_links=SUBSTANTIVE_FIELDS[1:]))
        integrity = client.get(f"/api/v1/projects/{project_id}/configuration-integrity", headers=headers).json()
        assert integrity["ok"] is False
        assert integrity["fields_without_rq"] == [SUBSTANTIVE_FIELDS[0]]


def test_ca_10_schedule_shows_progress_and_pending_dependencies():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure(client, project_id, headers, "phase", "F0",
                  {"name": "Registro no OSF", "duration_weeks": 2, "order": 0, "progress_percent": 100})
        configure(client, project_id, headers, "phase", "F1",
                  {"name": "Buscas", "duration_weeks": 3, "order": 1, "dependencies": ["F0"], "progress_percent": 50})
        configure(client, project_id, headers, "phase", "F2",
                  {"name": "Pilotagem", "duration_weeks": 1, "order": 2, "dependencies": ["F1"]})

        schedule = client.get(f"/api/v1/projects/{project_id}/schedule", headers=headers).json()
        phases = {phase["key"]: phase for phase in schedule["phases"]}
        assert phases["F0"]["status"] == "concluida"
        assert phases["F1"]["status"] == "em_andamento"
        assert phases["F2"]["blocked_by"] == ["F1"]
        assert phases["F2"]["status"] == "dependencia_pendente"
        assert schedule["overall_progress_percent"] == pytest.approx((2 * 100 + 3 * 50) / 6, abs=0.01)


def test_rule_2_changes_after_gate_zero_require_registered_deviation():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure_complete_protocol(client, project_id, headers)
        assert client.post(f"/api/v1/projects/{project_id}/gates/0/confirm", headers=headers, json={}).status_code == 201

        blocked = configure(client, project_id, headers, "criteria", "CI1", {"text": "Aborda MAS e agentes LLM."})
        assert blocked.status_code == 422
        deviation_id = deviation(client, project_id, headers, "§6.1")
        accepted = configure(client, project_id, headers, "criteria", "CI1",
                             {"text": "Aborda MAS e agentes LLM."}, deviation_id=deviation_id)
        assert accepted.status_code == 201
        assert accepted.json()["data"]["deviation_id"] == deviation_id


def test_rule_5_research_question_is_deactivated_with_justification_not_deleted():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure(client, project_id, headers, "research_question", "RQ9", research_question())
        assert configure(client, project_id, headers, "research_question", "RQ9",
                         research_question(active=False)).status_code == 422
        deactivated = configure(client, project_id, headers, "research_question", "RQ9",
                                research_question(active=False, deactivation_justification="Fundida na RQ1."))
        assert deactivated.status_code == 201
        versions = client.get(f"/api/v1/projects/{project_id}/configuration?kind=research_question",
                              headers=headers).json()
        assert [version["version"] for version in versions] == [1, 2]


def test_edge_concurrent_glossary_edit_is_detected():
    with TestClient(app) as client:
        headers = auth(login(client))
        project_id = create_project(client, login(client))["id"]
        configure(client, project_id, headers, "glossary", "RAI", {"definition": "IA responsável."})
        first = configure(client, project_id, headers, "glossary", "RAI",
                          {"definition": "IA responsável (v2)."}, expected_version=1)
        second = configure(client, project_id, headers, "glossary", "RAI",
                           {"definition": "IA responsável (outra)."}, expected_version=1)
        assert first.status_code == 201
        assert second.status_code == 409
