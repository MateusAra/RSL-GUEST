"""Collaboration and traceability (spec 009 adapted, no new roles)."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ..agreement import AGREEMENT_THRESHOLD
from ..db import utcnow
from ..deps import CurrentUser, DbSession, MemberReview, log_activity
from ..models import (
    ARTICLE_STATUSES,
    STAGES,
    Article,
    ArticleAssignment,
    ArticleComment,
    Code,
    DataExtractionField,
    Notification,
    Question,
    QuestionField,
    QuestionTheme,
    Review,
    Segment,
    SegmentCode,
    Theme,
    ThemeCode,
    User,
)
from ..notify import notify
from ..serializers import user_public
from .analysis import _accepted, _extraction_values, _fields, final_articles, quality_scores
from .conducting import _article
from .synthesis import agreement_data

router = APIRouter(tags=["colaboração"])

Stage = Literal["selection", "quality", "extraction", "coding"]
STAGE_PATHS = {"selection": "conducao/selecao", "quality": "conducao/qualidade", "extraction": "conducao/extracao",
               "coding": "sintese/codificacao"}


def _members(review: Review) -> dict[int, User]:
    return {review.author_id: review.author, **{user.id: user for user in review.co_authors}}


def _stage_articles(db: DbSession, review: Review, stage: str) -> list[Article]:
    """Articles that take part in a stage: non-duplicates for selection, accepted for quality, final otherwise."""
    if stage == "selection":
        return list(db.scalars(select(Article).where(Article.review_id == review.id, Article.status != "D").order_by(Article.id)))
    if stage == "quality":
        return _accepted(db, review)
    return final_articles(db, review)


def _assignments(db: DbSession, review: Review, stage: str) -> dict[int, ArticleAssignment]:
    return {item.article_id: item for item in db.scalars(select(ArticleAssignment).where(
        ArticleAssignment.review_id == review.id, ArticleAssignment.stage == stage))}


# ---- assignments --------------------------------------------------------------------

class DistributeIn(BaseModel):
    stage: Stage
    user_ids: list[int]


class AssignIn(BaseModel):
    stage: Stage
    user_id: int | None
    justification: str = ""


@router.get("/reviews/{review_id}/assignments")
def list_assignments(review: MemberReview, db: DbSession, stage: Stage) -> dict[str, Any]:
    members = _members(review)
    return {
        "stage": stage,
        "assignments": {str(article_id): {"user_id": item.user_id, "user": user_public(members[item.user_id])
                                          if item.user_id in members else None}
                        for article_id, item in _assignments(db, review, stage).items()},
    }


@router.post("/reviews/{review_id}/assignments/distribute")
def distribute(payload: DistributeIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    """Round-robin the unassigned articles of a stage among the chosen members, balancing current load."""
    members = _members(review)
    chosen = list(dict.fromkeys(payload.user_ids))
    if not chosen or not set(chosen) <= members.keys():
        raise HTTPException(status_code=422, detail="Escolha membros desta revisão.")
    current = _assignments(db, review, payload.stage)
    load = {member_id: sum(item.user_id == member_id for item in current.values()) for member_id in chosen}
    created: dict[int, int] = {member_id: 0 for member_id in chosen}
    for article in _stage_articles(db, review, payload.stage):
        if article.id in current:
            continue
        member_id = min(chosen, key=lambda item: (load[item], chosen.index(item)))
        db.add(ArticleAssignment(review_id=review.id, article_id=article.id, stage=payload.stage, user_id=member_id,
                                 assigned_by_id=user.id))
        load[member_id] += 1
        created[member_id] += 1
    for member_id, count in created.items():
        if count:
            notify(db, [member_id], "assignment", f"{count} estudo(s) atribuído(s) a você em {STAGES[payload.stage]}: {review.title}",
                   review, f"/revisoes/{review.id}/{STAGE_PATHS[payload.stage]}", exclude=user.id)
    log_activity(db, user, f"distribuiu {sum(created.values())} estudo(s) de {STAGES[payload.stage]} em", review)
    db.commit()
    return {"stage": payload.stage, "assigned": {str(key): value for key, value in created.items()}, "load": {str(k): v for k, v in load.items()}}


@router.put("/reviews/{review_id}/articles/{article_id}/assignment")
def assign(article_id: int, payload: AssignIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    members = _members(review)
    if payload.user_id is not None and payload.user_id not in members:
        raise HTTPException(status_code=422, detail="Atribua a um membro desta revisão.")
    existing = db.scalar(select(ArticleAssignment).where(ArticleAssignment.article_id == article.id,
                                                         ArticleAssignment.stage == payload.stage))
    previous_user_id = None if existing is None else existing.user_id
    if previous_user_id is not None and previous_user_id != payload.user_id and not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Reatribuir exige justificativa.")
    if payload.user_id is None:
        if existing is not None:
            db.delete(existing)
    elif existing is None:
        db.add(ArticleAssignment(review_id=review.id, article_id=article.id, stage=payload.stage, user_id=payload.user_id,
                                 assigned_by_id=user.id))
    else:
        existing.user_id, existing.assigned_by_id = payload.user_id, user.id
    if payload.user_id is not None and payload.user_id != previous_user_id:
        notify(db, [payload.user_id], "assignment", f"'{article.title}' foi atribuído a você em {STAGES[payload.stage]}",
               review, f"/revisoes/{review.id}/{STAGE_PATHS[payload.stage]}", exclude=user.id)
    target = members[payload.user_id].username if payload.user_id is not None else "ninguém"
    log_activity(db, user, f"atribuiu ({STAGES[payload.stage]}) a {target}", review,
                 f"{article.title} — {payload.justification.strip()}" if payload.justification.strip() else article.title)
    db.commit()
    return {"article_id": article.id, "stage": payload.stage, "user_id": payload.user_id}


# ---- discussions ------------------------------------------------------------------------

class CommentIn(BaseModel):
    body: str = Field(max_length=4000)
    is_resolution: bool = False


def _comment_out(db: DbSession, comment: ArticleComment) -> dict[str, Any]:
    author = db.get(User, comment.user_id) if comment.user_id else None
    return {"id": comment.id, "user": None if author is None else user_public(author), "body": comment.body,
            "is_resolution": comment.is_resolution,
            "resolution_status": None if comment.resolution_status is None else ARTICLE_STATUSES[comment.resolution_status],
            "created_at": comment.created_at.isoformat()}


@router.get("/reviews/{review_id}/articles/{article_id}/comments")
def list_comments(article_id: int, review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    _article(db, review, article_id)
    return [_comment_out(db, item) for item in db.scalars(
        select(ArticleComment).where(ArticleComment.article_id == article_id).order_by(ArticleComment.id))]


@router.post("/reviews/{review_id}/articles/{article_id}/comments", status_code=201)
def add_comment(article_id: int, payload: CommentIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    body = payload.body.strip()
    if not body:
        raise HTTPException(status_code=422, detail="Escreva a mensagem.")
    comment = ArticleComment(review_id=review.id, article_id=article.id, user_id=user.id, body=body,
                             is_resolution=payload.is_resolution,
                             resolution_status=article.status if payload.is_resolution else None)
    db.add(comment)
    participants = list(db.scalars(select(ArticleComment.user_id).where(ArticleComment.article_id == article.id)))
    assignees = list(db.scalars(select(ArticleAssignment.user_id).where(ArticleAssignment.article_id == article.id)))
    notify(db, [*participants, *assignees], "comment",
           f"{user.full_name} {'resolveu a discussão' if payload.is_resolution else 'comentou'} em '{article.title}'",
           review, f"/revisoes/{review.id}/conducao/selecao?artigo={article.id}", exclude=user.id)
    db.commit()
    return _comment_out(db, comment)


# ---- notifications ---------------------------------------------------------------------------

@router.get("/notifications")
def my_notifications(db: DbSession, user: CurrentUser) -> dict[str, Any]:
    items = db.scalars(select(Notification).where(Notification.user_id == user.id)
                       .order_by(Notification.read_at.is_not(None), Notification.created_at.desc()).limit(50)).all()
    unread = db.scalar(select(func.count()).select_from(Notification).where(
        Notification.user_id == user.id, Notification.read_at.is_(None))) or 0
    return {"unread": unread, "items": [
        {"id": item.id, "kind": item.kind, "message": item.message, "link": item.link, "review_id": item.review_id,
         "read": item.read_at is not None, "created_at": item.created_at.isoformat()} for item in items]}


@router.post("/notifications/{notification_id}/read", status_code=204)
def mark_read(notification_id: int, db: DbSession, user: CurrentUser) -> Response:
    item = db.get(Notification, notification_id)
    if item is None or item.user_id != user.id:
        raise HTTPException(status_code=404, detail="Notificação não encontrada.")
    item.read_at = item.read_at or utcnow()
    db.commit()
    return Response(status_code=204)


@router.post("/notifications/read-all", status_code=204)
def mark_all_read(db: DbSession, user: CurrentUser) -> Response:
    for item in db.scalars(select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))):
        item.read_at = utcnow()
    db.commit()
    return Response(status_code=204)


# ---- dashboard ------------------------------------------------------------------------------------

def _pending(stage: str, article: Article, scores: dict, segments: set[int]) -> bool:
    if stage == "selection":
        return article.status == "U"
    if stage == "quality":
        return not scores.get(article.id, {}).get("complete", False)
    if stage == "extraction":
        return not article.finished_data_extraction
    return article.id not in segments


@router.get("/reviews/{review_id}/dashboard")
def dashboard(review: MemberReview, db: DbSession) -> dict[str, Any]:
    statuses = dict(db.execute(select(Article.status, func.count()).where(Article.review_id == review.id)
                               .group_by(Article.status)).all())
    scores = quality_scores(db, review)
    final = final_articles(db, review)
    coded = set(db.scalars(select(Segment.article_id).where(Segment.review_id == review.id)))
    members = _members(review)
    per_member: dict[int, dict[str, dict[str, int]]] = {member_id: {} for member_id in members}
    for stage in STAGES:
        stage_articles = {article.id: article for article in _stage_articles(db, review, stage)}
        for article_id, item in _assignments(db, review, stage).items():
            if item.user_id not in per_member or article_id not in stage_articles:
                continue
            bucket = per_member[item.user_id].setdefault(stage, {"assigned": 0, "pending": 0})
            bucket["assigned"] += 1
            bucket["pending"] += _pending(stage, stage_articles[article_id], scores, coded)
    agreement = agreement_data(db, review)
    db.commit()
    return {
        "selection": {code: statuses.get(code, 0) for code in ARTICLE_STATUSES},
        "quality": {"accepted": len(scores), "complete": sum(entry["complete"] for entry in scores.values()),
                    "incomplete": sum(not entry["complete"] for entry in scores.values())},
        "extraction": {"final": len(final), "finished": sum(article.finished_data_extraction for article in final)},
        "coding": {"studies_coded": len(coded & {article.id for article in final}), "final": len(final),
                   "segments": db.scalar(select(func.count()).select_from(Segment).where(Segment.review_id == review.id)) or 0,
                   "agreement": agreement["value"] if agreement["enabled"] else None,
                   "agreement_metric": agreement["metric"], "agreement_threshold": AGREEMENT_THRESHOLD},
        "members": [{"user": user_public(members[member_id]), "stages": stages} for member_id, stages in per_member.items()],
    }


# ---- evidence chain --------------------------------------------------------------------------------

class LinksIn(BaseModel):
    field_ids: list[int] = Field(default_factory=list)
    theme_ids: list[int] = Field(default_factory=list)


class ConclusionIn(BaseModel):
    conclusion: str


def _question(db: DbSession, review: Review, question_id: int) -> Question:
    question = db.get(Question, question_id)
    if question is None or question.review_id != review.id:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada nesta revisão.")
    return question


@router.put("/reviews/{review_id}/questions/{question_id}/links")
def save_links(question_id: int, payload: LinksIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    question = _question(db, review, question_id)
    fields = set(db.scalars(select(DataExtractionField.id).where(DataExtractionField.review_id == review.id)))
    themes = set(db.scalars(select(Theme.id).where(Theme.review_id == review.id)))
    if not set(payload.field_ids) <= fields or not set(payload.theme_ids) <= themes:
        raise HTTPException(status_code=422, detail="Campos e temas precisam ser desta revisão.")
    db.query(QuestionField).filter(QuestionField.question_id == question.id).delete()
    db.query(QuestionTheme).filter(QuestionTheme.question_id == question.id).delete()
    for field_id in dict.fromkeys(payload.field_ids):
        db.add(QuestionField(question_id=question.id, field_id=field_id))
    for theme_id in dict.fromkeys(payload.theme_ids):
        db.add(QuestionTheme(question_id=question.id, theme_id=theme_id))
    db.commit()
    return {"question_id": question.id, "field_ids": payload.field_ids, "theme_ids": payload.theme_ids}


@router.put("/reviews/{review_id}/questions/{question_id}/conclusion")
def save_conclusion(question_id: int, payload: ConclusionIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    question = _question(db, review, question_id)
    question.conclusion = payload.conclusion.strip()
    log_activity(db, user, "registrou a conclusão da pergunta", review, question.question)
    db.commit()
    return {"question_id": question.id, "conclusion": question.conclusion}


def _display(field: DataExtractionField, value: Any) -> str:
    lookups = {lookup.id: lookup.value for lookup in field.lookups}
    if field.field_type == "M":
        return "; ".join(lookups.get(item, "") for item in value or [])
    if field.field_type == "O":
        return lookups.get(value, "") if value else ""
    if field.field_type == "B":
        return {"True": "Sim", "False": "Não"}.get(value or "", "")
    return value or ""


def _theme_codes(db: DbSession, theme_ids: list[int]) -> dict[int, list[int]]:
    """Codes of each theme, including the codes of its sub-themes (higher-order themes)."""
    result = {}
    for theme_id in theme_ids:
        pending, seen, codes = [theme_id], set(), []
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            codes += list(db.scalars(select(ThemeCode.code_id).where(ThemeCode.theme_id == current)))
            pending += list(db.scalars(select(Theme.id).where(Theme.parent_id == current)))
        result[theme_id] = list(dict.fromkeys(codes))
    return result


@router.get("/reviews/{review_id}/evidence")
def evidence_chain(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    """RQ → extraction fields (values per study) → coded segments → themes → conclusion; missing links are gaps."""
    final = final_articles(db, review)
    values = _extraction_values(db, [article.id for article in final])
    fields = {field.id: field for field in _fields(db, review)}
    output = []
    for question in db.scalars(select(Question).where(Question.review_id == review.id).order_by(Question.order, Question.id)):
        field_ids = list(db.scalars(select(QuestionField.field_id).where(QuestionField.question_id == question.id)))
        theme_ids = list(db.scalars(select(QuestionTheme.theme_id).where(QuestionTheme.question_id == question.id)))
        theme_codes = _theme_codes(db, theme_ids)
        gaps = []
        if not field_ids:
            gaps.append("Nenhum campo de extração ligado à pergunta.")
        if not theme_ids:
            gaps.append("Nenhum tema ligado à pergunta.")
        if not question.conclusion:
            gaps.append("Conclusão ainda não registrada.")
        studies = []
        for article in final:
            field_values = [{"field": fields[field_id].description, "value": _display(fields[field_id], values[article.id].get(field_id))}
                            for field_id in field_ids if field_id in fields]
            for item in field_values:
                if not item["value"]:
                    gaps.append(f"'{article.title}' sem valor em '{item['field']}'.")
            segments = []
            for theme_id, code_ids in theme_codes.items():
                if not code_ids:
                    continue
                rows = db.execute(
                    select(Segment.id, Segment.text, Segment.page, Code.name)
                    .join(SegmentCode, SegmentCode.segment_id == Segment.id).join(Code, Code.id == SegmentCode.code_id)
                    .where(Segment.article_id == article.id, SegmentCode.is_final.is_(True), SegmentCode.code_id.in_(code_ids))
                ).all()
                theme = db.get(Theme, theme_id)
                segments += [{"segment_id": row[0], "text": row[1], "page": row[2], "code": row[3], "theme": theme.name}
                             for row in rows]
            studies.append({"article_id": article.id, "title": article.title, "fields": field_values, "segments": segments})
        for theme_id, code_ids in theme_codes.items():
            if not any(item["theme"] == db.get(Theme, theme_id).name for study in studies for item in study["segments"]):
                gaps.append(f"Tema '{db.get(Theme, theme_id).name}' sem trechos nos estudos finais.")
        output.append({
            "question_id": question.id, "question": question.question, "conclusion": question.conclusion,
            "field_ids": field_ids, "theme_ids": theme_ids,
            "themes": [db.get(Theme, theme_id).name for theme_id in theme_ids],
            "studies": studies, "gaps": gaps,
        })
    return output
