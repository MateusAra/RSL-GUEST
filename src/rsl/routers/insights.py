"""Analyses (spec 008 adapted): bibliometrics, extraction fields, hypotheses, sensitivity and snapshots."""

from __future__ import annotations

import re
from collections import Counter
from itertools import combinations
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from ..deps import CurrentUser, DbSession, MemberReview, OwnerReview, log_activity
from ..importers import DOCUMENT_CATEGORIES, document_category
from ..models import (
    VERDICTS,
    AnalysisSettings,
    AnalysisSnapshot,
    Article,
    DataExtractionField,
    Hypothesis,
    HypothesisVerdict,
    Review,
)
from .analysis import _answers, _extraction_values, _fields, _questions, final_articles, quality_scores
from .conducting import _article

router = APIRouter(tags=["análises"])

TOP = 15


# ---- settings and filters ---------------------------------------------------------

def _settings(db: DbSession, review: Review) -> AnalysisSettings:
    settings = db.get(AnalysisSettings, review.id)
    if settings is None:
        settings = AnalysisSettings(review_id=review.id)
        db.add(settings)
        db.flush()
    return settings


def _settings_out(settings: AnalysisSettings) -> dict[str, float]:
    return {"high_min_pct": settings.high_min_pct, "high_weight": settings.high_weight,
            "moderate_min_pct": settings.moderate_min_pct, "moderate_weight": settings.moderate_weight,
            "author_concentration_pct": settings.author_concentration_pct}


class SettingsIn(BaseModel):
    high_min_pct: float = Field(ge=0, le=100)
    high_weight: float = Field(gt=0, le=1)
    moderate_min_pct: float = Field(ge=0, le=100)
    moderate_weight: float = Field(ge=0, le=1)
    author_concentration_pct: float = Field(gt=0, le=100)


@router.get("/reviews/{review_id}/analysis-settings")
def get_settings(review: MemberReview, db: DbSession) -> dict[str, float]:
    settings = _settings(db, review)
    db.commit()
    return _settings_out(settings)


@router.put("/reviews/{review_id}/analysis-settings")
def save_settings(payload: SettingsIn, review: OwnerReview, db: DbSession, user: CurrentUser) -> dict[str, float]:
    if payload.moderate_min_pct > payload.high_min_pct:
        raise HTTPException(status_code=422, detail="A faixa moderada precisa começar abaixo da faixa alta.")
    settings = _settings(db, review)
    for name, value in payload.model_dump().items():
        setattr(settings, name, value)
    log_activity(db, user, "alterou a ponderação das análises de", review)
    db.commit()
    return _settings_out(settings)


class Filters(BaseModel):
    min_quality_pct: float | None = None
    year_from: int | None = None
    year_to: int | None = None
    source_ids: list[int] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)

    def active(self) -> bool:
        return any((self.min_quality_pct is not None, self.year_from, self.year_to, self.source_ids, self.categories))


def filters_from_query(
    min_quality_pct: float | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    source_ids: str = "",
    categories: str = "",
) -> Filters:
    return Filters(
        min_quality_pct=min_quality_pct, year_from=year_from, year_to=year_to,
        source_ids=[int(item) for item in source_ids.split(",") if item.strip().isdigit()],
        categories=[item for item in categories.split(",") if item in DOCUMENT_CATEGORIES],
    )


def _quality_pct(db: DbSession, review: Review) -> dict[int, float | None]:
    questions, answers = _questions(db, review), _answers(db, review)
    max_score = len(questions) * max((answer.weight for answer in answers), default=0.0)
    scores = quality_scores(db, review)
    return {article_id: (entry["score"] / max_score * 100 if max_score else None) for article_id, entry in scores.items()}


def _band(pct: float | None, settings: AnalysisSettings) -> tuple[str, float]:
    if pct is None:
        return "none", 1.0
    if pct >= settings.high_min_pct:
        return "high", settings.high_weight
    if pct >= settings.moderate_min_pct:
        return "moderate", settings.moderate_weight
    return "low", 0.0


def _year(article: Article) -> int | None:
    return int(article.year) if article.year.isdigit() else None


def _corpus(db: DbSession, review: Review, filters: Filters) -> tuple[list[Article], dict[int, float | None]]:
    """Final selection after the sensitivity filters. Filters never change data (spec 008, rule 6)."""
    quality = _quality_pct(db, review)
    corpus = []
    for article in final_articles(db, review):
        year, pct = _year(article), quality.get(article.id)
        if filters.min_quality_pct is not None and (pct is None or pct < filters.min_quality_pct):
            continue
        if filters.year_from and (year is None or year < filters.year_from):
            continue
        if filters.year_to and (year is None or year > filters.year_to):
            continue
        if filters.source_ids and article.source_id not in filters.source_ids:
            continue
        if filters.categories and document_category(article.document_type, article.journal, article.doi) not in filters.categories:
            continue
        corpus.append(article)
    return corpus, quality


# ---- computations ----------------------------------------------------------------------

def _split(text: str, pattern: str) -> list[str]:
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


def _authors(article: Article) -> list[str]:
    return list(dict.fromkeys(_split(article.author, r"\s+and\s+|;")))


def _ranked(counter: Counter, limit: int = TOP) -> list[dict[str, Any]]:
    return [{"label": label, "count": count} for label, count in sorted(counter.items(), key=lambda item: (-item[1], str(item[0])))[:limit]]


def bibliometrics(corpus: list[Article], settings: AnalysisSettings) -> dict[str, Any]:
    years = Counter(article.year or "Sem ano" for article in corpus)
    keywords = Counter(
        keyword.casefold()
        for article in corpus
        for keyword in dict.fromkeys(_split(f"{article.keywords};{article.author_keywords}", r"[;,]")).keys()
    )
    authors = Counter(author for article in corpus for author in _authors(article))
    pairs = Counter(" & ".join(pair) for article in corpus for pair in combinations(sorted(_authors(article)), 2))
    total = len(corpus)
    concentrated = [
        {"author": author, "count": count, "pct": round(count / total * 100, 1)}
        for author, count in authors.most_common()
        if total and count / total * 100 > settings.author_concentration_pct and count > 1
    ]
    return {
        "per_year": [{"label": year, "count": years[year]} for year in sorted(years)],
        "per_source": _ranked(Counter(article.source.name if article.source else "Sem fonte" for article in corpus)),
        "per_venue": _ranked(Counter(article.journal or "Sem veículo" for article in corpus)),
        "per_category": _ranked(Counter(
            DOCUMENT_CATEGORIES[document_category(article.document_type, article.journal, article.doi)] for article in corpus)),
        "top_keywords": _ranked(keywords, 20),
        "top_authors": _ranked(authors),
        "coauthor_pairs": _ranked(pairs),
        "author_concentration": concentrated,
    }


def _field_label(field: DataExtractionField, value: Any) -> list[str]:
    lookups = {lookup.id: lookup.value for lookup in field.lookups}
    if field.field_type == "M":
        return [lookups[item] for item in value or [] if item in lookups]
    if field.field_type == "O":
        return [lookups[value]] if value in lookups else []
    if field.field_type == "B":
        return [{"True": "Sim", "False": "Não"}[value]] if value in {"True", "False"} else []
    return []


def field_frequencies(db: DbSession, review: Review, corpus: list[Article]) -> list[dict[str, Any]]:
    values = _extraction_values(db, [article.id for article in corpus])
    output = []
    for field in _fields(db, review):
        if field.field_type not in {"B", "O", "M"}:
            continue
        counter = Counter(label for article in corpus for label in _field_label(field, values[article.id].get(field.id)))
        unanswered = sum(not _field_label(field, values[article.id].get(field.id)) for article in corpus)
        output.append({"field_id": field.id, "field": field.description, "field_type": field.field_type,
                       "values": _ranked(counter, 50), "unanswered": unanswered})
    return output


def hypotheses_synthesis(db: DbSession, review: Review, corpus: list[Article], quality: dict[int, float | None],
                         settings: AnalysisSettings) -> list[dict[str, Any]]:
    hypotheses = db.scalars(select(Hypothesis).where(Hypothesis.review_id == review.id)
                            .order_by(Hypothesis.order, Hypothesis.id)).all()
    ids = [article.id for article in corpus]
    verdicts = {(item.hypothesis_id, item.article_id): item.verdict
                for item in db.scalars(select(HypothesisVerdict).where(HypothesisVerdict.article_id.in_(ids)))} if ids else {}
    output = []
    for hypothesis in hypotheses:
        counts = {key: 0 for key in VERDICTS}
        weighted = {key: 0.0 for key in VERDICTS}
        moderate = {key: 0 for key in VERDICTS}
        missing = 0
        for article in corpus:
            verdict = verdicts.get((hypothesis.id, article.id))
            if verdict is None:
                missing += 1
                continue
            band, weight = _band(quality.get(article.id), settings)
            counts[verdict] += 1
            weighted[verdict] += weight
            if band == "moderate":
                moderate[verdict] += 1
        rated = sum(counts.values())
        weight_total = sum(weighted.values())
        output.append({
            "id": hypothesis.id, "code": hypothesis.code, "statement": hypothesis.statement,
            "rated": rated, "missing": missing,
            # "Inconclusive" stays in the denominator (spec 008, rule 7).
            "verdicts": [
                {"verdict": key, "label": label, "count": counts[key],
                 "pct": round(counts[key] / rated * 100, 1) if rated else 0.0,
                 "weighted": round(weighted[key], 3),
                 "weighted_pct": round(weighted[key] / weight_total * 100, 1) if weight_total else 0.0,
                 "moderate_band": moderate[key]}
                for key, label in VERDICTS.items()
            ],
        })
    return output


def compute(db: DbSession, review: Review, filters: Filters) -> dict[str, Any]:
    settings = _settings(db, review)
    corpus, quality = _corpus(db, review, filters)
    bands = Counter(_band(quality.get(article.id), settings)[0] for article in corpus)
    result: dict[str, Any] = {
        "filters": filters.model_dump(),
        "settings": _settings_out(settings),
        "corpus": len(corpus),
        "final_total": len(final_articles(db, review)),
        "quality_bands": {band: bands.get(band, 0) for band in ("high", "moderate", "low", "none")},
        "bibliometrics": bibliometrics(corpus, settings),
        "fields": field_frequencies(db, review, corpus),
        "hypotheses": hypotheses_synthesis(db, review, corpus, quality, settings),
    }
    if filters.active():
        full, full_quality = _corpus(db, review, Filters())
        result["comparison"] = {"corpus": len(full),
                                "hypotheses": hypotheses_synthesis(db, review, full, full_quality, settings)}
    return result


@router.get("/reviews/{review_id}/insights")
def get_insights(
    review: MemberReview,
    db: DbSession,
    min_quality_pct: float | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    source_ids: str = "",
    categories: str = "",
) -> dict[str, Any]:
    result = compute(db, review, filters_from_query(min_quality_pct, year_from, year_to, source_ids, categories))
    db.commit()
    return result


@router.get("/reviews/{review_id}/insights/crosstab")
def crosstab(
    review: MemberReview,
    db: DbSession,
    field_a: int = Query(...),
    field_b: int = Query(...),
    min_quality_pct: float | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    source_ids: str = "",
    categories: str = "",
) -> dict[str, Any]:
    fields = {field.id: field for field in _fields(db, review) if field.field_type in {"B", "O", "M"}}
    if field_a not in fields or field_b not in fields or field_a == field_b:
        raise HTTPException(status_code=422, detail="Escolha dois campos diferentes do tipo seleção ou booleano.")
    corpus, _ = _corpus(db, review, filters_from_query(min_quality_pct, year_from, year_to, source_ids, categories))
    values = _extraction_values(db, [article.id for article in corpus])
    cells: Counter = Counter()
    for article in corpus:
        for first in _field_label(fields[field_a], values[article.id].get(field_a)):
            for second in _field_label(fields[field_b], values[article.id].get(field_b)):
                cells[(first, second)] += 1
    rows = sorted({key[0] for key in cells})
    columns = sorted({key[1] for key in cells})
    return {"field_a": fields[field_a].description, "field_b": fields[field_b].description, "rows": rows,
            "columns": columns, "matrix": [[cells[(row, column)] for column in columns] for row in rows],
            "corpus": len(corpus)}


# ---- hypotheses and verdicts ------------------------------------------------------------

class HypothesisIn(BaseModel):
    code: str = Field(max_length=20)
    statement: str
    independent_variables: str = ""
    dependent_variables: str = ""
    operational_criteria: str = ""


def _hypothesis(db: DbSession, review: Review, hypothesis_id: int) -> Hypothesis:
    hypothesis = db.get(Hypothesis, hypothesis_id)
    if hypothesis is None or hypothesis.review_id != review.id:
        raise HTTPException(status_code=404, detail="Hipótese não encontrada nesta revisão.")
    return hypothesis


def _hypothesis_out(hypothesis: Hypothesis) -> dict[str, Any]:
    return {"id": hypothesis.id, "code": hypothesis.code, "statement": hypothesis.statement,
            "independent_variables": hypothesis.independent_variables,
            "dependent_variables": hypothesis.dependent_variables,
            "operational_criteria": hypothesis.operational_criteria, "order": hypothesis.order}


def _clean_hypothesis(payload: HypothesisIn) -> dict[str, str]:
    data = {key: value.strip() for key, value in payload.model_dump().items()}
    if not data["code"] or not data["statement"]:
        raise HTTPException(status_code=422, detail="Informe o identificador e o enunciado da hipótese.")
    return data


@router.get("/reviews/{review_id}/hypotheses")
def list_hypotheses(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    return [_hypothesis_out(item) for item in db.scalars(
        select(Hypothesis).where(Hypothesis.review_id == review.id).order_by(Hypothesis.order, Hypothesis.id))]


@router.post("/reviews/{review_id}/hypotheses", status_code=201)
def create_hypothesis(payload: HypothesisIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    order = int(db.scalar(select(func.coalesce(func.max(Hypothesis.order), -1)).where(Hypothesis.review_id == review.id))) + 1
    hypothesis = Hypothesis(review_id=review.id, order=order, **_clean_hypothesis(payload))
    db.add(hypothesis)
    log_activity(db, user, "adicionou a hipótese", review, hypothesis.code)
    db.commit()
    return _hypothesis_out(hypothesis)


@router.patch("/reviews/{review_id}/hypotheses/{hypothesis_id}")
def update_hypothesis(hypothesis_id: int, payload: HypothesisIn, review: MemberReview, db: DbSession) -> dict[str, Any]:
    hypothesis = _hypothesis(db, review, hypothesis_id)
    for key, value in _clean_hypothesis(payload).items():
        setattr(hypothesis, key, value)
    db.commit()
    return _hypothesis_out(hypothesis)


@router.delete("/reviews/{review_id}/hypotheses/{hypothesis_id}", status_code=204)
def delete_hypothesis(hypothesis_id: int, review: MemberReview, db: DbSession) -> Response:
    db.delete(_hypothesis(db, review, hypothesis_id))
    db.commit()
    return Response(status_code=204)


class VerdictIn(BaseModel):
    verdict: str | None
    justification: str = ""


@router.get("/reviews/{review_id}/verdicts")
def list_verdicts(review: MemberReview, db: DbSession) -> dict[str, dict[str, dict[str, str]]]:
    ids = [article.id for article in final_articles(db, review)]
    rows = db.scalars(select(HypothesisVerdict).where(HypothesisVerdict.article_id.in_(ids))).all() if ids else []
    output: dict[str, dict[str, dict[str, str]]] = {}
    for row in rows:
        output.setdefault(str(row.article_id), {})[str(row.hypothesis_id)] = {
            "verdict": row.verdict, "justification": row.justification}
    return output


@router.put("/reviews/{review_id}/articles/{article_id}/verdicts/{hypothesis_id}")
def save_verdict(article_id: int, hypothesis_id: int, payload: VerdictIn, review: MemberReview, db: DbSession,
                 user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    hypothesis = _hypothesis(db, review, hypothesis_id)
    if article.id not in {item.id for item in final_articles(db, review)}:
        raise HTTPException(status_code=422, detail="Vereditos são registrados só para estudos da seleção final.")
    row = db.scalar(select(HypothesisVerdict).where(HypothesisVerdict.hypothesis_id == hypothesis.id,
                                                    HypothesisVerdict.article_id == article.id))
    if payload.verdict is None:
        if row is not None:
            db.delete(row)
            db.commit()
        return {"article_id": article.id, "hypothesis_id": hypothesis.id, "verdict": None}
    if payload.verdict not in VERDICTS:
        raise HTTPException(status_code=422, detail="Veredito inválido.")
    if not payload.justification.strip():
        raise HTTPException(status_code=422, detail="Justifique o veredito com base no estudo.")
    if row is None:
        row = HypothesisVerdict(hypothesis_id=hypothesis.id, article_id=article.id, verdict=payload.verdict)
        db.add(row)
    row.verdict, row.justification, row.user_id = payload.verdict, payload.justification.strip(), user.id
    db.commit()
    return {"article_id": article.id, "hypothesis_id": hypothesis.id, "verdict": row.verdict,
            "justification": row.justification}


# ---- snapshots -------------------------------------------------------------------------------

class SnapshotIn(BaseModel):
    label: str = Field(default="", max_length=200)
    filters: Filters = Field(default_factory=Filters)


def _snapshot_out(snapshot: AnalysisSnapshot, include_results: bool) -> dict[str, Any]:
    data = {"id": snapshot.id, "label": snapshot.label, "filters": snapshot.filters, "settings": snapshot.settings,
            "created_by_id": snapshot.created_by_id, "created_at": snapshot.created_at.isoformat(),
            "corpus": snapshot.results.get("corpus")}
    if include_results:
        data["results"] = snapshot.results
    return data


@router.post("/reviews/{review_id}/insights/snapshots", status_code=201)
def create_snapshot(payload: SnapshotIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    results = compute(db, review, payload.filters)
    snapshot = AnalysisSnapshot(review_id=review.id, label=payload.label.strip(), filters=payload.filters.model_dump(),
                                settings=results["settings"], results=results, created_by_id=user.id)
    db.add(snapshot)
    log_activity(db, user, "salvou um instantâneo das análises de", review, snapshot.label)
    db.commit()
    return _snapshot_out(snapshot, include_results=True)


@router.get("/reviews/{review_id}/insights/snapshots")
def list_snapshots(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    return [_snapshot_out(item, include_results=False) for item in db.scalars(
        select(AnalysisSnapshot).where(AnalysisSnapshot.review_id == review.id).order_by(AnalysisSnapshot.created_at.desc()))]


@router.get("/reviews/{review_id}/insights/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: int, review: MemberReview, db: DbSession) -> dict[str, Any]:
    snapshot = db.get(AnalysisSnapshot, snapshot_id)
    if snapshot is None or snapshot.review_id != review.id:
        raise HTTPException(status_code=404, detail="Instantâneo não encontrado.")
    return _snapshot_out(snapshot, include_results=True)
