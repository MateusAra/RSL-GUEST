"""Thematic synthesis (Cruzes & Dybå 2011): codebook, coded segments, dual coding, themes, reliability."""

from __future__ import annotations

import csv
import io
import json
import math
import random
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select

from ..agreement import AGREEMENT_THRESHOLD, coding_agreement
from ..db import utcnow
from ..deps import CurrentUser, DbSession, MemberReview, OwnerReview, log_activity
from ..models import (
    CHECKLIST_ITEMS,
    CODE_KINDS,
    CODE_STATUSES,
    Article,
    Code,
    CodeEvent,
    CodingSample,
    CodingSettings,
    DataExtractionField,
    Review,
    Segment,
    SegmentCode,
    SegmentResolution,
    SynthesisChecklistItem,
    Theme,
    ThemeCode,
    User,
)
from ..notify import notify
from .analysis import final_articles

router = APIRouter(tags=["síntese"])


# ---- helpers ----------------------------------------------------------------------

def _settings(db: DbSession, review: Review) -> CodingSettings:
    settings = db.get(CodingSettings, review.id)
    if settings is None:
        settings = CodingSettings(review_id=review.id)
        db.add(settings)
        db.flush()
    return settings


def _ensure_open(db: DbSession, review: Review) -> CodingSettings:
    settings = _settings(db, review)
    if settings.closed_at is not None:
        raise HTTPException(status_code=409, detail="A fase de codificação está fechada. Reabra para alterar.")
    return settings


def _event(db: DbSession, review: Review, user: User, action: str, code: Code | None,
           previous: dict | None = None, new: dict | None = None, justification: str = "") -> None:
    db.add(CodeEvent(review_id=review.id, code_id=None if code is None else code.id, action=action,
                     previous=previous, new=new, justification=justification, user_id=user.id))


def _code(db: DbSession, review: Review, code_id: int) -> Code:
    code = db.get(Code, code_id)
    if code is None or code.review_id != review.id:
        raise HTTPException(status_code=404, detail="Código não encontrado nesta revisão.")
    return code


def _snapshot(code: Code) -> dict[str, Any]:
    return {"name": code.name, "definition": code.definition, "limits": code.limits, "status": code.status}


def _usage(db: DbSession, code_ids: list[int]) -> dict[int, int]:
    if not code_ids:
        return {}
    return dict(db.execute(
        select(SegmentCode.code_id, func.count(func.distinct(SegmentCode.segment_id)))
        .where(SegmentCode.code_id.in_(code_ids)).group_by(SegmentCode.code_id)
    ).all())


def code_out(code: Code, usage: int) -> dict[str, Any]:
    return {
        "id": code.id, "name": code.name, "definition": code.definition, "limits": code.limits,
        "kind": code.kind, "kind_label": CODE_KINDS[code.kind], "status": code.status,
        "status_label": CODE_STATUSES[code.status], "origin_field_id": code.origin_field_id,
        "origin_lookup_id": code.origin_lookup_id, "merged_into_id": code.merged_into_id,
        "created_by_id": code.created_by_id, "segments": usage,
    }


def _final_ids(db: DbSession, review: Review) -> set[int]:
    return {article.id for article in final_articles(db, review)}


def _sample(db: DbSession, review: Review, settings: CodingSettings, article_id: int) -> CodingSample | None:
    if not settings.dual_enabled:
        return None
    return db.get(CodingSample, (review.id, article_id))


def _slot(settings: CodingSettings, user: User) -> Literal["a", "b"] | None:
    if user.id == settings.coder_a_id:
        return "a"
    if user.id == settings.coder_b_id:
        return "b"
    return None


def _both_done(sample: CodingSample | None) -> bool:
    return sample is not None and sample.coder_a_done and sample.coder_b_done


def _active_code_ids(db: DbSession, review: Review, code_ids: list[int]) -> list[int]:
    unique = sorted(set(code_ids))
    if not unique:
        return []
    found = set(db.scalars(select(Code.id).where(Code.review_id == review.id, Code.status == "active", Code.id.in_(unique))))
    if found != set(unique):
        raise HTTPException(status_code=422, detail="Só é possível aplicar códigos ativos desta revisão.")
    return unique


# ---- codebook --------------------------------------------------------------------

class CodeIn(BaseModel):
    name: str = Field(max_length=200)
    definition: str = ""
    limits: str = ""


class CodeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    definition: str | None = None
    limits: str | None = None
    justification: str = ""


class MergeIn(BaseModel):
    code_ids: list[int]
    name: str = Field(max_length=200)
    definition: str
    limits: str
    justification: str


class RemoveIn(BaseModel):
    migrate_to_id: int | None = None
    justification: str = ""


@router.get("/reviews/{review_id}/codes")
def list_codes(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    codes = list(db.scalars(select(Code).where(Code.review_id == review.id).order_by(func.lower(Code.name))))
    usage = _usage(db, [code.id for code in codes])
    return [code_out(code, usage.get(code.id, 0)) for code in codes]


@router.post("/reviews/{review_id}/codes", status_code=201)
def create_code(payload: CodeIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    _ensure_open(db, review)
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=422, detail="Informe o nome do código.")
    code = Code(review_id=review.id, name=name, definition=payload.definition.strip(), limits=payload.limits.strip(),
                kind="emergent", status="draft", created_by_id=user.id)
    db.add(code)
    db.flush()
    _event(db, review, user, "created", code, None, _snapshot(code))
    db.commit()
    return code_out(code, 0)


@router.post("/reviews/{review_id}/codes/import-start-list")
def import_start_list(review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    """Deductive codes from the values of select fields of the extraction form (re-import never duplicates)."""
    _ensure_open(db, review)
    existing = set(db.scalars(select(Code.origin_lookup_id).where(Code.review_id == review.id,
                                                                  Code.origin_lookup_id.is_not(None))))
    created = 0
    fields = db.scalars(select(DataExtractionField).where(
        DataExtractionField.review_id == review.id, DataExtractionField.field_type.in_(["O", "M"]))
        .order_by(DataExtractionField.order))
    for field in fields:
        for lookup in field.lookups:
            if lookup.id in existing:
                continue
            code = Code(review_id=review.id, name=f"{field.description}: {lookup.value}"[:200], kind="deductive",
                        status="draft", origin_field_id=field.id, origin_lookup_id=lookup.id, created_by_id=user.id)
            db.add(code)
            db.flush()
            _event(db, review, user, "imported", code, None, _snapshot(code))
            created += 1
    db.commit()
    return {"created": created}


@router.patch("/reviews/{review_id}/codes/{code_id}")
def update_code(code_id: int, payload: CodeUpdate, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    _ensure_open(db, review)
    code = _code(db, review, code_id)
    if code.status in {"merged", "removed"}:
        raise HTTPException(status_code=422, detail="Códigos fundidos ou removidos não podem ser editados.")
    if code.status == "active" and not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Alterar um código ativo exige justificativa.")
    previous = _snapshot(code)
    if payload.name is not None:
        if not payload.name.strip():
            raise HTTPException(status_code=422, detail="O nome não pode ficar vazio.")
        code.name = payload.name.strip()
    if payload.definition is not None:
        code.definition = payload.definition.strip()
    if payload.limits is not None:
        code.limits = payload.limits.strip()
    if code.status == "active" and (not code.definition or not code.limits):
        raise HTTPException(status_code=422, detail="Código ativo precisa de definição e limites.")
    action = "renamed" if previous["name"] != code.name else "redefined"
    _event(db, review, user, action, code, previous, _snapshot(code), payload.justification.strip())
    db.commit()
    return code_out(code, _usage(db, [code.id]).get(code.id, 0))


@router.post("/reviews/{review_id}/codes/{code_id}/activate")
def activate_code(code_id: int, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    _ensure_open(db, review)
    code = _code(db, review, code_id)
    if code.status != "draft":
        raise HTTPException(status_code=422, detail="Só códigos em rascunho podem ser ativados.")
    if not code.definition or not code.limits:
        raise HTTPException(status_code=422, detail="Defina o significado e os limites do código antes de ativá-lo.")
    previous = _snapshot(code)
    code.status = "active"
    _event(db, review, user, "activated", code, previous, _snapshot(code))
    db.commit()
    return code_out(code, 0)


@router.post("/reviews/{review_id}/codes/merge", status_code=201)
def merge_codes(payload: MergeIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    _ensure_open(db, review)
    sources = [_code(db, review, code_id) for code_id in dict.fromkeys(payload.code_ids)]
    if len(sources) < 2 or any(code.status != "active" for code in sources):
        raise HTTPException(status_code=422, detail="Escolha pelo menos dois códigos ativos para fundir.")
    if not (payload.name.strip() and payload.definition.strip() and payload.limits.strip() and payload.justification.strip()):
        raise HTTPException(status_code=422, detail="A fusão exige nome, definição, limites e justificativa.")
    merged = Code(review_id=review.id, name=payload.name.strip(), definition=payload.definition.strip(),
                  limits=payload.limits.strip(), kind="emergent", status="active", created_by_id=user.id)
    db.add(merged)
    db.flush()
    applications = db.scalars(select(SegmentCode).where(SegmentCode.code_id.in_([code.id for code in sources]))).all()
    seen: set[tuple[int, int | None, bool]] = set()
    for application in applications:
        key = (application.segment_id, application.coder_id, application.is_final)
        if key in seen:
            db.delete(application)
        else:
            application.code_id = merged.id
            seen.add(key)
    for code in sources:
        previous = _snapshot(code)
        code.status, code.merged_into_id = "merged", merged.id
        _event(db, review, user, "merged", code, previous, {**_snapshot(code), "merged_into": merged.name},
               payload.justification.strip())
    _event(db, review, user, "created_by_merge", merged, {"absorbed": [code.name for code in sources]},
           _snapshot(merged), payload.justification.strip())
    db.commit()
    return code_out(merged, _usage(db, [merged.id]).get(merged.id, 0))


@router.post("/reviews/{review_id}/codes/{code_id}/remove")
def remove_code(code_id: int, payload: RemoveIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    _ensure_open(db, review)
    code = _code(db, review, code_id)
    if code.status in {"merged", "removed"}:
        raise HTTPException(status_code=422, detail="Este código já não está em uso.")
    used = _usage(db, [code.id]).get(code.id, 0)
    if used and payload.migrate_to_id is None and not payload.justification.strip():
        raise HTTPException(status_code=422,
                            detail="O código tem trechos: migre-os para outro código ou justifique o descarte.")
    if payload.migrate_to_id is not None:
        target = _code(db, review, payload.migrate_to_id)
        if target.status != "active" or target.id == code.id:
            raise HTTPException(status_code=422, detail="Migre os trechos para outro código ativo.")
        for application in db.scalars(select(SegmentCode).where(SegmentCode.code_id == code.id)).all():
            duplicate = db.scalar(select(SegmentCode.id).where(
                SegmentCode.segment_id == application.segment_id, SegmentCode.code_id == target.id,
                SegmentCode.coder_id == application.coder_id, SegmentCode.is_final == application.is_final))
            if duplicate is not None:
                db.delete(application)
            else:
                application.code_id = target.id
    else:
        db.execute(delete(SegmentCode).where(SegmentCode.code_id == code.id))
    previous = _snapshot(code)
    code.status = "removed"
    _event(db, review, user, "removed", code, previous,
           {**_snapshot(code), "segments": used, "migrated_to": payload.migrate_to_id}, payload.justification.strip())
    db.commit()
    return code_out(code, 0)


@router.get("/reviews/{review_id}/codes/{code_id}/history")
def code_history(code_id: int, review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    code = _code(db, review, code_id)
    related = [code.id, *db.scalars(select(Code.id).where(Code.merged_into_id == code.id))]
    events = db.scalars(select(CodeEvent).where(CodeEvent.code_id.in_(related)).order_by(CodeEvent.id)).all()
    return [_event_out(db, event) for event in events]


def _event_out(db: DbSession, event: CodeEvent) -> dict[str, Any]:
    user = db.get(User, event.user_id) if event.user_id else None
    return {
        "sequence": event.id, "code_id": event.code_id, "action": event.action, "previous": event.previous,
        "new": event.new, "justification": event.justification, "user": None if user is None else user.username,
        "created_at": event.created_at.isoformat(),
    }


@router.get("/reviews/{review_id}/coding/events")
def export_events(review: MemberReview, db: DbSession, format: Literal["json", "csv"] = "json") -> Response:
    events = [_event_out(db, event) for event in
              db.scalars(select(CodeEvent).where(CodeEvent.review_id == review.id).order_by(CodeEvent.id))]
    if format == "json":
        return Response(json.dumps(events, ensure_ascii=False, indent=2), media_type="application/json",
                        headers={"Content-Disposition": f'attachment; filename="{review.name}-codificacao.json"'})
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["sequencia", "data", "usuario", "acao", "codigo_id", "anterior", "novo", "justificativa"])
    for event in events:
        writer.writerow([event["sequence"], event["created_at"], event["user"], event["action"], event["code_id"],
                         json.dumps(event["previous"], ensure_ascii=False), json.dumps(event["new"], ensure_ascii=False),
                         event["justification"]])
    return Response(buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{review.name}-codificacao.csv"'})


# ---- coding --------------------------------------------------------------------------

class SettingsIn(BaseModel):
    dual_enabled: bool
    sample_percent: int = Field(default=20, ge=1, le=100)
    coder_a_id: int | None = None
    coder_b_id: int | None = None


def _settings_out(db: DbSession, review: Review, settings: CodingSettings) -> dict[str, Any]:
    sample = db.scalars(select(CodingSample).where(CodingSample.review_id == review.id)).all()
    return {
        "dual_enabled": settings.dual_enabled, "sample_percent": settings.sample_percent,
        "coder_a_id": settings.coder_a_id, "coder_b_id": settings.coder_b_id,
        "codebook_verified_by_id": settings.codebook_verified_by_id,
        "codebook_verified_at": None if settings.codebook_verified_at is None else settings.codebook_verified_at.isoformat(),
        "closed_at": None if settings.closed_at is None else settings.closed_at.isoformat(),
        "close_justification": settings.close_justification,
        "sample": [{"article_id": item.article_id, "coder_a_done": item.coder_a_done,
                    "coder_b_done": item.coder_b_done} for item in sample],
    }


@router.get("/reviews/{review_id}/coding")
def coding_overview(review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _settings(db, review)
    db.commit()
    articles = final_articles(db, review)
    counts = dict(db.execute(select(Segment.article_id, func.count()).where(Segment.review_id == review.id)
                             .group_by(Segment.article_id)).all())
    sample_ids = {item["article_id"] for item in _settings_out(db, review, settings)["sample"]} if settings.dual_enabled else set()
    return {
        "settings": _settings_out(db, review, settings),
        "my_slot": _slot(settings, user),
        "articles": [{"id": article.id, "title": article.title, "author": article.author, "year": article.year,
                      "segments": counts.get(article.id, 0), "in_sample": article.id in sample_ids}
                     for article in articles],
    }


@router.put("/reviews/{review_id}/coding/settings")
def save_settings(payload: SettingsIn, review: OwnerReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    if payload.dual_enabled:
        members = {review.author_id, *(coauthor.id for coauthor in review.co_authors)}
        if payload.coder_a_id is None or payload.coder_b_id is None or payload.coder_a_id == payload.coder_b_id \
                or not {payload.coder_a_id, payload.coder_b_id} <= members:
            raise HTTPException(status_code=422, detail="Escolha dois membros diferentes da revisão como codificadores.")
    settings.dual_enabled, settings.sample_percent = payload.dual_enabled, payload.sample_percent
    settings.coder_a_id, settings.coder_b_id = payload.coder_a_id, payload.coder_b_id
    if payload.dual_enabled and db.scalar(select(func.count()).select_from(CodingSample)
                                          .where(CodingSample.review_id == review.id)) == 0:
        # Spec 007 rule 4: the system draws the sample; it is never chosen by hand.
        candidates = sorted(_final_ids(db, review))
        size = max(1, math.ceil(len(candidates) * payload.sample_percent / 100)) if candidates else 0
        for article_id in random.SystemRandom().sample(candidates, size):
            db.add(CodingSample(review_id=review.id, article_id=article_id))
    if payload.dual_enabled:
        notify(db, [payload.coder_a_id, payload.coder_b_id], "dual_coding",
               f"Você é codificador da amostra de dupla codificação em '{review.title}'", review,
               f"/revisoes/{review.id}/sintese/codificacao", exclude=user.id)
    log_activity(db, user, "configurou a codificação de", review)
    db.commit()
    return _settings_out(db, review, settings)


class SegmentIn(BaseModel):
    text: str
    page: str = Field(default="", max_length=20)
    code_ids: list[int] = Field(default_factory=list)


class SegmentCodesIn(BaseModel):
    code_ids: list[int]


def _visible_codes(db: DbSession, review: Review, settings: CodingSettings, segment: Segment, user: User) -> dict[str, Any]:
    applications = db.scalars(select(SegmentCode).where(SegmentCode.segment_id == segment.id)).all()
    final = sorted(item.code_id for item in applications if item.is_final)
    sample = _sample(db, review, settings, segment.article_id)
    data: dict[str, Any] = {"final": final}
    if sample is not None:
        mine = sorted(item.code_id for item in applications if not item.is_final and item.coder_id == user.id)
        data["mine"] = mine
        if _both_done(sample):
            data["coder_a"] = sorted(i.code_id for i in applications if not i.is_final and i.coder_id == settings.coder_a_id)
            data["coder_b"] = sorted(i.code_id for i in applications if not i.is_final and i.coder_id == settings.coder_b_id)
    return data


def _segment_out(db: DbSession, review: Review, settings: CodingSettings, segment: Segment, user: User) -> dict[str, Any]:
    return {"id": segment.id, "article_id": segment.article_id, "text": segment.text, "page": segment.page,
            "created_by_id": segment.created_by_id, "codes": _visible_codes(db, review, settings, segment, user)}


def _coding_article(db: DbSession, review: Review, article_id: int) -> Article:
    article = db.get(Article, article_id)
    if article is None or article.review_id != review.id:
        raise HTTPException(status_code=404, detail="Artigo não encontrado nesta revisão.")
    if article.id not in _final_ids(db, review):
        raise HTTPException(status_code=422, detail="Só estudos da seleção final podem ser codificados.")
    return article


def _apply(db: DbSession, review: Review, settings: CodingSettings, segment: Segment, user: User,
           code_ids: list[int]) -> None:
    sample = _sample(db, review, settings, segment.article_id)
    if sample is not None:
        slot = _slot(settings, user)
        if slot is None:
            raise HTTPException(status_code=403, detail="Este estudo está na amostra de dupla codificação.")
        if getattr(sample, f"coder_{slot}_done"):
            raise HTTPException(status_code=409, detail="Você já concluiu a codificação deste estudo.")
        db.execute(delete(SegmentCode).where(SegmentCode.segment_id == segment.id, SegmentCode.coder_id == user.id,
                                             SegmentCode.is_final.is_(False)))
        for code_id in code_ids:
            db.add(SegmentCode(segment_id=segment.id, code_id=code_id, coder_id=user.id, is_final=False))
        return
    db.execute(delete(SegmentCode).where(SegmentCode.segment_id == segment.id, SegmentCode.is_final.is_(True)))
    for code_id in code_ids:
        db.add(SegmentCode(segment_id=segment.id, code_id=code_id, coder_id=user.id, is_final=True))


@router.get("/reviews/{review_id}/articles/{article_id}/segments")
def list_segments(article_id: int, review: MemberReview, db: DbSession, user: CurrentUser) -> list[dict[str, Any]]:
    _coding_article(db, review, article_id)
    settings = _settings(db, review)
    db.commit()
    segments = db.scalars(select(Segment).where(Segment.article_id == article_id).order_by(Segment.id)).all()
    return [_segment_out(db, review, settings, segment, user) for segment in segments]


@router.post("/reviews/{review_id}/articles/{article_id}/segments", status_code=201)
def create_segment(article_id: int, payload: SegmentIn, review: MemberReview, db: DbSession,
                   user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    article = _coding_article(db, review, article_id)
    text, page = payload.text.strip(), payload.page.strip()
    if not text:
        raise HTTPException(status_code=422, detail="Cole o trecho exato do estudo.")
    if not page:
        raise HTTPException(status_code=422, detail="Informe a página do trecho.")
    code_ids = _active_code_ids(db, review, payload.code_ids)
    sample = _sample(db, review, settings, article.id)
    if sample is not None and _slot(settings, user) is None:
        raise HTTPException(status_code=403, detail="Este estudo está na amostra de dupla codificação.")
    segment = Segment(review_id=review.id, article_id=article.id, text=text, page=page, created_by_id=user.id)
    db.add(segment)
    db.flush()
    _apply(db, review, settings, segment, user, code_ids)
    db.commit()
    return _segment_out(db, review, settings, segment, user)


def _segment(db: DbSession, review: Review, segment_id: int) -> Segment:
    segment = db.get(Segment, segment_id)
    if segment is None or segment.review_id != review.id:
        raise HTTPException(status_code=404, detail="Trecho não encontrado nesta revisão.")
    return segment


@router.put("/reviews/{review_id}/segments/{segment_id}/codes")
def set_segment_codes(segment_id: int, payload: SegmentCodesIn, review: MemberReview, db: DbSession,
                      user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    segment = _segment(db, review, segment_id)
    _apply(db, review, settings, segment, user, _active_code_ids(db, review, payload.code_ids))
    db.commit()
    return _segment_out(db, review, settings, segment, user)


@router.delete("/reviews/{review_id}/segments/{segment_id}", status_code=204)
def delete_segment(segment_id: int, review: MemberReview, db: DbSession, user: CurrentUser) -> Response:
    _ensure_open(db, review)
    segment = _segment(db, review, segment_id)
    log_activity(db, user, "removeu um trecho codificado de", review, segment.text[:80])
    db.delete(segment)
    db.commit()
    return Response(status_code=204)


# ---- dual coding ---------------------------------------------------------------------

def _finalize_agreed(db: DbSession, review: Review, settings: CodingSettings, sample: CodingSample) -> None:
    """When both coders are done, segments with identical code sets become final automatically."""
    for segment in db.scalars(select(Segment).where(Segment.article_id == sample.article_id)):
        rows = db.scalars(select(SegmentCode).where(SegmentCode.segment_id == segment.id)).all()
        first = {row.code_id for row in rows if not row.is_final and row.coder_id == settings.coder_a_id}
        second = {row.code_id for row in rows if not row.is_final and row.coder_id == settings.coder_b_id}
        if first == second and not any(row.is_final for row in rows):
            for code_id in first:
                db.add(SegmentCode(segment_id=segment.id, code_id=code_id, coder_id=None, is_final=True))


@router.post("/reviews/{review_id}/coding/sample/{article_id}/done")
def finish_sample_article(article_id: int, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    sample = _sample(db, review, settings, article_id)
    slot = _slot(settings, user)
    if sample is None or slot is None:
        raise HTTPException(status_code=404, detail="Estudo fora da amostra ou você não é codificador.")
    setattr(sample, f"coder_{slot}_done", True)
    db.flush()
    if _both_done(sample):
        _finalize_agreed(db, review, settings, sample)
    db.commit()
    return {"article_id": article_id, "coder_a_done": sample.coder_a_done, "coder_b_done": sample.coder_b_done}


def agreement_data(db: DbSession, review: Review) -> dict[str, Any]:
    settings = _settings(db, review)
    done = [item for item in db.scalars(select(CodingSample).where(CodingSample.review_id == review.id))
            if _both_done(item)] if settings.dual_enabled else []
    first: dict[int, set[int]] = {}
    second: dict[int, set[int]] = {}
    divergences = []
    for item in done:
        for segment in db.scalars(select(Segment).where(Segment.article_id == item.article_id).order_by(Segment.id)):
            rows = db.scalars(select(SegmentCode).where(SegmentCode.segment_id == segment.id)).all()
            first[segment.id] = {row.code_id for row in rows if not row.is_final and row.coder_id == settings.coder_a_id}
            second[segment.id] = {row.code_id for row in rows if not row.is_final and row.coder_id == settings.coder_b_id}
            if first[segment.id] != second[segment.id]:
                divergences.append({
                    "segment_id": segment.id, "article_id": segment.article_id, "text": segment.text,
                    "page": segment.page, "coder_a": sorted(first[segment.id]), "coder_b": sorted(second[segment.id]),
                    "final": sorted(row.code_id for row in rows if row.is_final),
                    "resolved": any(row.is_final for row in rows),
                })
    codes = sorted({code for values in (*first.values(), *second.values()) for code in values})
    return {"enabled": settings.dual_enabled, "articles_done": len(done),
            **coding_agreement(first, second, codes), "divergences": divergences}


@router.get("/reviews/{review_id}/coding/agreement")
def get_agreement(review: MemberReview, db: DbSession) -> dict[str, Any]:
    data = agreement_data(db, review)
    db.commit()
    return data


class ResolveIn(BaseModel):
    code_ids: list[int]
    justification: str


@router.post("/reviews/{review_id}/segments/{segment_id}/resolve")
def resolve_segment(segment_id: int, payload: ResolveIn, review: MemberReview, db: DbSession,
                    user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    segment = _segment(db, review, segment_id)
    if not _both_done(_sample(db, review, settings, segment.article_id)):
        raise HTTPException(status_code=422, detail="A divergência só é resolvida depois que os dois codificadores concluem.")
    if not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Registre a justificativa da resolução.")
    code_ids = _active_code_ids(db, review, payload.code_ids)
    db.execute(delete(SegmentCode).where(SegmentCode.segment_id == segment.id, SegmentCode.is_final.is_(True)))
    for code_id in code_ids:
        db.add(SegmentCode(segment_id=segment.id, code_id=code_id, coder_id=user.id, is_final=True))
    db.add(SegmentResolution(segment_id=segment.id, code_ids=code_ids, justification=payload.justification.strip(),
                             user_id=user.id))
    db.commit()
    return _segment_out(db, review, settings, segment, user)


# ---- phase: verification and closing ------------------------------------------------------

class CloseIn(BaseModel):
    justification: str = ""


@router.post("/reviews/{review_id}/coding/verify-codebook")
def verify_codebook(review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    creators = set(db.scalars(select(Code.created_by_id).where(Code.review_id == review.id, Code.status == "active")))
    if not creators:
        raise HTTPException(status_code=422, detail="Não há códigos ativos para conferir.")
    if creators == {user.id}:
        raise HTTPException(status_code=422, detail="O codebook deve ser conferido por outro membro, não por quem o criou.")
    settings.codebook_verified_by_id, settings.codebook_verified_at = user.id, utcnow()
    log_activity(db, user, "conferiu o codebook de", review)
    db.commit()
    return _settings_out(db, review, settings)


@router.post("/reviews/{review_id}/coding/close")
def close_coding(payload: CloseIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _ensure_open(db, review)
    problems = []
    if settings.codebook_verified_at is None:
        problems.append("o codebook ainda não foi conferido por outro membro")
    if settings.dual_enabled:
        agreement = agreement_data(db, review)
        pending = db.scalar(select(func.count()).select_from(CodingSample).where(
            CodingSample.review_id == review.id,
            (CodingSample.coder_a_done.is_(False)) | (CodingSample.coder_b_done.is_(False)))) or 0
        if pending:
            problems.append(f"{pending} estudo(s) da amostra ainda sem dupla codificação concluída")
        if agreement["value"] is None or agreement["value"] < AGREEMENT_THRESHOLD:
            problems.append(f"a concordância ({agreement['metric']}) está abaixo de {AGREEMENT_THRESHOLD}")
        if any(not item["resolved"] for item in agreement["divergences"]):
            problems.append("há divergências sem resolução")
    if problems and not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Não é possível fechar: " + "; ".join(problems)
                            + ". Registre uma justificativa para fechar mesmo assim.")
    settings.closed_at, settings.closed_by_id = utcnow(), user.id
    settings.close_justification = payload.justification.strip()
    log_activity(db, user, "fechou a codificação de", review, "; ".join(problems))
    db.commit()
    return {**_settings_out(db, review, settings), "problems": problems}


@router.post("/reviews/{review_id}/coding/reopen")
def reopen_coding(review: OwnerReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    settings = _settings(db, review)
    settings.closed_at, settings.closed_by_id, settings.close_justification = None, None, ""
    log_activity(db, user, "reabriu a codificação de", review)
    db.commit()
    return _settings_out(db, review, settings)


# ---- themes ---------------------------------------------------------------------------------

class ThemeIn(BaseModel):
    name: str = Field(max_length=200)
    description: str = ""
    code_ids: list[int] = Field(default_factory=list)
    child_theme_ids: list[int] = Field(default_factory=list)
    justification: str = ""


class ThemeCodeIn(BaseModel):
    code_id: int
    justification: str = ""


def _theme(db: DbSession, review: Review, theme_id: int) -> Theme:
    theme = db.get(Theme, theme_id)
    if theme is None or theme.review_id != review.id:
        raise HTTPException(status_code=404, detail="Tema não encontrado nesta revisão.")
    return theme


def _link_code(db: DbSession, review: Review, theme: Theme, code_id: int, justification: str) -> None:
    code = _code(db, review, code_id)
    if code.status != "active":
        raise HTTPException(status_code=422, detail="Só códigos ativos entram em temas.")
    if db.get(ThemeCode, (theme.id, code.id)) is not None:
        return
    elsewhere = db.scalar(select(func.count()).select_from(ThemeCode).where(ThemeCode.code_id == code.id))
    if elsewhere and not justification.strip():
        raise HTTPException(status_code=422, detail=f"'{code.name}' já está em outro tema: justifique o uso em mais de um.")
    db.add(ThemeCode(theme_id=theme.id, code_id=code.id, justification=justification.strip()))


@router.get("/reviews/{review_id}/themes")
def list_themes(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    themes = db.scalars(select(Theme).where(Theme.review_id == review.id).order_by(func.lower(Theme.name))).all()
    links = db.scalars(select(ThemeCode).join(Theme, Theme.id == ThemeCode.theme_id).where(Theme.review_id == review.id)).all()
    codes = {code.id: code for code in db.scalars(select(Code).where(Code.review_id == review.id))}
    segments_by_code: dict[int, list[dict[str, Any]]] = {}
    rows = db.execute(
        select(SegmentCode.code_id, Segment.id, Segment.text, Segment.page, Article.id, Article.title)
        .join(Segment, Segment.id == SegmentCode.segment_id).join(Article, Article.id == Segment.article_id)
        .where(Segment.review_id == review.id, SegmentCode.is_final.is_(True)).order_by(Segment.id)
    ).all()
    for code_id, segment_id, text, page, article_id, title in rows:
        segments_by_code.setdefault(code_id, []).append(
            {"id": segment_id, "text": text, "page": page, "article_id": article_id, "article_title": title})
    return [
        {
            "id": theme.id, "name": theme.name, "description": theme.description, "parent_id": theme.parent_id,
            "codes": [
                {**code_out(codes[link.code_id], len(segments_by_code.get(link.code_id, []))),
                 "justification": link.justification, "evidence": segments_by_code.get(link.code_id, [])}
                for link in links if link.theme_id == theme.id
            ],
        }
        for theme in themes
    ]


@router.post("/reviews/{review_id}/themes", status_code=201)
def create_theme(payload: ThemeIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    if not payload.name.strip():
        raise HTTPException(status_code=422, detail="Informe o nome do tema.")
    if not payload.code_ids and not payload.child_theme_ids:
        raise HTTPException(status_code=422, detail="Um tema precisa de pelo menos um código (ou de temas, se for de ordem superior).")
    theme = Theme(review_id=review.id, name=payload.name.strip(), description=payload.description.strip(),
                  created_by_id=user.id)
    db.add(theme)
    db.flush()
    for code_id in dict.fromkeys(payload.code_ids):
        _link_code(db, review, theme, code_id, payload.justification)
    for child_id in dict.fromkeys(payload.child_theme_ids):
        child = _theme(db, review, child_id)
        if child.id == theme.id:
            raise HTTPException(status_code=422, detail="Um tema não pode conter a si mesmo.")
        child.parent_id = theme.id
    log_activity(db, user, "criou o tema", review, theme.name)
    db.commit()
    return next(item for item in list_themes(review, db) if item["id"] == theme.id)


class ThemeUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    description: str | None = None
    parent_id: int | None = None
    clear_parent: bool = False


@router.patch("/reviews/{review_id}/themes/{theme_id}")
def update_theme(theme_id: int, payload: ThemeUpdate, review: MemberReview, db: DbSession) -> dict[str, Any]:
    theme = _theme(db, review, theme_id)
    if payload.name is not None:
        if not payload.name.strip():
            raise HTTPException(status_code=422, detail="Informe o nome do tema.")
        theme.name = payload.name.strip()
    if payload.description is not None:
        theme.description = payload.description.strip()
    if payload.clear_parent:
        theme.parent_id = None
    elif payload.parent_id is not None:
        parent = _theme(db, review, payload.parent_id)
        ancestor: Theme | None = parent
        while ancestor is not None:
            if ancestor.id == theme.id:
                raise HTTPException(status_code=422, detail="Isso criaria um ciclo entre temas.")
            ancestor = db.get(Theme, ancestor.parent_id) if ancestor.parent_id else None
        theme.parent_id = parent.id
    db.commit()
    return next(item for item in list_themes(review, db) if item["id"] == theme.id)


@router.delete("/reviews/{review_id}/themes/{theme_id}", status_code=204)
def delete_theme(theme_id: int, review: MemberReview, db: DbSession, user: CurrentUser) -> Response:
    theme = _theme(db, review, theme_id)
    for child in db.scalars(select(Theme).where(Theme.parent_id == theme.id)):
        child.parent_id = theme.parent_id
    log_activity(db, user, "removeu o tema", review, theme.name)
    db.delete(theme)
    db.commit()
    return Response(status_code=204)


@router.post("/reviews/{review_id}/themes/{theme_id}/codes", status_code=201)
def add_theme_code(theme_id: int, payload: ThemeCodeIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    theme = _theme(db, review, theme_id)
    _link_code(db, review, theme, payload.code_id, payload.justification)
    db.commit()
    return next(item for item in list_themes(review, db) if item["id"] == theme.id)


@router.delete("/reviews/{review_id}/themes/{theme_id}/codes/{code_id}", status_code=204)
def remove_theme_code(theme_id: int, code_id: int, review: MemberReview, db: DbSession) -> Response:
    theme = _theme(db, review, theme_id)
    link = db.get(ThemeCode, (theme.id, code_id))
    if link is None:
        raise HTTPException(status_code=404, detail="Código não está neste tema.")
    remaining = db.scalar(select(func.count()).select_from(ThemeCode).where(ThemeCode.theme_id == theme.id)) or 0
    has_children = db.scalar(select(func.count()).select_from(Theme).where(Theme.parent_id == theme.id)) or 0
    if remaining <= 1 and not has_children:
        raise HTTPException(status_code=422, detail="O tema ficaria sem códigos. Remova o tema ou adicione outro código antes.")
    db.delete(link)
    db.commit()
    return Response(status_code=204)


# ---- reliability checklist ---------------------------------------------------------------------

class ChecklistIn(BaseModel):
    met: bool
    justification: str


@router.get("/reviews/{review_id}/synthesis-checklist")
def get_checklist(review: MemberReview, db: DbSession) -> dict[str, Any]:
    rows = {row.item: row for row in db.scalars(select(SynthesisChecklistItem).where(
        SynthesisChecklistItem.review_id == review.id))}
    items = [
        {"item": number, "text": text, "met": rows[number].met if number in rows else None,
         "justification": rows[number].justification if number in rows else ""}
        for number, text in CHECKLIST_ITEMS.items()
    ]
    return {"items": items, "evaluated": all(item["justification"] for item in items)}


@router.put("/reviews/{review_id}/synthesis-checklist/{item}")
def save_checklist_item(item: int, payload: ChecklistIn, review: MemberReview, db: DbSession,
                        user: CurrentUser) -> dict[str, Any]:
    if item not in CHECKLIST_ITEMS:
        raise HTTPException(status_code=404, detail="Item desconhecido.")
    if not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Cada item exige justificativa.")
    row = db.get(SynthesisChecklistItem, (review.id, item))
    if row is None:
        row = SynthesisChecklistItem(review_id=review.id, item=item)
        db.add(row)
    row.met, row.justification, row.user_id = payload.met, payload.justification.strip(), user.id
    db.commit()
    return get_checklist(review, db)
