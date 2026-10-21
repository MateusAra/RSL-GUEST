from __future__ import annotations

import re
from typing import Any, Literal, TypeVar

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import delete, func, select

from ..db import Base
from ..deps import CurrentUser, DbSession, MemberReview, log_activity
from ..models import (
    DataExtractionField,
    DataExtractionLookup,
    Keyword,
    QualityAnswer,
    QualityQuestion,
    Question,
    Review,
    SearchSession,
    SelectionCriteria,
    Source,
)
from ..search import CUSTOM_CONNECTORS

router = APIRouter(tags=["planejamento"])

FIELD_TYPES = {
    "B": "Booleano",
    "S": "Texto",
    "F": "Número real",
    "I": "Número inteiro",
    "D": "Data",
    "O": "Seleção única",
    "M": "Seleção múltipla",
}
SELECT_TYPES = {"O", "M"}
PICOC_KEYWORD_FIELDS = {"population": "P", "intervention": "I", "comparison": "C", "outcome": "O"}
SUGGESTED_ANSWERS = (("Sim", 1.0), ("Parcialmente", 0.5), ("Não", 0.0))

ModelT = TypeVar("ModelT", bound=Base)


def _owned(db: DbSession, model: type[ModelT], object_id: int, review: Review) -> ModelT:
    instance = db.get(model, object_id)
    if instance is None or getattr(instance, "review_id", None) != review.id:
        raise HTTPException(status_code=404, detail="Item não encontrado nesta revisão.")
    return instance


def _clean(text: str, label: str) -> str:
    text = text.strip()
    if not text:
        raise HTTPException(status_code=422, detail=f"Informe {label}.")
    return text


def _next_order(db: DbSession, model: type[Base], review: Review) -> int:
    return int(db.scalar(select(func.coalesce(func.max(model.order), -1)).where(model.review_id == review.id))) + 1


def _reorder(db: DbSession, model: type[Base], review: Review, ids: list[int]) -> None:
    items = {item.id: item for item in db.scalars(select(model).where(model.review_id == review.id)).all()}
    if sorted(ids) != sorted(items):
        raise HTTPException(status_code=422, detail="A nova ordem precisa conter todos os itens.")
    for position, item_id in enumerate(ids):
        items[item_id].order = position


def _max_score(db: DbSession, review: Review) -> float:
    questions = db.scalar(select(func.count()).select_from(QualityQuestion).where(QualityQuestion.review_id == review.id))
    best = db.scalar(select(func.max(QualityAnswer.weight)).where(QualityAnswer.review_id == review.id))
    return float((questions or 0) * (best or 0))


# ---- serialization ---------------------------------------------------------

def _keyword_out(keyword: Keyword, synonyms: list[Keyword]) -> dict[str, Any]:
    return {
        "id": keyword.id,
        "description": keyword.description,
        "related_to": keyword.related_to,
        "synonyms": [{"id": item.id, "description": item.description} for item in synonyms],
    }


def _field_out(field: DataExtractionField) -> dict[str, Any]:
    return {
        "id": field.id,
        "description": field.description,
        "field_type": field.field_type,
        "field_type_label": FIELD_TYPES[field.field_type],
        "order": field.order,
        "lookups": [
            {"id": lookup.id, "value": lookup.value}
            for lookup in sorted(field.lookups, key=lambda item: item.value.casefold())
        ],
    }


def planning_out(db: DbSession, review: Review) -> dict[str, Any]:
    keywords = db.scalars(select(Keyword).where(Keyword.review_id == review.id).order_by(func.lower(Keyword.description))).all()
    synonyms: dict[int, list[Keyword]] = {}
    for keyword in keywords:
        if keyword.synonym_of_id is not None:
            synonyms.setdefault(keyword.synonym_of_id, []).append(keyword)
    base_string = db.scalar(
        select(SearchSession).where(SearchSession.review_id == review.id, SearchSession.source_id.is_(None))
    )
    criteria = db.scalars(
        select(SelectionCriteria)
        .where(SelectionCriteria.review_id == review.id)
        .order_by(func.lower(SelectionCriteria.description))
    ).all()
    return {
        "objective": review.objective,
        "picoc": {
            "population": review.population,
            "intervention": review.intervention,
            "comparison": review.comparison,
            "outcome": review.outcome,
            "context": review.context,
        },
        "questions": [
            {"id": item.id, "question": item.question, "order": item.order}
            for item in db.scalars(select(Question).where(Question.review_id == review.id).order_by(Question.order, Question.id))
        ],
        "keywords": [_keyword_out(item, synonyms.get(item.id, [])) for item in keywords if item.synonym_of_id is None],
        "search_string": "" if base_string is None else base_string.search_string,
        "sources": [source_out(source) for source in review.sources],
        "inclusion_criteria": [{"id": item.id, "description": item.description} for item in criteria if item.criteria_type == "I"],
        "exclusion_criteria": [{"id": item.id, "description": item.description} for item in criteria if item.criteria_type == "E"],
        "quality_questions": [
            {"id": item.id, "description": item.description, "order": item.order}
            for item in db.scalars(
                select(QualityQuestion).where(QualityQuestion.review_id == review.id)
                .order_by(QualityQuestion.order, QualityQuestion.id)
            )
        ],
        "quality_answers": [
            {"id": item.id, "description": item.description, "weight": item.weight}
            for item in db.scalars(
                select(QualityAnswer).where(QualityAnswer.review_id == review.id).order_by(QualityAnswer.weight.desc())
            )
        ],
        "quality_max_score": _max_score(db, review),
        "quality_cutoff_score": review.quality_cutoff_score,
        "data_extraction_fields": [
            _field_out(item)
            for item in db.scalars(
                select(DataExtractionField).where(DataExtractionField.review_id == review.id)
                .order_by(DataExtractionField.order, DataExtractionField.id)
            )
        ],
        "field_types": FIELD_TYPES,
    }


@router.get("/reviews/{review_id}/planning")
def get_planning(review: MemberReview, db: DbSession) -> dict[str, Any]:
    return planning_out(db, review)


# ---- objectives and PICOC --------------------------------------------------

class ObjectiveIn(BaseModel):
    objective: str = Field(max_length=1000)


class PicocIn(BaseModel):
    population: str = Field(default="", max_length=200)
    intervention: str = Field(default="", max_length=200)
    comparison: str = Field(default="", max_length=200)
    outcome: str = Field(default="", max_length=200)
    context: str = Field(default="", max_length=200)


@router.put("/reviews/{review_id}/objective")
def save_objective(payload: ObjectiveIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    review.objective = payload.objective.strip()
    log_activity(db, user, "editou os objetivos", review)
    db.commit()
    return {"objective": review.objective}


@router.put("/reviews/{review_id}/picoc")
def save_picoc(payload: PicocIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    for name, value in payload.model_dump().items():
        setattr(review, name, value.strip())
    log_activity(db, user, "editou o PICOC", review)
    db.commit()
    return planning_out(db, review)["picoc"]


# ---- research questions ----------------------------------------------------

class QuestionIn(BaseModel):
    question: str = Field(max_length=500)


class OrderIn(BaseModel):
    ids: list[int]


@router.post("/reviews/{review_id}/questions", status_code=201)
def add_question(payload: QuestionIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    question = Question(review_id=review.id, question=_clean(payload.question, "a pergunta"),
                        order=_next_order(db, Question, review))
    db.add(question)
    log_activity(db, user, "adicionou a pergunta", review, question.question)
    db.commit()
    return {"id": question.id, "question": question.question, "order": question.order}


@router.patch("/reviews/{review_id}/questions/{question_id}")
def edit_question(question_id: int, payload: QuestionIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    question = _owned(db, Question, question_id, review)
    question.question = _clean(payload.question, "a pergunta")
    db.commit()
    return {"id": question.id, "question": question.question, "order": question.order}


@router.delete("/reviews/{review_id}/questions/{question_id}", status_code=204)
def remove_question(question_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_owned(db, Question, question_id, review))
    db.commit()
    return Response(status_code=204)


@router.put("/reviews/{review_id}/questions/order", status_code=204)
def order_questions(payload: OrderIn, review: MemberReview, db: DbSession) -> Response:
    _reorder(db, Question, review, payload.ids)
    db.commit()
    return Response(status_code=204)


# ---- selection criteria ----------------------------------------------------

class CriteriaIn(BaseModel):
    criteria_type: Literal["I", "E"]
    description: str = Field(max_length=200)


@router.post("/reviews/{review_id}/criteria", status_code=201)
def add_criteria(payload: CriteriaIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    criteria = SelectionCriteria(review_id=review.id, criteria_type=payload.criteria_type,
                                 description=_clean(payload.description, "o critério"))
    db.add(criteria)
    log_activity(db, user, "adicionou o critério", review, criteria.description)
    db.commit()
    return {"id": criteria.id, "criteria_type": criteria.criteria_type, "description": criteria.description}


@router.delete("/reviews/{review_id}/criteria/{criteria_id}", status_code=204)
def remove_criteria(criteria_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_owned(db, SelectionCriteria, criteria_id, review))
    db.commit()
    return Response(status_code=204)


# ---- keywords and synonyms -------------------------------------------------

class KeywordIn(BaseModel):
    description: str = Field(max_length=200)
    related_to: Literal["", "P", "I", "C", "O"] = ""
    synonym_of_id: int | None = None


class KeywordUpdate(BaseModel):
    description: str | None = Field(default=None, max_length=200)
    related_to: Literal["", "P", "I", "C", "O"] | None = None


@router.post("/reviews/{review_id}/keywords", status_code=201)
def add_keyword(payload: KeywordIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    if payload.synonym_of_id is not None:
        parent = _owned(db, Keyword, payload.synonym_of_id, review)
        if parent.synonym_of_id is not None:
            raise HTTPException(status_code=422, detail="Sinônimos se ligam a uma palavra-chave, não a outro sinônimo.")
    keyword = Keyword(review_id=review.id, description=_clean(payload.description, "a palavra-chave"),
                      related_to=payload.related_to, synonym_of_id=payload.synonym_of_id)
    db.add(keyword)
    db.commit()
    return {"id": keyword.id, "description": keyword.description, "related_to": keyword.related_to,
            "synonym_of_id": keyword.synonym_of_id}


@router.patch("/reviews/{review_id}/keywords/{keyword_id}")
def edit_keyword(keyword_id: int, payload: KeywordUpdate, review: MemberReview, db: DbSession) -> dict[str, Any]:
    keyword = _owned(db, Keyword, keyword_id, review)
    if payload.description is not None:
        keyword.description = _clean(payload.description, "a palavra-chave")
    if payload.related_to is not None:
        keyword.related_to = payload.related_to
    db.commit()
    return {"id": keyword.id, "description": keyword.description, "related_to": keyword.related_to,
            "synonym_of_id": keyword.synonym_of_id}


@router.delete("/reviews/{review_id}/keywords/{keyword_id}", status_code=204)
def remove_keyword(keyword_id: int, review: MemberReview, db: DbSession) -> Response:
    keyword = _owned(db, Keyword, keyword_id, review)
    db.execute(delete(Keyword).where(Keyword.synonym_of_id == keyword.id))
    db.delete(keyword)
    db.commit()
    return Response(status_code=204)


@router.post("/reviews/{review_id}/keywords/import-picoc")
def import_picoc_keywords(review: MemberReview, db: DbSession) -> dict[str, Any]:
    """Split the P, I, C and O fields by comma into keywords (as Parsifal's "Import PICOC Keywords")."""
    existing = {
        keyword.description.casefold()
        for keyword in db.scalars(select(Keyword).where(Keyword.review_id == review.id))
    }
    created = 0
    for field, related_to in PICOC_KEYWORD_FIELDS.items():
        for term in (part.strip() for part in getattr(review, field).split(",")):
            if term and term.casefold() not in existing:
                db.add(Keyword(review_id=review.id, description=term[:200], related_to=related_to))
                existing.add(term.casefold())
                created += 1
    db.commit()
    return {"created": created, **{"keywords": planning_out(db, review)["keywords"]}}


# ---- search string ---------------------------------------------------------

class SearchStringIn(BaseModel):
    search_string: str = Field(max_length=10000)


def _quote(term: str) -> str:
    return f'"{term}"' if re.search(r"\s", term) else term


def generate_search_string(db: DbSession, review: Review) -> str:
    keywords = planning_out(db, review)["keywords"]
    groups = []
    for keyword in keywords:
        terms = [keyword["description"], *(synonym["description"] for synonym in keyword["synonyms"])]
        group = " OR ".join(_quote(term) for term in terms)
        groups.append(f"({group})" if len(terms) > 1 else group)
    return " AND ".join(groups)


@router.post("/reviews/{review_id}/search-string/generate")
def suggest_search_string(review: MemberReview, db: DbSession) -> dict[str, str]:
    return {"search_string": generate_search_string(db, review)}


@router.put("/reviews/{review_id}/search-string")
def save_search_string(payload: SearchStringIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    session = db.scalar(
        select(SearchSession).where(SearchSession.review_id == review.id, SearchSession.source_id.is_(None))
    )
    if session is None:
        session = SearchSession(review_id=review.id, source_id=None, search_string="", version=0)
        db.add(session)
    session.search_string = payload.search_string.strip()
    session.version += 1
    log_activity(db, user, "salvou a string de busca", review)
    db.commit()
    return {"search_string": session.search_string, "version": session.version}


# ---- sources ---------------------------------------------------------------

class SourceIn(BaseModel):
    source_id: int | None = None
    name: str = Field(default="", max_length=100)
    url: str = Field(default="", max_length=200)
    connector: str | None = None


def source_out(source: Source) -> dict[str, Any]:
    return {"id": source.id, "name": source.name, "url": source.url, "is_default": source.is_default,
            "connector": source.connector}


def _custom_connector(value: str | None) -> str | None:
    if value and value not in CUSTOM_CONNECTORS:
        raise HTTPException(status_code=422, detail="Fontes próprias só podem usar a busca automática do OpenAlex ou do Semantic Scholar.")
    return value or None


@router.get("/reviews/{review_id}/sources/suggested")
def suggested_sources(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    current = {source.id for source in review.sources}
    return [
        source_out(source)
        for source in db.scalars(select(Source).where(Source.is_default.is_(True)).order_by(Source.name))
        if source.id not in current
    ]


@router.post("/reviews/{review_id}/sources", status_code=201)
def add_source(payload: SourceIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    if payload.source_id is not None:
        source = db.get(Source, payload.source_id)
        if source is None or not source.is_default:
            raise HTTPException(status_code=404, detail="Biblioteca não encontrada.")
    else:
        source = Source(name=_clean(payload.name, "o nome da fonte"), url=payload.url.strip(), is_default=False,
                        connector=_custom_connector(payload.connector))
        db.add(source)
        db.flush()
    if any(item.id == source.id for item in review.sources):
        raise HTTPException(status_code=409, detail="Esta fonte já faz parte da revisão.")
    review.sources.append(source)
    log_activity(db, user, "adicionou a fonte", review, source.name)
    db.commit()
    return source_out(source)


@router.patch("/reviews/{review_id}/sources/{source_id}")
def edit_source(source_id: int, payload: SourceIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    source = next((item for item in review.sources if item.id == source_id), None)
    if source is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada nesta revisão.")
    if source.is_default:
        raise HTTPException(status_code=422, detail="As bibliotecas sugeridas não podem ser editadas.")
    source.name, source.url = _clean(payload.name, "o nome da fonte"), payload.url.strip()
    source.connector = _custom_connector(payload.connector)
    db.commit()
    return source_out(source)


@router.delete("/reviews/{review_id}/sources/{source_id}", status_code=204)
def remove_source(source_id: int, review: MemberReview, db: DbSession) -> Response:
    if not any(item.id == source_id for item in review.sources):
        raise HTTPException(status_code=404, detail="Fonte não encontrada nesta revisão.")
    review.sources = [item for item in review.sources if item.id != source_id]
    db.commit()
    return Response(status_code=204)


# ---- quality assessment checklist -----------------------------------------

class QualityQuestionIn(BaseModel):
    description: str = Field(max_length=255)


class QualityAnswerIn(BaseModel):
    description: str = Field(max_length=255)
    weight: float


class CutoffIn(BaseModel):
    quality_cutoff_score: float = Field(ge=0)


@router.post("/reviews/{review_id}/quality-questions", status_code=201)
def add_quality_question(payload: QualityQuestionIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    question = QualityQuestion(review_id=review.id, description=_clean(payload.description, "a pergunta"),
                               order=_next_order(db, QualityQuestion, review))
    db.add(question)
    db.commit()
    return {"id": question.id, "description": question.description, "order": question.order}


@router.patch("/reviews/{review_id}/quality-questions/{question_id}")
def edit_quality_question(question_id: int, payload: QualityQuestionIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    question = _owned(db, QualityQuestion, question_id, review)
    question.description = _clean(payload.description, "a pergunta")
    db.commit()
    return {"id": question.id, "description": question.description, "order": question.order}


@router.delete("/reviews/{review_id}/quality-questions/{question_id}", status_code=204)
def remove_quality_question(question_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_owned(db, QualityQuestion, question_id, review))
    db.commit()
    return Response(status_code=204)


@router.put("/reviews/{review_id}/quality-questions/order", status_code=204)
def order_quality_questions(payload: OrderIn, review: MemberReview, db: DbSession) -> Response:
    _reorder(db, QualityQuestion, review, payload.ids)
    db.commit()
    return Response(status_code=204)


@router.post("/reviews/{review_id}/quality-answers", status_code=201)
def add_quality_answer(payload: QualityAnswerIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    answer = QualityAnswer(review_id=review.id, description=_clean(payload.description, "a resposta"),
                           weight=payload.weight)
    db.add(answer)
    db.commit()
    return {"id": answer.id, "description": answer.description, "weight": answer.weight}


@router.post("/reviews/{review_id}/quality-answers/suggested")
def add_suggested_answers(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    existing = {
        answer.description.casefold()
        for answer in db.scalars(select(QualityAnswer).where(QualityAnswer.review_id == review.id))
    }
    for description, weight in SUGGESTED_ANSWERS:
        if description.casefold() not in existing:
            db.add(QualityAnswer(review_id=review.id, description=description, weight=weight))
    db.commit()
    return planning_out(db, review)["quality_answers"]


@router.patch("/reviews/{review_id}/quality-answers/{answer_id}")
def edit_quality_answer(answer_id: int, payload: QualityAnswerIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    answer = _owned(db, QualityAnswer, answer_id, review)
    answer.description, answer.weight = _clean(payload.description, "a resposta"), payload.weight
    db.commit()
    return {"id": answer.id, "description": answer.description, "weight": answer.weight}


@router.delete("/reviews/{review_id}/quality-answers/{answer_id}", status_code=204)
def remove_quality_answer(answer_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_owned(db, QualityAnswer, answer_id, review))
    db.commit()
    return Response(status_code=204)


@router.put("/reviews/{review_id}/quality-cutoff")
def save_cutoff(payload: CutoffIn, review: MemberReview, db: DbSession) -> dict[str, float]:
    max_score = _max_score(db, review)
    if max_score and payload.quality_cutoff_score > max_score:
        raise HTTPException(status_code=422, detail=f"O corte não pode passar da pontuação máxima ({max_score:g}).")
    review.quality_cutoff_score = payload.quality_cutoff_score
    db.commit()
    return {"quality_cutoff_score": review.quality_cutoff_score, "quality_max_score": max_score}


# ---- data extraction form --------------------------------------------------

class ExtractionFieldIn(BaseModel):
    description: str = Field(max_length=255)
    field_type: Literal["B", "S", "F", "I", "D", "O", "M"]
    lookups: list[str] = Field(default_factory=list)


def _apply_field(field: DataExtractionField, payload: ExtractionFieldIn) -> None:
    field.description = _clean(payload.description, "a descrição do campo")
    field.field_type = payload.field_type
    values = list(dict.fromkeys(value.strip() for value in payload.lookups if value.strip()))
    if payload.field_type in SELECT_TYPES and not values:
        raise HTTPException(status_code=422, detail="Campos de seleção precisam de pelo menos um valor.")
    if payload.field_type not in SELECT_TYPES:
        values = []
    current = {lookup.value: lookup for lookup in field.lookups}
    field.lookups = [current.get(value) or DataExtractionLookup(value=value[:1000]) for value in values]


@router.post("/reviews/{review_id}/extraction-fields", status_code=201)
def add_extraction_field(payload: ExtractionFieldIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    field = DataExtractionField(review_id=review.id, description="", field_type=payload.field_type,
                                order=_next_order(db, DataExtractionField, review))
    _apply_field(field, payload)
    db.add(field)
    db.commit()
    return _field_out(field)


@router.patch("/reviews/{review_id}/extraction-fields/{field_id}")
def edit_extraction_field(field_id: int, payload: ExtractionFieldIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    field = _owned(db, DataExtractionField, field_id, review)
    _apply_field(field, payload)
    db.commit()
    return _field_out(field)


@router.delete("/reviews/{review_id}/extraction-fields/{field_id}", status_code=204)
def remove_extraction_field(field_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_owned(db, DataExtractionField, field_id, review))
    db.commit()
    return Response(status_code=204)


@router.put("/reviews/{review_id}/extraction-fields/order", status_code=204)
def order_extraction_fields(payload: OrderIn, review: MemberReview, db: DbSession) -> Response:
    _reorder(db, DataExtractionField, review, payload.ids)
    db.commit()
    return Response(status_code=204)
