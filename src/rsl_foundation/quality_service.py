from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select

from .database import QualityArbitrationRecord, QualityAssessmentRecord, StudyRecord
from .quality import QA_V4_INSTRUMENT, calculate_weighted_kappa, resolve_quality_consensus
from .roles import Role

KAPPA_WARNING_THRESHOLD = 0.6


def _score_map(items: list[dict[str, Any]] | None) -> dict[str, float | None]:
    return {item["criterion_id"]: item["score"] for item in items or []}


class QualityMixin:
    """Spec 005: configurable instrument, reopening, arbitration and project-level report."""

    def _project_instrument(self, database: Any, project_id: str) -> tuple[dict[str, Any], int | None]:
        record = self._latest_documents(database, project_id, "qa_instrument").get("default")
        if record is None:
            return QA_V4_INSTRUMENT, None
        return record.data, record.version

    def get_quality_instrument(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            instrument, version = self._project_instrument(database, project_id)
        return {"version": version, "source": "protocol_v4" if version is None else "project", **instrument}

    def _quality_pair(
        self, database: Any, project_id: str, study_id: str
    ) -> tuple[list[str], dict[str, QualityAssessmentRecord]]:
        reviewer_ids = self._assigned_reviewers(database, project_id)
        assessments = database.scalars(
            select(QualityAssessmentRecord).where(
                QualityAssessmentRecord.project_id == project_id,
                QualityAssessmentRecord.study_id == study_id,
                QualityAssessmentRecord.reviewer_user_id.in_(reviewer_ids),
            )
        ).all()
        return reviewer_ids, {assessment.reviewer_user_id: assessment for assessment in assessments}

    def _quality_consensus(
        self,
        database: Any,
        project_id: str,
        study_id: str,
        reviewer_ids: list[str],
        assessments: dict[str, QualityAssessmentRecord],
    ) -> dict[str, Any] | None:
        if len(reviewer_ids) != 2 or not all(
            user_id in assessments and assessments[user_id].confirmed for user_id in reviewer_ids
        ):
            return None
        first, second = (assessments[user_id] for user_id in reviewer_ids)
        # Arbitrations made before the latest confirmation refer to superseded ratings.
        latest_confirmation = max(first.updated_at, second.updated_at)
        if latest_confirmation.tzinfo is None:
            latest_confirmation = latest_confirmation.replace(tzinfo=timezone.utc)
        arbitrations: dict[str, float | None] = {}
        for record in database.scalars(
            select(QualityArbitrationRecord)
            .where(
                QualityArbitrationRecord.project_id == project_id,
                QualityArbitrationRecord.study_id == study_id,
            )
            .order_by(QualityArbitrationRecord.created_at, QualityArbitrationRecord.id)
        ).all():
            created_at = record.created_at if record.created_at.tzinfo else record.created_at.replace(tzinfo=timezone.utc)
            if created_at >= latest_confirmation:
                arbitrations[record.criterion_id] = record.score
        instrument, _ = self._project_instrument(database, project_id)
        return resolve_quality_consensus(
            _score_map(first.scores), _score_map(second.scores), arbitrations, instrument
        )

    # ---- CA-09: reopening a confirmed assessment ------------------------

    def reopen_quality_assessment(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if not justification.strip():
            raise ValueError("reopening a QA assessment requires a justification")
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.REVISOR})
            record = database.scalar(
                select(QualityAssessmentRecord)
                .where(
                    QualityAssessmentRecord.project_id == project_id,
                    QualityAssessmentRecord.study_id == study_id,
                    QualityAssessmentRecord.reviewer_user_id == payload["user_id"],
                )
                .with_for_update()
            )
            if record is None:
                raise LookupError("QA assessment not found")
            if not record.confirmed:
                raise ValueError("only confirmed QA assessments can be reopened")
            record.confirmed = False
            record.reopen_justification = justification.strip()
            record.version += 1
            record.updated_at = datetime.now(timezone.utc)
            self._append_audit(
                database,
                entity_type="quality_assessment",
                entity_id=record.id,
                action="quality_assessment_reopened",
                actor_user_id=payload["user_id"],
                previous_value={"confirmed": True, "score": record.score, "scores": record.scores},
                new_value={"confirmed": False, "justification": record.reopen_justification},
            )
            return {"id": record.id, "study_id": study_id, "confirmed": False, "version": record.version}

    # ---- RF32: arbitration by the third reviewer ------------------------

    def submit_quality_arbitration(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        criterion_id: str,
        score: float | None,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if not justification.strip():
            raise ValueError("arbitration requires a justification")
        with self._session_factory.begin() as database:
            self._require_project_membership(database, project_id, payload["user_id"], {Role.TERCEIRO_REVISOR})
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            reviewer_ids, assessments = self._quality_pair(database, project_id, study_id)
            consensus = self._quality_consensus(database, project_id, study_id, reviewer_ids, assessments)
            if consensus is None:
                raise ValueError("arbitration requires both QA assessments confirmed")
            if criterion_id not in consensus["disputed_criteria"]:
                raise ValueError(f"{criterion_id} is not in dispute for this study")
            instrument, _ = self._project_instrument(database, project_id)
            criterion = next(item for item in instrument["criteria"] if item["id"] == criterion_id)
            if score is None and not criterion.get("na_eligible"):
                raise ValueError(f"{criterion_id} is not eligible for N/A")
            if score is not None and score not in {0, 0.5, 1}:
                raise ValueError(f"{criterion_id} score must be 0, 0.5, 1 or N/A")
            record = QualityArbitrationRecord(
                id=secrets.token_hex(16),
                project_id=project_id,
                study_id=study_id,
                criterion_id=criterion_id,
                score=score,
                justification=justification.strip(),
                arbiter_user_id=payload["user_id"],
                created_at=datetime.now(timezone.utc),
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="quality_arbitration",
                entity_id=record.id,
                action="quality_arbitration_recorded",
                actor_user_id=payload["user_id"],
                previous_value={
                    "scores": [_score_map(assessments[user_id].scores).get(criterion_id) for user_id in reviewer_ids]
                },
                new_value={"study_id": study_id, "criterion_id": criterion_id, "score": score,
                           "justification": record.justification},
            )
            return {"id": record.id, "study_id": study_id, "criterion_id": criterion_id, "score": score}

    # ---- RF31/RF32: project report --------------------------------------

    def get_quality_summary(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            study_ids = sorted(
                set(
                    database.scalars(
                        select(QualityAssessmentRecord.study_id).where(QualityAssessmentRecord.project_id == project_id)
                    ).all()
                )
            )
            titles = {
                study.id: study.title
                for study in database.scalars(select(StudyRecord).where(StudyRecord.id.in_(study_ids))).all()
            } if study_ids else {}
            studies, excluded, queue = [], [], []
            initial_first: list[float] = []
            initial_second: list[float] = []
            kappa_studies = 0
            for study_id in study_ids:
                reviewer_ids, assessments = self._quality_pair(database, project_id, study_id)
                initial = [assessments.get(user_id) for user_id in reviewer_ids]
                if len(initial) == 2 and all(item is not None and item.initial_scores for item in initial):
                    # Rule 11: the initial weighted kappa uses the first confirmed ratings only.
                    first_map, second_map = (_score_map(item.initial_scores) for item in initial)
                    shared = [key for key in first_map if first_map[key] is not None and second_map.get(key) is not None]
                    initial_first.extend(first_map[key] for key in shared)
                    initial_second.extend(second_map[key] for key in shared)
                    kappa_studies += 1
                consensus = self._quality_consensus(database, project_id, study_id, reviewer_ids, assessments)
                entry: dict[str, Any] = {"study_id": study_id, "title": titles.get(study_id)}
                if consensus is None:
                    entry["status"] = "in_progress"
                else:
                    entry["status"] = consensus["status"]
                    entry["disputed_criteria"] = consensus["disputed_criteria"]
                    if consensus["pending_arbitration"]:
                        queue.append({"study_id": study_id, "criteria": consensus["pending_arbitration"]})
                    if "score" in consensus:
                        entry.update(
                            {
                                "final_score": consensus["score"],
                                "category_scores": consensus["category_scores"],
                                "classification": consensus["classification"],
                                "outcome": consensus["outcome"],
                                "not_applicable_count": consensus["not_applicable_count"],
                            }
                        )
                        if consensus["status"] == "final" and consensus["outcome"] == "excluido_qualidade":
                            excluded.append(
                                {"study_id": study_id, "title": titles.get(study_id), "reason": "qualidade",
                                 "final_score": consensus["score"]}
                            )
                studies.append(entry)
        kappa = calculate_weighted_kappa(initial_first, initial_second) if initial_first else None
        final = [entry for entry in studies if entry["status"] == "final"]
        return {
            "studies": studies,
            "excluded": excluded,
            "arbitration_queue": queue,
            "counts": {
                "assessed": len(studies),
                "final": len(final),
                "aprovado": sum(entry["outcome"] == "aprovado" for entry in final),
                "ressalva": sum(entry["outcome"] == "ressalva" for entry in final),
                "excluido_qualidade": len(excluded),
                "awaiting_arbitration": len(queue),
                "in_progress": sum(entry["status"] == "in_progress" for entry in studies),
            },
            "initial_weighted_kappa": {
                "value": kappa,
                "studies": kappa_studies,
                "rated_items": len(initial_first),
                "warning": kappa is not None and kappa < KAPPA_WARNING_THRESHOLD,
            },
        }
