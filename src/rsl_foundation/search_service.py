from __future__ import annotations

import hashlib
import re
import secrets
from datetime import datetime, timezone
from typing import Any

from rapidfuzz import fuzz, process
from sqlalchemy import select

from .database import (
    DuplicateCandidateRecord,
    DuplicateDecisionRecord,
    RawImportRecord,
    SearchExecutionRecord,
    SnowballRoundRecord,
    StudyRecord,
)
from .importers import PUBLICATION_TYPE_RANK, metadata_completeness, normalize_title
from .roles import Role

# Protocolo v4.0 §5.2.1: bases automáticas, campos pesquisados e limites.
SEARCH_BASES: dict[str, dict[str, Any]] = {
    "web_of_science": {"name": "Web of Science", "fields": ["Topic"], "result_limit": None},
    "scopus": {"name": "Scopus", "fields": ["TITLE-ABS-KEY"], "result_limit": None},
    "ieee": {"name": "IEEE Xplore", "fields": ["All Metadata"], "result_limit": None},
    "acm": {"name": "ACM Digital Library", "fields": ["Title", "Abstract", "Keywords"], "result_limit": None},
    "google_scholar": {"name": "Google Scholar", "fields": ["title", "abstract"], "result_limit": 300},
    "arxiv": {"name": "arXiv", "fields": ["cs.MA", "cs.AI", "cs.CL"], "result_limit": None},
}
SEARCH_WINDOW = (2016, 2026)
# Protocolo v4.0 §5.2.2: veículos da busca manual.
PROTOCOL_MANUAL_VENUES = (
    "JAAMAS", "TADS", "Expert Systems with Applications", "Information Sciences", "AAMAS", "KES-AMSTA", "ICMSCI",
)
# Protocolo v4.0 §8: snowballing backward e forward em Scopus e WoS, no máximo 2 rodadas.
SNOWBALL_BASES = {"scopus", "web_of_science"}
SNOWBALL_DIRECTIONS = {"backward", "forward"}
MAX_SNOWBALL_ROUNDS = 2
# Spec 003 regra 4: >= 0,90 sugere duplicidade; a faixa intermediária vai à revisão humana.
TITLE_DUPLICATE_THRESHOLD = 0.90
TITLE_REVIEW_THRESHOLD = 0.85

_QUERY_TOKEN = re.compile(r'"[^"]*"|\(|\)|[^\s()"]+')


def validate_boolean_query(query: str) -> None:
    """Spec 003 RF13: boolean syntax, precedence groups and the error position."""
    if not query.strip():
        raise ValueError("search query is required")
    if query.count('"') % 2:
        raise ValueError(f"unmatched quote at position {query.rfind(chr(34))}")
    open_parentheses: list[int] = []
    previous: str | None = None
    position = 0
    for match in _QUERY_TOKEN.finditer(query):
        text, position = match.group(0), match.start()
        operator = text.upper()
        if text == "(":
            open_parentheses.append(position)
            kind = "open"
        elif text == ")":
            if not open_parentheses:
                raise ValueError(f"unmatched closing parenthesis at position {position}")
            if previous == "open":
                raise ValueError(f"empty parentheses at position {position}")
            if previous in {"binary", "not"}:
                raise ValueError(f"operator without right operand at position {position}")
            open_parentheses.pop()
            kind = "close"
        elif operator in {"AND", "OR"}:
            if previous in {None, "open", "binary", "not"}:
                raise ValueError(f"operator {text} without left operand at position {position}")
            kind = "binary"
        elif operator == "NOT":
            if previous == "not":
                raise ValueError(f"repeated NOT at position {position}")
            kind = "not"
        else:
            kind = "term"
        previous = kind
    if previous in {"binary", "not"}:
        raise ValueError(f"query ends with an operator at position {position}")
    if open_parentheses:
        raise ValueError(f"unmatched opening parenthesis at position {open_parentheses[-1]}")


def _study_metadata(study: StudyRecord) -> dict[str, Any]:
    return {
        "authors": study.authors,
        "year": study.year,
        "venue": study.venue,
        "doi": study.doi,
        "abstract": study.abstract,
        "keywords": study.keywords,
    }


def canonical_preference(study: StudyRecord) -> tuple[int, int, int, str]:
    """Spec 003 RF21 (decisão do PO): periódico > anais > pré-print, depois metadados, depois o mais recente."""
    return (
        PUBLICATION_TYPE_RANK.get(study.publication_type or "", 0),
        metadata_completeness(_study_metadata(study)),
        study.year or 0,
        study.id,
    )


def _venue_key(venue: str) -> str:
    return "-".join(normalize_title(venue).split()) or "venue"


class SearchMixin:
    """Spec 003: bases, versioned strings, seminal test-set, manual search, snowballing, canonical groups."""

    # ---- RF14: bases ----------------------------------------------------

    def _base_configuration(self, database: Any, project_id: str) -> dict[str, dict[str, Any]]:
        overrides = self._latest_documents(database, project_id, "search_base")
        strings = self._latest_documents(database, project_id, "search_string")
        configuration = {}
        for base, defaults in SEARCH_BASES.items():
            override = overrides[base].data if base in overrides else {}
            adapted = strings.get(base)
            configuration[base] = {
                "base": base,
                "name": defaults["name"],
                "fields": override.get("fields", defaults["fields"]),
                "year_from": override.get("year_from", SEARCH_WINDOW[0]),
                "year_to": override.get("year_to", SEARCH_WINDOW[1]),
                "result_limit": override.get("result_limit", defaults["result_limit"]),
                "adapted_query": None if adapted is None else adapted.data["query"],
                "search_string_version": None if adapted is None else adapted.version,
                "ready": adapted is not None,
            }
        return configuration

    def get_search_bases(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            master = self._latest_documents(database, project_id, "search_string").get("master")
            return {
                "master_query": None if master is None else master.data["query"],
                "master_version": None if master is None else master.version,
                "bases": list(self._base_configuration(database, project_id).values()),
            }

    # ---- RF13: versioned search strings ---------------------------------

    def save_search_string(
        self,
        token: str,
        project_id: str,
        base_key: str,
        *,
        query: str,
        justification: str,
        deviation_id: str | None = None,
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if base_key != "master" and base_key not in SEARCH_BASES:
            raise ValueError("search string key must be master or one of the six bases")
        validate_boolean_query(query)
        if not justification.strip():
            raise ValueError("search string version requires a justification")
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.ADMIN, Role.REVISOR})
            return self._store_project_document(
                database,
                project_id=project_id,
                kind="search_string",
                key=base_key,
                data={"query": query.strip(), "justification": justification.strip()},
                user_id=payload["user_id"],
                expected_version=expected_version,
                deviation_id=deviation_id,
            )

    # ---- RF15/RF16: imports ---------------------------------------------

    def _import_records(
        self,
        database: Any,
        *,
        project_id: str,
        file_name: str,
        content: bytes,
        user_id: str,
        source: str,
        search_execution_id: str | None = None,
        snowball_round_id: str | None = None,
        direction: str | None = None,
    ) -> dict[str, Any]:
        from .importers import parse_records_with_report

        if len(content) > 50 * 1024 * 1024:
            raise ValueError("import file exceeds the 50 MiB limit")
        parsed_records, report = parse_records_with_report(content, file_name)
        raw_import_id = secrets.token_hex(16)
        content_hash = hashlib.sha256(content).hexdigest()
        origin = "search" if snowball_round_id is None else f"snowball/{direction}"
        database.add(
            RawImportRecord(
                id=raw_import_id,
                search_execution_id=search_execution_id,
                snowball_round_id=snowball_round_id,
                direction=direction,
                file_name=file_name,
                content_hash_sha256=content_hash,
                content=content,
                imported_count=len(parsed_records),
                anomalies=report["anomalies"],
                imported_by=user_id,
            )
        )
        study_ids: list[str] = []
        for parsed in parsed_records:
            study_id = f"s-{secrets.token_hex(12)}"
            study_ids.append(study_id)
            database.add(
                StudyRecord(
                    id=study_id,
                    project_id=project_id,
                    search_execution_id=search_execution_id,
                    snowball_round_id=snowball_round_id,
                    raw_import_id=raw_import_id,
                    origin=origin,
                    publication_type=parsed["publication_type"],
                    title=parsed["title"],
                    normalized_title=parsed["normalized_title"],
                    authors=parsed["authors"],
                    year=parsed["year"],
                    venue=parsed["venue"],
                    doi=parsed["doi"],
                    abstract=parsed["abstract"],
                    keywords=parsed["keywords"],
                    source=source,
                    imported_by=user_id,
                )
            )
        self._append_audit(
            database,
            entity_type="raw_import",
            entity_id=raw_import_id,
            action="raw_results_imported",
            actor_user_id=user_id,
            previous_value=None,
            new_value={
                "file_name": file_name,
                "sha256": content_hash,
                "record_count": len(parsed_records),
                "origin": origin,
                "anomaly_count": len(report["anomalies"]),
            },
        )
        return {
            "id": raw_import_id,
            "search_execution_id": search_execution_id,
            "snowball_round_id": snowball_round_id,
            "origin": origin,
            "raw_sha256": content_hash,
            "imported_count": len(study_ids),
            "study_ids": study_ids,
            "source_count": report["source_count"],
            "skipped_count": report["skipped_count"],
            "encoding": report["encoding"],
            "warnings": report["warnings"],
            "anomalies": report["anomalies"],
        }

    # ---- RF17: seminal test-set -----------------------------------------

    def _search_validation(self, database: Any, project_id: str) -> dict[str, Any]:
        seminals = {
            key: record.data
            for key, record in self._latest_documents(database, project_id, "seminal").items()
            if record.data.get("active", True)
        }
        configuration = self._base_configuration(database, project_id)
        bases = []
        alerts = []
        for base, config in configuration.items():
            studies: list[StudyRecord] = []
            status = "no_adapted_string"
            if config["search_string_version"] is not None:
                execution_ids = database.scalars(
                    select(SearchExecutionRecord.id).where(
                        SearchExecutionRecord.project_id == project_id,
                        SearchExecutionRecord.base == base,
                        SearchExecutionRecord.search_string_version == config["search_string_version"],
                    )
                ).all()
                status = "not_executed"
                if execution_ids:
                    status = "checked"
                    studies = database.scalars(
                        select(StudyRecord).where(StudyRecord.search_execution_id.in_(execution_ids))
                    ).all()
            dois = {study.doi for study in studies if study.doi}
            titles = [study.normalized_title for study in studies if study.normalized_title]
            retrieved, missing = [], []
            for seminal_id, seminal in sorted(seminals.items()):
                found = bool(seminal.get("doi")) and seminal["doi"] in dois
                if not found and titles:
                    found = process.extractOne(
                        normalize_title(seminal["title"]),
                        titles,
                        scorer=fuzz.ratio,
                        score_cutoff=TITLE_DUPLICATE_THRESHOLD * 100,
                    ) is not None
                if found:
                    retrieved.append(seminal_id)
                    continue
                year = seminal.get("year")
                outside_window = year is not None and not config["year_from"] <= year <= config["year_to"]
                missing.append({"seminal_id": seminal_id, "outside_window": outside_window})
                reason = " (fora da janela temporal; justificar via desvio)" if outside_window else ""
                if status != "checked":
                    reason = f" (base sem {'string adaptada' if status == 'no_adapted_string' else 'execução'})"
                alerts.append(f"{seminal_id} não recuperado em {base}{reason}")
            bases.append(
                {
                    "base": base,
                    "status": status,
                    "search_string_version": config["search_string_version"],
                    "retrieved": retrieved,
                    "missing": missing,
                }
            )
        return {
            "seminals": sorted(seminals),
            "bases": bases,
            "alerts": alerts,
            "ok": bool(seminals) and not alerts,
        }

    def get_search_validation(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            return self._search_validation(database, project_id)

    # ---- RF18: manual search --------------------------------------------

    def register_manual_search(
        self,
        token: str,
        project_id: str,
        *,
        venue: str,
        year_from: int | None,
        year_to: int | None,
        unswept_editions: list[str] | None = None,
        notes: str = "",
        expected_version: int | None = None,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if not venue.strip():
            raise ValueError("manual search requires the venue")
        if year_from is None or year_to is None:
            raise ValueError("manual search requires the swept period")
        if year_from > year_to:
            raise ValueError("swept period must start before it ends")
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.ADMIN, Role.REVISOR})
            return self._store_project_document(
                database,
                project_id=project_id,
                kind="manual_search",
                key=_venue_key(venue),
                data={
                    "venue": venue.strip(),
                    "year_from": year_from,
                    "year_to": year_to,
                    "unswept_editions": [edition.strip() for edition in unswept_editions or [] if edition.strip()],
                    "notes": notes.strip(),
                },
                user_id=payload["user_id"],
                expected_version=expected_version,
            )

    def list_manual_searches(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = self._latest_documents(database, project_id, "manual_search")
        venues = [{"key": key, "version": record.version, **record.data} for key, record in sorted(records.items())]
        registered = {_venue_key(item["venue"]) for item in venues}
        return {
            "venues": venues,
            "protocol_venues_missing": [venue for venue in PROTOCOL_MANUAL_VENUES if _venue_key(venue) not in registered],
            "meets_minimum": len(venues) >= len(PROTOCOL_MANUAL_VENUES),
        }

    # ---- RF19/RF28: snowballing -----------------------------------------

    def _snowball_counts(self, database: Any, project_id: str, round_id: str) -> dict[str, Any]:
        canonical_of, _ = self._duplicate_groups(database, project_id)
        studies = database.scalars(select(StudyRecord).where(StudyRecord.snowball_round_id == round_id)).all()
        counts: dict[str, dict[str, int]] = {
            direction: {"candidates": 0, "duplicates": 0, "included": 0, "excluded": 0, "pending": 0}
            for direction in sorted(SNOWBALL_DIRECTIONS)
        }
        for study in studies:
            bucket = counts[study.origin.split("/", 1)[1]]
            bucket["candidates"] += 1
            if study.id in canonical_of:
                bucket["duplicates"] += 1
                continue
            phase_one = self._triage_result(database, project_id, study.id, 1)
            phase_two = self._triage_result(database, project_id, study.id, 2)
            if phase_two == "included":
                bucket["included"] += 1
            elif "excluded" in {phase_one, phase_two}:
                bucket["excluded"] += 1
            else:
                bucket["pending"] += 1
        totals = {
            name: sum(bucket[name] for bucket in counts.values())
            for name in ("candidates", "duplicates", "included", "excluded", "pending")
        }
        return {"by_direction": counts, **totals}

    def _snowball_round(self, database: Any, round_id: str, user_id: str) -> SnowballRoundRecord:
        record = database.get(SnowballRoundRecord, round_id)
        if record is None:
            raise LookupError("snowballing round not found")
        self._require_project_membership(database, record.project_id, user_id, {Role.ADMIN, Role.REVISOR})
        return record

    def open_snowball_round(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.ADMIN, Role.REVISOR})
            rounds = database.scalars(
                select(SnowballRoundRecord)
                .where(SnowballRoundRecord.project_id == project_id)
                .order_by(SnowballRoundRecord.round_number)
            ).all()
            if any(record.status == "open" for record in rounds):
                raise ValueError("a snowballing round is already open")
            number = len(rounds) + 1
            if number > MAX_SNOWBALL_ROUNDS:
                raise ValueError(f"snowballing allows at most {MAX_SNOWBALL_ROUNDS} rounds")
            if number > 1:
                previous_counts = self._snowball_counts(database, project_id, rounds[-1].id)
                if previous_counts["included"] == 0:
                    raise ValueError(
                        f"stopping criterion: round {number - 1} included no new studies; round {number} is blocked"
                    )
            record = SnowballRoundRecord(
                id=secrets.token_hex(16),
                project_id=project_id,
                round_number=number,
                status="open",
                opened_by=payload["user_id"],
                opened_at=datetime.now(timezone.utc),
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="snowball_round",
                entity_id=record.id,
                action="snowball_round_opened",
                actor_user_id=payload["user_id"],
                previous_value=None,
                new_value={"round_number": number},
            )
            return {"id": record.id, "project_id": project_id, "round_number": number, "status": "open"}

    def import_snowball_candidates(
        self,
        token: str,
        round_id: str,
        *,
        direction: str,
        base: str,
        file_name: str,
        content: bytes,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if direction not in SNOWBALL_DIRECTIONS:
            raise ValueError("snowballing direction must be backward or forward")
        if base not in SNOWBALL_BASES:
            raise ValueError("snowballing uses Scopus or Web of Science")
        with self._session_factory.begin() as database:
            record = self._snowball_round(database, round_id, payload["user_id"])
            if record.status != "open":
                raise ValueError("snowballing round is closed")
            return self._import_records(
                database,
                project_id=record.project_id,
                file_name=file_name,
                content=content,
                user_id=payload["user_id"],
                source=base,
                snowball_round_id=record.id,
                direction=direction,
            )

    def close_snowball_round(self, token: str, round_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory.begin() as database:
            record = self._snowball_round(database, round_id, payload["user_id"])
            if record.status != "open":
                raise ValueError("snowballing round is already closed")
            summary = self._snowball_counts(database, record.project_id, record.id)
            record.status = "closed"
            record.closed_by = payload["user_id"]
            record.closed_at = datetime.now(timezone.utc)
            record.closing_summary = summary
            self._append_audit(
                database,
                entity_type="snowball_round",
                entity_id=record.id,
                action="snowball_round_closed",
                actor_user_id=payload["user_id"],
                previous_value={"status": "open"},
                new_value={"status": "closed", "summary": summary},
            )
            return {"id": record.id, "round_number": record.round_number, "status": "closed", "summary": summary}

    def list_snowball_rounds(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            rounds = database.scalars(
                select(SnowballRoundRecord)
                .where(SnowballRoundRecord.project_id == project_id)
                .order_by(SnowballRoundRecord.round_number)
            ).all()
            output = [
                {
                    "id": record.id,
                    "round_number": record.round_number,
                    "status": record.status,
                    "opened_at": record.opened_at.isoformat(),
                    "closed_at": None if record.closed_at is None else record.closed_at.isoformat(),
                    "closing_summary": record.closing_summary,
                    "counts": self._snowball_counts(database, project_id, record.id),
                }
                for record in rounds
            ]
        if any(item["status"] == "open" for item in output):
            next_round = {"allowed": False, "reason": "a round is open"}
        elif len(output) >= MAX_SNOWBALL_ROUNDS:
            next_round = {"allowed": False, "reason": f"maximum of {MAX_SNOWBALL_ROUNDS} rounds reached"}
        elif output and output[-1]["counts"]["included"] == 0:
            next_round = {"allowed": False, "reason": "stopping criterion: previous round included no new studies"}
        else:
            next_round = {"allowed": True, "reason": None}
        return {"rounds": output, "next_round": next_round, "minimum_rounds_met": bool(output)}

    # ---- RF20/RF21: canonical groups ------------------------------------

    @staticmethod
    def _latest_duplicate_decisions(database: Any, project_id: str) -> dict[str, DuplicateDecisionRecord]:
        decisions = database.scalars(
            select(DuplicateDecisionRecord)
            .join(DuplicateCandidateRecord, DuplicateCandidateRecord.id == DuplicateDecisionRecord.candidate_id)
            .where(DuplicateCandidateRecord.project_id == project_id)
            .order_by(DuplicateDecisionRecord.created_at, DuplicateDecisionRecord.id)
        ).all()
        return {decision.candidate_id: decision for decision in decisions}

    def _duplicate_groups(self, database: Any, project_id: str) -> tuple[dict[str, str], list[dict[str, Any]]]:
        candidates = database.scalars(
            select(DuplicateCandidateRecord).where(DuplicateCandidateRecord.project_id == project_id)
        ).all()
        latest = self._latest_duplicate_decisions(database, project_id)
        parent: dict[str, str] = {}

        def find(study_id: str) -> str:
            parent.setdefault(study_id, study_id)
            while parent[study_id] != study_id:
                parent[study_id] = parent[parent[study_id]]
                study_id = parent[study_id]
            return study_id

        duplicate_decisions = []
        for candidate in candidates:
            decision = latest.get(candidate.id)
            if decision is not None and decision.decision == "duplicate":
                parent[find(candidate.study_id_a)] = find(candidate.study_id_b)
                duplicate_decisions.append(decision)

        members: dict[str, list[str]] = {}
        for study_id in list(parent):
            members.setdefault(find(study_id), []).append(study_id)
        # The latest human choice of canonical prevails; otherwise the RF21 preference picks it.
        manual_canonical: dict[str, str] = {}
        for decision in sorted(duplicate_decisions, key=lambda item: (item.created_at, item.id)):
            if decision.method == "manual":
                manual_canonical[find(decision.canonical_study_id)] = decision.canonical_study_id

        grouped_ids = [study_id for group in members.values() if len(group) > 1 for study_id in group]
        studies = {
            study.id: study
            for study in database.scalars(select(StudyRecord).where(StudyRecord.id.in_(grouped_ids))).all()
        } if grouped_ids else {}

        canonical_of: dict[str, str] = {}
        groups = []
        for root, group in members.items():
            if len(group) < 2:
                continue
            canonical = manual_canonical.get(root) or max(
                (studies[study_id] for study_id in group), key=canonical_preference
            ).id
            groups.append({"canonical_study_id": canonical, "study_ids": sorted(group)})
            for study_id in group:
                if study_id != canonical:
                    canonical_of[study_id] = canonical
        return canonical_of, groups

    def get_deduplication_summary(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            canonical_of, groups = self._duplicate_groups(database, project_id)
            studies = database.scalars(select(StudyRecord).where(StudyRecord.project_id == project_id)).all()
            executions = database.scalars(
                select(SearchExecutionRecord)
                .where(SearchExecutionRecord.project_id == project_id)
                .order_by(SearchExecutionRecord.executed_at)
            ).all()
            candidates = database.scalars(
                select(DuplicateCandidateRecord.id).where(DuplicateCandidateRecord.project_id == project_id)
            ).all()
            latest = self._latest_duplicate_decisions(database, project_id)
        by_execution: dict[str, list[StudyRecord]] = {}
        for study in studies:
            by_execution.setdefault(study.search_execution_id or f"snowball:{study.snowball_round_id}", []).append(study)
        return {
            "total_records": len(studies),
            "unique_studies": len(studies) - len(canonical_of),
            "duplicates": len(canonical_of),
            "pending_review": sum(1 for candidate_id in candidates if candidate_id not in latest),
            "groups": groups,
            "executions": [
                {
                    "id": execution.id,
                    "base": execution.base,
                    "executed_at": execution.executed_at.isoformat(),
                    "search_string_version": execution.search_string_version,
                    "reported_result_count": execution.reported_result_count,
                    "imported": len(by_execution.get(execution.id, [])),
                    "duplicates": sum(1 for study in by_execution.get(execution.id, []) if study.id in canonical_of),
                }
                for execution in executions
            ],
        }
