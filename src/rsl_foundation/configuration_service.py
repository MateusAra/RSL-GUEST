from __future__ import annotations

import csv
import io
import json
import re
import secrets
from difflib import unified_diff
from typing import Any

from sqlalchemy import select

from .database import (
    ExtractionRecord,
    ProjectDocumentRecord,
    ProjectGateRecord,
    ProjectMembershipRecord,
    ProtocolDeviationRecord,
)
from .extraction import EXTRACTION_FIELD_IDS, is_substantive_field
from .roles import Role

FIXED_VERDICTS = ("suporta", "parcialmente suporta", "refuta", "inconclusivo")
# Spec 002 §11 (resolvido pelo PO): score >= 7,0 pesa 1,0; 4,0-6,9 pesa 0,5 e é reportado à parte.
DEFAULT_QUALITY_WEIGHTING = {
    "high": {"min_score": 7.0, "weight": 1.0},
    "moderate": {"min_score": 4.0, "weight": 0.5},
}
# Spec 002 regra 2 (e spec 003 regra 2): mudanças depois do Portão 0 exigem desvio registrado.
GATE_GUARDED_KINDS = {"research_question", "criteria", "search_string"}
TEXT_DIFF_FIELDS = {"protocol": "text", "research_question": "text", "search_string": "query"}
GATES = {0: "Portão 0 — protocolo registrado", 1: "Portão 1 — string validada contra os seminais"}


def field_sort_key(field_id: str) -> tuple[str, int]:
    match = re.fullmatch(r"Q-([A-Z]+)(\d+)", field_id)
    return (match.group(1), int(match.group(2))) if match else (field_id, 0)


def _document_lines(kind: str, data: dict[str, Any]) -> list[str]:
    if kind in TEXT_DIFF_FIELDS:
        return str(data.get(TEXT_DIFF_FIELDS[kind], "")).splitlines()
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False).splitlines()


class ConfigurationMixin:
    """Spec 002: versioned configuration, integrity, schedule and gates."""

    # ---- shared helpers -------------------------------------------------

    @staticmethod
    def _latest_documents(database: Any, project_id: str, kind: str) -> dict[str, ProjectDocumentRecord]:
        records = database.scalars(
            select(ProjectDocumentRecord)
            .where(ProjectDocumentRecord.project_id == project_id, ProjectDocumentRecord.kind == kind)
            .order_by(ProjectDocumentRecord.version)
        ).all()
        return {record.document_key: record for record in records}

    @staticmethod
    def _gate_confirmed(database: Any, project_id: str, gate: int) -> bool:
        return database.scalar(
            select(ProjectGateRecord.id).where(
                ProjectGateRecord.project_id == project_id, ProjectGateRecord.gate == gate
            )
        ) is not None

    @staticmethod
    def _require_deviation(database: Any, project_id: str, deviation_id: str | None) -> ProtocolDeviationRecord:
        deviation = database.get(ProtocolDeviationRecord, deviation_id) if deviation_id else None
        if deviation is None or deviation.project_id != project_id:
            raise ValueError("deviation_id must reference a deviation registered in this project")
        return deviation

    @staticmethod
    def _assigned_reviewers(database: Any, project_id: str) -> list[str]:
        return list(
            database.scalars(
                select(ProjectMembershipRecord.user_id)
                .where(
                    ProjectMembershipRecord.project_id == project_id,
                    ProjectMembershipRecord.role == Role.REVISOR.value,
                )
                .order_by(ProjectMembershipRecord.user_id)
                .limit(2)
            ).all()
        )

    def _store_project_document(
        self,
        database: Any,
        *,
        project_id: str,
        kind: str,
        key: str,
        data: dict[str, Any],
        user_id: str,
        expected_version: int | None = None,
        deviation_id: str | None = None,
    ) -> dict[str, Any]:
        previous = database.scalar(
            select(ProjectDocumentRecord)
            .where(
                ProjectDocumentRecord.project_id == project_id,
                ProjectDocumentRecord.kind == kind,
                ProjectDocumentRecord.document_key == key,
            )
            .order_by(ProjectDocumentRecord.version.desc())
            .limit(1)
        )
        current_version = 0 if previous is None else previous.version
        if expected_version is not None and expected_version != current_version:
            raise ValueError("409: configuration version conflict; reload and merge before saving")
        if kind in GATE_GUARDED_KINDS and self._gate_confirmed(database, project_id, 0):
            self._require_deviation(database, project_id, deviation_id)
            data = {**data, "deviation_id": deviation_id}
        elif deviation_id:
            self._require_deviation(database, project_id, deviation_id)
            data = {**data, "deviation_id": deviation_id}

        version = current_version + 1
        diff_text = ""
        if previous is not None:
            diff_text = "\n".join(
                unified_diff(
                    _document_lines(kind, previous.data),
                    _document_lines(kind, data),
                    fromfile=f"{key}@{previous.version}",
                    tofile=f"{key}@{version}",
                    lineterm="",
                )
            )
        record = ProjectDocumentRecord(
            id=secrets.token_hex(16),
            project_id=project_id,
            kind=kind,
            document_key=key,
            version=version,
            data=data,
            created_by=user_id,
        )
        database.add(record)
        self._append_audit(
            database,
            entity_type=kind,
            entity_id=record.id,
            action="configuration_version_created",
            actor_user_id=user_id,
            previous_value=None if previous is None else {
                "key": key, "version": previous.version, "data": previous.data,
            },
            new_value={"key": key, "version": version, "data": data},
        )
        return {
            "id": record.id,
            "project_id": project_id,
            "kind": kind,
            "key": key,
            "version": version,
            "data": data,
            "created_by": user_id,
            "diff": diff_text,
        }

    # ---- RF02/RF11: diff between any two versions -----------------------

    def get_configuration_diff(
        self,
        token: str,
        project_id: str,
        *,
        kind: str,
        key: str,
        from_version: int,
        to_version: int,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = {
                record.version: record
                for record in database.scalars(
                    select(ProjectDocumentRecord).where(
                        ProjectDocumentRecord.project_id == project_id,
                        ProjectDocumentRecord.kind == kind,
                        ProjectDocumentRecord.document_key == key,
                        ProjectDocumentRecord.version.in_([from_version, to_version]),
                    )
                ).all()
            }
            if from_version not in records or to_version not in records:
                raise LookupError("configuration version not found")
            return {
                "kind": kind,
                "key": key,
                "from_version": from_version,
                "to_version": to_version,
                "diff": "\n".join(
                    unified_diff(
                        _document_lines(kind, records[from_version].data),
                        _document_lines(kind, records[to_version].data),
                        fromfile=f"{key}@{from_version}",
                        tofile=f"{key}@{to_version}",
                        lineterm="",
                    )
                ),
            }

    # ---- RF12/RNF04: integrity ------------------------------------------

    def _configuration_integrity(self, database: Any, project_id: str) -> dict[str, Any]:
        research_questions = {
            key: record.data
            for key, record in self._latest_documents(database, project_id, "research_question").items()
            if record.data.get("active", True)
        }
        criteria = {
            key for key, record in self._latest_documents(database, project_id, "criteria").items()
            if record.data.get("active", True)
        }
        glossary = self._latest_documents(database, project_id, "glossary")
        hypotheses = self._latest_documents(database, project_id, "hypothesis")
        linked_fields = {
            field_id for data in research_questions.values() for field_id in data.get("field_links", [])
        }
        report = {
            "research_questions": len(research_questions),
            "rqs_without_fields": sorted(key for key, data in research_questions.items() if not data.get("field_links")),
            "rqs_without_analyses": sorted(key for key, data in research_questions.items() if not data.get("analysis_links")),
            "fields_without_rq": sorted(
                (field_id for field_id in EXTRACTION_FIELD_IDS
                 if is_substantive_field(field_id) and field_id not in linked_fields),
                key=field_sort_key,
            ),
            "glossary_terms": len(glossary),
            "glossary_pending": sorted(
                key for key, record in glossary.items()
                if not (set(record.data.get("criteria_links", [])) & criteria)
                and not (set(record.data.get("field_links", [])) & EXTRACTION_FIELD_IDS)
            ),
            "picoc_complete": bool(self._latest_documents(database, project_id, "picoc")),
            "hypotheses_missing": [key for key in ("H1", "H2") if key not in hypotheses],
            "verdicts_configured": bool(self._latest_documents(database, project_id, "verdict_rules")),
            "protocol_versions": len(self._latest_documents(database, project_id, "protocol")),
        }
        issues = []
        if not report["protocol_versions"]:
            issues.append("protocol has no version")
        if not research_questions:
            issues.append("no active research question")
        if report["rqs_without_fields"]:
            issues.append(f"{len(report['rqs_without_fields'])} research question(s) without extraction fields")
        if report["rqs_without_analyses"]:
            issues.append(f"{len(report['rqs_without_analyses'])} research question(s) without analyses")
        if report["fields_without_rq"]:
            issues.append(f"{len(report['fields_without_rq'])} extraction field(s) without research question")
        if report["glossary_pending"]:
            issues.append(f"{len(report['glossary_pending'])} glossary term(s) without CI/CE or field link")
        if not report["picoc_complete"]:
            issues.append("PICOC is not configured")
        if report["hypotheses_missing"]:
            issues.append(f"missing hypotheses: {', '.join(report['hypotheses_missing'])}")
        if not report["verdicts_configured"]:
            issues.append("the four hypothesis verdicts are not configured")
        report["issues"] = issues
        report["ok"] = not issues
        return report

    def get_configuration_integrity(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            return self._configuration_integrity(database, project_id)

    def get_analysis_configuration(self, token: str, project_id: str) -> dict[str, Any]:
        """CA-07: configuration read by the analysis module (spec 008)."""
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            hypotheses = self._latest_documents(database, project_id, "hypothesis")
            verdicts = self._latest_documents(database, project_id, "verdict_rules")
            verdict_rules = verdicts.get("default") or next(iter(verdicts.values()), None)
            return {
                "hypotheses": {key: record.data for key, record in sorted(hypotheses.items())},
                "verdicts": None if verdict_rules is None else verdict_rules.data["verdicts"],
                "quality_weighting": None if verdict_rules is None else verdict_rules.data["quality_weighting"],
                "operational_criteria": None if verdict_rules is None else verdict_rules.data.get("operational_criteria", {}),
            }

    # ---- RF04: schedule (visual only, spec 002 [ESCLARECER 3]) ----------

    def get_schedule(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            phases = {key: record.data for key, record in self._latest_documents(database, project_id, "phase").items()}
        progress = {key: float(data.get("progress_percent", 0)) for key, data in phases.items()}
        output = []
        for key, data in sorted(phases.items(), key=lambda item: (item[1].get("order", 0), item[0])):
            dependencies = list(data.get("dependencies", []))
            blocked_by = [dependency for dependency in dependencies if progress.get(dependency, 0) < 100]
            current = progress[key]
            status = (
                "concluida" if current >= 100
                else "dependencia_pendente" if blocked_by
                else "em_andamento" if current > 0
                else "nao_iniciada"
            )
            output.append(
                {
                    "key": key,
                    "name": data["name"],
                    "duration_weeks": data["duration_weeks"],
                    "dependencies": dependencies,
                    "unknown_dependencies": [dependency for dependency in dependencies if dependency not in phases],
                    "progress_percent": current,
                    "blocked_by": blocked_by,
                    "status": status,
                }
            )
        total_weeks = sum(float(item["duration_weeks"]) for item in output)
        overall = (
            round(sum(float(item["duration_weeks"]) * item["progress_percent"] for item in output) / total_weeks, 2)
            if total_weeks else 0.0
        )
        return {"phases": output, "total_weeks": total_weeks, "overall_progress_percent": overall}

    # ---- RF03: exportable deviation log ---------------------------------

    def export_protocol_deviations(self, token: str, project_id: str, export_format: str) -> tuple[str, str]:
        deviations = self.list_protocol_deviations(token, project_id)
        if export_format == "json":
            return json.dumps(deviations, ensure_ascii=False, indent=2), "application/json"
        if export_format != "csv":
            raise ValueError("format must be csv or json")
        buffer = io.StringIO()
        columns = ["id", "created_at", "stage", "description", "justification", "affected_section", "author_user_id"]
        writer = csv.DictWriter(buffer, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(deviations)
        return buffer.getvalue(), "text/csv"

    # ---- gates ----------------------------------------------------------

    def list_gates(self, token: str, project_id: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = {
                record.gate: record
                for record in database.scalars(
                    select(ProjectGateRecord).where(ProjectGateRecord.project_id == project_id)
                ).all()
            }
        return [
            {
                "gate": gate,
                "name": name,
                "confirmed": gate in records,
                "confirmed_by": records[gate].confirmed_by if gate in records else None,
                "confirmed_at": records[gate].confirmed_at.isoformat() if gate in records else None,
                "details": records[gate].details if gate in records else None,
            }
            for gate, name in GATES.items()
        ]

    def confirm_gate(
        self,
        token: str,
        project_id: str,
        gate: int,
        *,
        deviation_id: str | None = None,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if gate not in GATES:
            raise LookupError("unknown gate")
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.ADMIN})
            if self._gate_confirmed(database, project_id, gate):
                raise ValueError("409: gate already confirmed")
            if gate == 0:
                integrity = self._configuration_integrity(database, project_id)
                if not integrity["ok"]:
                    raise ValueError("Portão 0 blocked: " + "; ".join(integrity["issues"]))
                details: dict[str, Any] = {"integrity": integrity}
            else:
                if not self._gate_confirmed(database, project_id, 0):
                    raise ValueError("Portão 1 requires Portão 0")
                validation = self._search_validation(database, project_id)
                if not validation["seminals"]:
                    raise ValueError("Portão 1 blocked: the seminal test-set is empty")
                waivable = all(
                    missing["outside_window"]
                    for base in validation["bases"]
                    for missing in base["missing"]
                )
                if validation["alerts"] and not (waivable and deviation_id):
                    raise ValueError("Portão 1 blocked: " + "; ".join(validation["alerts"]))
                if deviation_id:
                    self._require_deviation(database, project_id, deviation_id)
                details = {"search_validation": validation, "deviation_id": deviation_id}
            record = ProjectGateRecord(
                id=secrets.token_hex(16),
                project_id=project_id,
                gate=gate,
                confirmed_by=payload["user_id"],
                details=details,
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="project_gate",
                entity_id=record.id,
                action="gate_confirmed",
                actor_user_id=payload["user_id"],
                previous_value=None,
                new_value={"project_id": project_id, "gate": gate, "deviation_id": deviation_id},
            )
        return {"gate": gate, "name": GATES[gate], "confirmed": True, "details": details}

    @staticmethod
    def _linked_extractions(database: Any, project_id: str, field_ids: list[str]) -> list[str]:
        if not field_ids:
            return []
        return sorted(
            set(
                database.scalars(
                    select(ExtractionRecord.field_id).where(
                        ExtractionRecord.project_id == project_id,
                        ExtractionRecord.field_id.in_(field_ids),
                    )
                ).all()
            ),
            key=field_sort_key,
        )
