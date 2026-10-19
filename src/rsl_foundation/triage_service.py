from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select

from .database import ProjectDocumentRecord, StudyRecord, TriageResolutionRecord, TriageVoteRecord
from .roles import Role
from .triage import (
    ARBITRATION_DECISIONS,
    CONFLICT_LETTERS,
    CONSENSUS_DECISIONS,
    classify_triage_pair,
    resolve_conflict,
)


class TriageMixin:
    """Spec 004 RF26: consensus of D/E conflicts and third-reviewer arbitration."""

    def _triage_state(self, database: Any, project_id: str, study_id: str, phase: int) -> dict[str, Any] | None:
        reviewer_ids = self._assigned_reviewers(database, project_id)
        votes = {
            vote.reviewer_user_id: vote
            for vote in database.scalars(
                select(TriageVoteRecord).where(
                    TriageVoteRecord.project_id == project_id,
                    TriageVoteRecord.study_id == study_id,
                    TriageVoteRecord.phase == phase,
                    TriageVoteRecord.reviewer_user_id.in_(reviewer_ids),
                    TriageVoteRecord.confirmed.is_(True),
                )
            ).all()
        }
        if len(reviewer_ids) != 2 or len(votes) != 2:
            return None
        first, second = (votes[user_id] for user_id in reviewer_ids)
        letter, matrix_result = classify_triage_pair(first.vote, second.vote)
        state: dict[str, Any] = {
            "study_id": study_id,
            "phase": phase,
            "matrix_letter": letter,
            "matrix_result": matrix_result,
            "votes": [
                {"reviewer_user_id": vote.reviewer_user_id, "vote": vote.vote, "criterion_id": vote.criterion_id}
                for vote in (first, second)
            ],
        }
        if letter not in CONFLICT_LETTERS:
            state.update({"status": matrix_result, "final_result": matrix_result})
            return state
        resolutions = database.scalars(
            select(TriageResolutionRecord)
            .where(
                TriageResolutionRecord.project_id == project_id,
                TriageResolutionRecord.study_id == study_id,
                TriageResolutionRecord.phase == phase,
            )
            .order_by(TriageResolutionRecord.created_at, TriageResolutionRecord.id)
        ).all()
        consensus = [item for item in resolutions if item.stage == "consensus" and item.user_id in reviewer_ids]
        arbitration = next((item for item in resolutions if item.stage == "arbitration"), None)
        status, final_result = resolve_conflict(
            [item.decision for item in consensus], None if arbitration is None else arbitration.decision
        )

        def describe(item: TriageResolutionRecord) -> dict[str, Any]:
            return {
                "user_id": item.user_id,
                "decision": item.decision,
                "criterion_id": item.criterion_id,
                "justification": item.justification,
                "created_at": item.created_at.isoformat(),
            }

        state.update(
            {
                "status": status,
                "final_result": final_result or "consensus_required",
                "consensus": [describe(item) for item in consensus],
                "arbitration": None if arbitration is None else describe(arbitration),
            }
        )
        return state

    def _triage_result(self, database: Any, project_id: str, study_id: str, phase: int) -> str | None:
        state = self._triage_state(database, project_id, study_id, phase)
        return None if state is None else state["final_result"]

    @staticmethod
    def _validate_resolution(
        database: Any, project_id: str, decision: str, criterion_id: str | None, justification: str
    ) -> None:
        if not justification.strip():
            raise ValueError("triage resolution requires a justification")
        if decision == "excluir":
            # Spec 004 regras 2 e 4: exclusion must cite a configured CE.
            exists = criterion_id is not None and criterion_id.startswith("CE") and database.scalar(
                select(ProjectDocumentRecord.id).where(
                    ProjectDocumentRecord.project_id == project_id,
                    ProjectDocumentRecord.kind == "criteria",
                    ProjectDocumentRecord.document_key == criterion_id,
                )
            ) is not None
            if not exists:
                raise ValueError("exclusion requires a CE criterion configured for this project")

    def _record_resolution(
        self,
        database: Any,
        *,
        project_id: str,
        study_id: str,
        phase: int,
        stage: str,
        user_id: str,
        decision: str,
        criterion_id: str | None,
        justification: str,
    ) -> TriageResolutionRecord:
        record = TriageResolutionRecord(
            id=secrets.token_hex(16),
            project_id=project_id,
            study_id=study_id,
            phase=phase,
            stage=stage,
            user_id=user_id,
            decision=decision,
            criterion_id=criterion_id if decision == "excluir" else None,
            justification=justification.strip(),
            created_at=datetime.now(timezone.utc),
        )
        database.add(record)
        self._append_audit(
            database,
            entity_type="triage_resolution",
            entity_id=record.id,
            action=f"triage_{stage}_recorded",
            actor_user_id=user_id,
            previous_value=None,
            new_value={
                "study_id": study_id,
                "phase": phase,
                "decision": decision,
                "criterion_id": record.criterion_id,
                "justification": record.justification,
            },
        )
        return record

    def _conflict_state(self, database: Any, project_id: str, study_id: str, phase: int) -> dict[str, Any]:
        if phase not in {1, 2}:
            raise ValueError("triage phase must be 1 or 2")
        study = database.get(StudyRecord, study_id)
        if study is None or study.project_id != project_id:
            raise LookupError("study not found in project")
        state = self._triage_state(database, project_id, study_id, phase)
        if state is None or state["matrix_letter"] not in CONFLICT_LETTERS:
            raise ValueError("study is not a D/E conflict with both votes confirmed")
        return state

    def submit_triage_consensus(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        phase: int,
        decision: str,
        criterion_id: str | None = None,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if decision not in CONSENSUS_DECISIONS:
            raise ValueError("consensus decision must be incluir, excluir or sem_consenso")
        with self._session_factory.begin() as database:
            membership = self._require_project_membership(database, project_id, payload["user_id"], {Role.REVISOR})
            if membership.user_id not in self._assigned_reviewers(database, project_id):
                raise PermissionError("403: reviewer is not assigned to this triage pair")
            state = self._conflict_state(database, project_id, study_id, phase)
            if state["status"] != "awaiting_consensus":
                raise ValueError(f"409: conflict is already {state['status']}")
            if any(item["user_id"] == membership.user_id for item in state["consensus"]):
                raise ValueError("409: consensus position already recorded by this reviewer")
            self._validate_resolution(database, project_id, decision, criterion_id, justification)
            self._record_resolution(
                database,
                project_id=project_id,
                study_id=study_id,
                phase=phase,
                stage="consensus",
                user_id=membership.user_id,
                decision=decision,
                criterion_id=criterion_id,
                justification=justification,
            )
            database.flush()
            return self._triage_state(database, project_id, study_id, phase)

    def submit_triage_arbitration(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        phase: int,
        decision: str,
        criterion_id: str | None = None,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if decision not in ARBITRATION_DECISIONS:
            raise ValueError("arbitration decision must be incluir or excluir")
        with self._session_factory.begin() as database:
            membership = self._require_project_membership(
                database, project_id, payload["user_id"], {Role.TERCEIRO_REVISOR}
            )
            state = self._conflict_state(database, project_id, study_id, phase)
            # Spec 004 regra 6: the third reviewer acts only after R1 and R2 tried consensus.
            if state["status"] != "escalated":
                raise ValueError(f"409: arbitration requires an escalated conflict (status {state['status']})")
            self._validate_resolution(database, project_id, decision, criterion_id, justification)
            self._record_resolution(
                database,
                project_id=project_id,
                study_id=study_id,
                phase=phase,
                stage="arbitration",
                user_id=membership.user_id,
                decision=decision,
                criterion_id=criterion_id,
                justification=justification,
            )
            database.flush()
            return self._triage_state(database, project_id, study_id, phase)

    def list_triage_conflicts(self, token: str, project_id: str, *, phase: int) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if phase not in {1, 2}:
            raise ValueError("triage phase must be 1 or 2")
        with self._session_factory() as database:
            membership = self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            study_ids = database.scalars(
                select(TriageVoteRecord.study_id)
                .where(
                    TriageVoteRecord.project_id == project_id,
                    TriageVoteRecord.phase == phase,
                    TriageVoteRecord.confirmed.is_(True),
                )
                .group_by(TriageVoteRecord.study_id)
                .having(func.count() >= 2)
                .order_by(TriageVoteRecord.study_id)
            ).all()
            titles = {
                study.id: study.title
                for study in database.scalars(select(StudyRecord).where(StudyRecord.id.in_(study_ids))).all()
            } if study_ids else {}
            conflicts = []
            for study_id in study_ids:
                state = self._triage_state(database, project_id, study_id, phase)
                if state is None or state["matrix_letter"] not in CONFLICT_LETTERS:
                    continue
                # Spec 004 regra 6: R3 only sees conflicts that went through a consensus attempt.
                if Role(membership.role) == Role.TERCEIRO_REVISOR and state["status"] not in {
                    "escalated", "resolved_by_arbitration",
                }:
                    continue
                conflicts.append({**state, "title": titles.get(study_id)})
            return conflicts
