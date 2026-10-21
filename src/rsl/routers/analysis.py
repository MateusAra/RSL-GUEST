"""Conducting II: quality assessment, data extraction and data analysis."""

from __future__ import annotations

import csv
import io
from datetime import date
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from sqlalchemy import func, select

from ..deps import CurrentUser, DbSession, MemberReview
from ..models import (
    Article,
    DataExtraction,
    DataExtractionField,
    QualityAnswer,
    QualityAssessment,
    QualityQuestion,
    Review,
)
from .conducting import _article

router = APIRouter(tags=["análise"])


def _questions(db: DbSession, review: Review) -> list[QualityQuestion]:
    return list(db.scalars(
        select(QualityQuestion).where(QualityQuestion.review_id == review.id)
        .order_by(QualityQuestion.order, QualityQuestion.id)
    ))


def _answers(db: DbSession, review: Review) -> list[QualityAnswer]:
    return list(db.scalars(
        select(QualityAnswer).where(QualityAnswer.review_id == review.id).order_by(QualityAnswer.weight.desc())
    ))


def _accepted(db: DbSession, review: Review) -> list[Article]:
    return list(db.scalars(
        select(Article).where(Article.review_id == review.id, Article.status == "A").order_by(Article.title)
    ))


def quality_scores(db: DbSession, review: Review) -> dict[int, dict[str, Any]]:
    """Per accepted article: chosen answer per question and the summed score."""
    weights = {answer.id: answer.weight for answer in _answers(db, review)}
    question_ids = {question.id for question in _questions(db, review)}
    result: dict[int, dict[str, Any]] = {
        article.id: {"answers": {}, "score": 0.0, "complete": False} for article in _accepted(db, review)
    }
    if not result:
        return result
    for item in db.scalars(select(QualityAssessment).where(QualityAssessment.article_id.in_(result))):
        if item.question_id in question_ids and item.answer_id is not None:
            entry = result[item.article_id]
            entry["answers"][item.question_id] = item.answer_id
            entry["score"] += weights.get(item.answer_id, 0.0)
    for entry in result.values():
        entry["complete"] = bool(question_ids) and set(entry["answers"]) == question_ids
    return result


def final_articles(db: DbSession, review: Review) -> list[Article]:
    """Accepted articles that passed the quality cutoff (all accepted when there is no checklist)."""
    accepted = _accepted(db, review)
    if not _questions(db, review):
        return accepted
    scores = quality_scores(db, review)
    return [article for article in accepted if scores[article.id]["score"] >= review.quality_cutoff_score]


def _article_brief(article: Article) -> dict[str, Any]:
    return {"id": article.id, "title": article.title, "author": article.author, "year": article.year,
            "journal": article.journal, "source": article.source.name if article.source else None,
            "finished_data_extraction": article.finished_data_extraction}


# ---- 4. quality assessment ------------------------------------------------------

@router.get("/reviews/{review_id}/quality-assessment")
def get_quality_assessment(review: MemberReview, db: DbSession) -> dict[str, Any]:
    questions, answers = _questions(db, review), _answers(db, review)
    scores = quality_scores(db, review)
    max_score = len(questions) * max((answer.weight for answer in answers), default=0.0)
    return {
        "questions": [{"id": item.id, "description": item.description} for item in questions],
        "answers": [{"id": item.id, "description": item.description, "weight": item.weight} for item in answers],
        "max_score": max_score,
        "cutoff_score": review.quality_cutoff_score,
        "articles": [
            {**_article_brief(article), **scores[article.id],
             "answers": {str(key): value for key, value in scores[article.id]["answers"].items()},
             "passed": scores[article.id]["score"] >= review.quality_cutoff_score}
            for article in _accepted(db, review)
        ],
    }


class QualityAnswerIn(BaseModel):
    question_id: int
    answer_id: int | None


@router.put("/reviews/{review_id}/articles/{article_id}/quality")
def save_quality_answer(article_id: int, payload: QualityAnswerIn, review: MemberReview, db: DbSession,
                        user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    if article.status != "A":
        raise HTTPException(status_code=422, detail="Só estudos aceitos passam pela avaliação de qualidade.")
    question = db.get(QualityQuestion, payload.question_id)
    if question is None or question.review_id != review.id:
        raise HTTPException(status_code=404, detail="Pergunta não encontrada nesta revisão.")
    if payload.answer_id is not None:
        answer = db.get(QualityAnswer, payload.answer_id)
        if answer is None or answer.review_id != review.id:
            raise HTTPException(status_code=404, detail="Resposta não encontrada nesta revisão.")
    assessment = db.scalar(select(QualityAssessment).where(
        QualityAssessment.article_id == article.id, QualityAssessment.question_id == question.id))
    if assessment is None:
        assessment = QualityAssessment(article_id=article.id, question_id=question.id)
        db.add(assessment)
    assessment.answer_id, assessment.user_id = payload.answer_id, user.id
    db.commit()
    entry = quality_scores(db, review)[article.id]
    return {"article_id": article.id, "score": entry["score"], "complete": entry["complete"],
            "passed": entry["score"] >= review.quality_cutoff_score}


# ---- 5. data extraction --------------------------------------------------------

def _fields(db: DbSession, review: Review) -> list[DataExtractionField]:
    return list(db.scalars(
        select(DataExtractionField).where(DataExtractionField.review_id == review.id)
        .order_by(DataExtractionField.order, DataExtractionField.id)
    ))


def _extraction_values(db: DbSession, article_ids: list[int]) -> dict[int, dict[int, Any]]:
    values: dict[int, dict[int, Any]] = {article_id: {} for article_id in article_ids}
    if not article_ids:
        return values
    for item in db.scalars(select(DataExtraction).where(DataExtraction.article_id.in_(article_ids))):
        field = db.get(DataExtractionField, item.field_id)
        if field is None:
            continue
        if field.field_type == "M":
            values[item.article_id][item.field_id] = sorted(lookup.id for lookup in item.select_values)
        elif field.field_type == "O":
            values[item.article_id][item.field_id] = item.select_values[0].id if item.select_values else None
        else:
            values[item.article_id][item.field_id] = item.value
    return values


@router.get("/reviews/{review_id}/data-extraction")
def get_data_extraction(review: MemberReview, db: DbSession) -> dict[str, Any]:
    articles = final_articles(db, review)
    values = _extraction_values(db, [article.id for article in articles])
    return {
        "fields": [
            {"id": field.id, "description": field.description, "field_type": field.field_type,
             "lookups": [{"id": lookup.id, "value": lookup.value} for lookup in field.lookups]}
            for field in _fields(db, review)
        ],
        "articles": [
            {**_article_brief(article), "values": {str(key): value for key, value in values[article.id].items()}}
            for article in articles
        ],
    }


class ExtractionValueIn(BaseModel):
    field_id: int
    value: Any = None


def _typed_value(field: DataExtractionField, value: Any) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return ""
    try:
        if field.field_type == "B":
            if text not in {"True", "False"}:
                raise ValueError
            return text
        if field.field_type == "F":
            return str(float(text.replace(",", ".")))
        if field.field_type == "I":
            number = float(text.replace(",", "."))
            if not number.is_integer():
                raise ValueError
            return str(int(number))
        if field.field_type == "D":
            return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        expected = {"B": "sim ou não", "F": "um número real", "I": "um número inteiro", "D": "uma data (AAAA-MM-DD)"}
        raise HTTPException(status_code=422,
                            detail=f"Valor inválido para '{field.description}': informe {expected[field.field_type]}.") from exc
    return text


@router.put("/reviews/{review_id}/articles/{article_id}/extraction")
def save_extraction_value(article_id: int, payload: ExtractionValueIn, review: MemberReview, db: DbSession,
                          user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    if article.id not in {item.id for item in final_articles(db, review)}:
        raise HTTPException(status_code=422, detail="O estudo precisa estar aceito e acima da nota de corte.")
    field = db.get(DataExtractionField, payload.field_id)
    if field is None or field.review_id != review.id:
        raise HTTPException(status_code=404, detail="Campo não encontrado nesta revisão.")
    extraction = db.scalar(select(DataExtraction).where(
        DataExtraction.article_id == article.id, DataExtraction.field_id == field.id))
    if extraction is None:
        extraction = DataExtraction(article_id=article.id, field_id=field.id, value="")
        db.add(extraction)
    extraction.user_id = user.id
    if field.field_type in {"O", "M"}:
        raw = payload.value if isinstance(payload.value, list) else ([] if payload.value in (None, "") else [payload.value])
        try:
            wanted = {int(item) for item in raw}
        except (TypeError, ValueError) as exc:
            raise HTTPException(status_code=422, detail="Valor de seleção inválido.") from exc
        if field.field_type == "O" and len(wanted) > 1:
            raise HTTPException(status_code=422, detail=f"'{field.description}' aceita só um valor.")
        lookups = {lookup.id: lookup for lookup in field.lookups}
        if not wanted <= lookups.keys():
            raise HTTPException(status_code=422, detail="Valor não pertence às opções do campo.")
        extraction.value = ""
        extraction.select_values = [lookups[item] for item in sorted(wanted)]
    else:
        extraction.value = _typed_value(field, payload.value)
        extraction.select_values = []
    db.commit()
    return {"article_id": article.id, "field_id": field.id,
            "value": _extraction_values(db, [article.id])[article.id].get(field.id)}


class ExtractionStatusIn(BaseModel):
    finished: bool


@router.put("/reviews/{review_id}/articles/{article_id}/extraction-status")
def save_extraction_status(article_id: int, payload: ExtractionStatusIn, review: MemberReview,
                           db: DbSession) -> dict[str, Any]:
    article = _article(db, review, article_id)
    article.finished_data_extraction = payload.finished
    db.commit()
    return {"article_id": article.id, "finished_data_extraction": article.finished_data_extraction}


def extraction_rows(db: DbSession, review: Review) -> tuple[list[str], list[list[str]]]:
    fields = _fields(db, review)
    articles = final_articles(db, review)
    values = _extraction_values(db, [article.id for article in articles])
    lookup_values = {lookup.id: lookup.value for field in fields for lookup in field.lookups}
    header = ["Título", "Autores", "Ano", "Fonte", *(field.description for field in fields), "Extração concluída"]
    rows = []
    for article in articles:
        cells = []
        for field in fields:
            value = values[article.id].get(field.id)
            if field.field_type == "M":
                cells.append("; ".join(lookup_values[item] for item in value or []))
            elif field.field_type == "O":
                cells.append(lookup_values.get(value, "") if value else "")
            elif field.field_type == "B":
                cells.append({"True": "Sim", "False": "Não"}.get(value or "", ""))
            else:
                cells.append(value or "")
        rows.append([article.title, article.author, article.year, article.source.name if article.source else "",
                     *cells, "Sim" if article.finished_data_extraction else "Não"])
    return header, rows


@router.get("/reviews/{review_id}/data-extraction/export")
def export_data_extraction(review: MemberReview, db: DbSession) -> Response:
    header, rows = extraction_rows(db, review)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)
    return Response(buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{review.name}-extracao.csv"'})


# ---- 6. data analysis ----------------------------------------------------------

def analysis_data(db: DbSession, review: Review) -> dict[str, Any]:
    rows = db.execute(
        select(Article.source_id, Article.status, func.count())
        .where(Article.review_id == review.id)
        .group_by(Article.source_id, Article.status)
    ).all()
    per_source = {source.id: {"source": source.name, "total": 0, "accepted": 0} for source in review.sources}
    status_totals = {"U": 0, "A": 0, "R": 0, "D": 0}
    for source_id, status, count in rows:
        status_totals[status] += count
        if source_id in per_source:
            per_source[source_id]["total"] += count
            if status == "A":
                per_source[source_id]["accepted"] += count
    years: dict[str, int] = {}
    final = final_articles(db, review)
    for article in final:
        key = article.year or "Sem ano"
        years[key] = years.get(key, 0) + 1
    return {
        "per_source": list(per_source.values()),
        "status_totals": status_totals,
        "final_per_year": [{"year": year, "count": years[year]} for year in sorted(years)],
        "final_total": len(final),
    }


@router.get("/reviews/{review_id}/analysis")
def get_analysis(review: MemberReview, db: DbSession) -> dict[str, Any]:
    return analysis_data(db, review)
