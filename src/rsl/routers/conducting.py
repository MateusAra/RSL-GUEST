from __future__ import annotations

import csv
import io
import re
import secrets
from typing import Any, Literal

from fastapi import APIRouter, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
import numpy as np
from rapidfuzz import fuzz, process
from sqlalchemy import asc, delete, desc, func, or_, select

from ..deps import AppSettings, CurrentUser, DbSession, MemberReview, log_activity
from ..importers import ARTICLE_TEXT_FIELDS, normalize_doi, normalize_title, parse_bibliography
from ..models import ARTICLE_STATUSES, Article, ArticleAssignment, Review, SearchResult, SearchSession, SelectionCriteria, Source

router = APIRouter(tags=["condução"])

MAX_IMPORT_BYTES = 50 * 1024 * 1024
DUPLICATE_TITLE_SIMILARITY = 95
SORTABLE = {"title": Article.title, "author": Article.author, "year": Article.year, "journal": Article.journal,
            "status": Article.status, "source": Article.source_id, "created_at": Article.created_at}


def _review_source(review: Review, source_id: int) -> Source:
    source = next((item for item in review.sources if item.id == source_id), None)
    if source is None:
        raise HTTPException(status_code=404, detail="Fonte não encontrada nesta revisão.")
    return source


def _article(db: DbSession, review: Review, article_id: int) -> Article:
    article = db.get(Article, article_id)
    if article is None or article.review_id != review.id:
        raise HTTPException(status_code=404, detail="Artigo não encontrado nesta revisão.")
    return article


def article_out(article: Article) -> dict[str, Any]:
    return {
        "id": article.id,
        **{field: getattr(article, field) for field in ARTICLE_TEXT_FIELDS},
        "source": None if article.source is None else {"id": article.source.id, "name": article.source.name},
        "status": article.status,
        "status_label": ARTICLE_STATUSES[article.status],
        "comments": article.comments,
        "selection_criteria_id": article.selection_criteria_id,
        "finished_data_extraction": article.finished_data_extraction,
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat(),
    }


# ---- 1. search strings per source -------------------------------------------

class SourceStringIn(BaseModel):
    search_string: str = Field(max_length=10000)


def _session(db: DbSession, review: Review, source_id: int | None) -> SearchSession | None:
    condition = SearchSession.source_id.is_(None) if source_id is None else SearchSession.source_id == source_id
    return db.scalar(select(SearchSession).where(SearchSession.review_id == review.id, condition))


@router.get("/reviews/{review_id}/search")
def get_search(review: MemberReview, db: DbSession) -> dict[str, Any]:
    base = _session(db, review, None)
    return {
        "base_string": "" if base is None else base.search_string,
        "sources": [
            {
                "source": {"id": source.id, "name": source.name, "url": source.url},
                "search_string": "" if (session := _session(db, review, source.id)) is None else session.search_string,
                "version": 0 if session is None else session.version,
            }
            for source in review.sources
        ],
    }


@router.put("/reviews/{review_id}/search/{source_id}")
def save_source_string(source_id: int, payload: SourceStringIn, review: MemberReview, db: DbSession,
                       user: CurrentUser) -> dict[str, Any]:
    source = _review_source(review, source_id)
    session = _session(db, review, source.id)
    if session is None:
        session = SearchSession(review_id=review.id, source_id=source.id, search_string="", version=0)
        db.add(session)
    session.search_string = payload.search_string.strip()
    session.version += 1
    log_activity(db, user, "salvou a string de busca de", review, source.name)
    db.commit()
    return {"search_string": session.search_string, "version": session.version}


# ---- 2. import studies --------------------------------------------------------

@router.get("/reviews/{review_id}/imports")
def import_summary(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    counts = dict(
        db.execute(
            select(Article.source_id, func.count()).where(Article.review_id == review.id).group_by(Article.source_id)
        ).all()
    )
    files = db.scalars(
        select(SearchResult).where(SearchResult.review_id == review.id).order_by(SearchResult.created_at.desc())
    ).all()
    return [
        {
            "source": {"id": source.id, "name": source.name},
            "articles": counts.get(source.id, 0),
            "files": [
                {"id": item.id, "file_name": item.file_name, "imported_count": item.imported_count,
                 "created_at": item.created_at.isoformat()}
                for item in files if item.source_id == source.id
            ],
        }
        for source in review.sources
    ]


@router.post("/reviews/{review_id}/sources/{source_id}/import", status_code=201)
async def import_articles(source_id: int, review: MemberReview, db: DbSession, user: CurrentUser,
                          settings: AppSettings, file: UploadFile = File(...)) -> dict[str, Any]:
    source = _review_source(review, source_id)
    content = await file.read(MAX_IMPORT_BYTES + 1)
    if len(content) > MAX_IMPORT_BYTES:
        raise HTTPException(status_code=413, detail="O arquivo passa do limite de 50 MB.")
    file_name = re.sub(r"[^\w.\-]+", "_", (file.filename or "importacao").rsplit("/", 1)[-1])[:200]
    try:
        records, report = parse_bibliography(content, file_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    object_key = f"reviews/{review.id}/{secrets.token_hex(8)}-{file_name}"
    target = settings.storage_path / object_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content)

    result = SearchResult(review_id=review.id, source_id=source.id, file_name=file_name, object_key=object_key,
                          imported_count=len(records), created_by_id=user.id)
    db.add(result)
    db.flush()
    for record in records:
        db.add(Article(review_id=review.id, source_id=source.id, search_result_id=result.id,
                       created_by_id=user.id, updated_by_id=user.id, **record))
    log_activity(db, user, f"importou {len(records)} estudo(s) de", review, source.name)
    db.commit()
    return {"source": {"id": source.id, "name": source.name}, "file_name": file_name, **report}


class ArticleIn(BaseModel):
    source_id: int
    title: str = Field(max_length=1000)
    author: str = Field(default="", max_length=1000)
    journal: str = Field(default="", max_length=1000)
    year: str = Field(default="", max_length=10)
    abstract: str = ""
    doi: str = Field(default="", max_length=200)
    url: str = Field(default="", max_length=500)
    keywords: str = Field(default="", max_length=1000)
    document_type: str = Field(default="", max_length=100)


@router.post("/reviews/{review_id}/articles", status_code=201)
def new_article(payload: ArticleIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    source = _review_source(review, payload.source_id)
    data = payload.model_dump(exclude={"source_id"})
    data["title"] = data["title"].strip()
    if not data["title"]:
        raise HTTPException(status_code=422, detail="Informe o título do artigo.")
    data["doi"] = normalize_doi(data["doi"]) if data["doi"] else ""
    article = Article(review_id=review.id, source_id=source.id, created_by_id=user.id, updated_by_id=user.id, **data)
    db.add(article)
    log_activity(db, user, "adicionou o artigo", review, article.title)
    db.commit()
    db.refresh(article)
    return article_out(article)


# ---- 3. study selection ---------------------------------------------------------

def _filtered(review: Review, source_id: int | None, status: str | None, q: str | None,
              assigned_to: int | None = None):
    query = select(Article).where(Article.review_id == review.id)
    if assigned_to is not None:
        query = query.where(Article.id.in_(select(ArticleAssignment.article_id).where(
            ArticleAssignment.stage == "selection", ArticleAssignment.user_id == assigned_to)))
    if source_id is not None:
        query = query.where(Article.source_id == source_id)
    if status:
        query = query.where(Article.status == status)
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(or_(Article.title.ilike(pattern), Article.author.ilike(pattern),
                                Article.abstract.ilike(pattern), Article.doi.ilike(pattern)))
    return query


@router.get("/reviews/{review_id}/articles")
def list_articles(
    review: MemberReview,
    db: DbSession,
    user: CurrentUser,
    source_id: int | None = None,
    status: Literal["U", "A", "R", "D"] | None = None,
    q: str | None = None,
    sort: Literal["title", "author", "year", "journal", "status", "source", "created_at"] = "title",
    order: Literal["asc", "desc"] = "asc",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=500),
    assigned_to_me: bool = False,
) -> dict[str, Any]:
    direction = asc if order == "asc" else desc
    assigned_to = user.id if assigned_to_me else None
    query = _filtered(review, source_id, status, q, assigned_to).order_by(direction(SORTABLE[sort]), Article.id)
    # Every id in the current filter and order, so the details modal can step through all of them.
    ids = list(db.scalars(query.with_only_columns(Article.id)))
    items = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    unfiltered = _filtered(review, source_id, None, q, assigned_to).subquery()
    status_counts = dict(
        db.execute(select(unfiltered.c.status, func.count()).group_by(unfiltered.c.status)).all()
    )
    source_counts = dict(
        db.execute(
            select(Article.source_id, func.count()).where(Article.review_id == review.id).group_by(Article.source_id)
        ).all()
    )
    return {
        "items": [article_out(article) for article in items],
        "total": len(ids),
        "page": page,
        "page_size": page_size,
        "ids": ids,
        "status_counts": {code: status_counts.get(code, 0) for code in ARTICLE_STATUSES},
        "source_counts": {str(key): value for key, value in source_counts.items()},
    }


@router.get("/reviews/{review_id}/articles/{article_id}")
def get_article(article_id: int, review: MemberReview, db: DbSession) -> dict[str, Any]:
    return article_out(_article(db, review, article_id))


class ArticleUpdate(BaseModel):
    status: Literal["U", "A", "R", "D"] | None = None
    comments: str | None = Field(default=None, max_length=2000)
    selection_criteria_id: int | None = None
    title: str | None = Field(default=None, max_length=1000)
    author: str | None = Field(default=None, max_length=1000)
    journal: str | None = Field(default=None, max_length=1000)
    year: str | None = Field(default=None, max_length=10)
    abstract: str | None = None
    doi: str | None = Field(default=None, max_length=200)
    url: str | None = Field(default=None, max_length=500)
    keywords: str | None = Field(default=None, max_length=1000)


@router.patch("/reviews/{review_id}/articles/{article_id}")
def update_article(article_id: int, payload: ArticleUpdate, review: MemberReview, db: DbSession,
                   user: CurrentUser) -> dict[str, Any]:
    article = _article(db, review, article_id)
    changes = payload.model_dump(exclude_unset=True)
    if "selection_criteria_id" in changes and changes["selection_criteria_id"] is not None:
        criteria = db.get(SelectionCriteria, changes["selection_criteria_id"])
        if criteria is None or criteria.review_id != review.id:
            raise HTTPException(status_code=404, detail="Critério não encontrado nesta revisão.")
    if "title" in changes and not (changes["title"] or "").strip():
        raise HTTPException(status_code=422, detail="O título não pode ficar vazio.")
    for field, value in changes.items():
        setattr(article, field, value.strip() if isinstance(value, str) and field != "abstract" else value)
    if changes.get("status") in {"U", "D"} and "selection_criteria_id" not in changes:
        article.selection_criteria_id = None
    article.updated_by_id = user.id
    db.commit()
    db.refresh(article)
    return article_out(article)


class BulkIn(BaseModel):
    ids: list[int]
    action: Literal["accept", "reject", "duplicated", "unclassify", "remove"]


BULK_STATUS = {"accept": "A", "reject": "R", "duplicated": "D", "unclassify": "U"}


@router.post("/reviews/{review_id}/articles/bulk")
def bulk_action(payload: BulkIn, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, int]:
    ids = list(db.scalars(select(Article.id).where(Article.review_id == review.id, Article.id.in_(payload.ids))))
    if payload.action == "remove":
        db.execute(delete(Article).where(Article.id.in_(ids)))
    else:
        for article in db.scalars(select(Article).where(Article.id.in_(ids))):
            article.status, article.updated_by_id = BULK_STATUS[payload.action], user.id
    log_activity(db, user, f"aplicou '{payload.action}' a {len(ids)} estudo(s) em", review)
    db.commit()
    return {"affected": len(ids)}


@router.post("/reviews/{review_id}/articles/find-duplicates")
def find_duplicates(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    """Group articles that share the DOI or have nearly the same normalized title."""
    articles = db.scalars(
        select(Article).where(Article.review_id == review.id, Article.status != "D").order_by(Article.id)
    ).all()
    parent = {article.id: article.id for article in articles}

    def find(item: int) -> int:
        while parent[item] != item:
            parent[item] = parent[parent[item]]
            item = parent[item]
        return item

    by_doi: dict[str, int] = {}
    for article in articles:
        if article.doi:
            if article.doi in by_doi:
                parent[find(article.id)] = find(by_doi[article.doi])
            by_doi.setdefault(article.doi, article.id)

    titled = [(article.id, normalize_title(article.title)) for article in articles if normalize_title(article.title)]
    titles = [title for _, title in titled]
    # Row blocks keep memory bounded on large imports; float32 keeps the exact score at the cutoff.
    for start in range(0, len(titles), 500):
        scores = process.cdist(titles[start:start + 500], titles, scorer=fuzz.ratio,
                               score_cutoff=DUPLICATE_TITLE_SIMILARITY, dtype=np.float32, workers=-1)
        for row, column in np.argwhere(scores > 0):
            first, second = start + int(row), int(column)
            if second > first:
                parent[find(titled[second][0])] = find(titled[first][0])

    groups: dict[int, list[Article]] = {}
    for article in articles:
        groups.setdefault(find(article.id), []).append(article)
    return [
        {"articles": [article_out(article) for article in members]}
        for members in groups.values()
        if len(members) > 1
    ]


class ResolveIn(BaseModel):
    keep_id: int
    duplicate_ids: list[int]


@router.post("/reviews/{review_id}/articles/resolve-duplicates")
def resolve_duplicates(payload: list[ResolveIn], review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, int]:
    marked = 0
    for group in payload:
        _article(db, review, group.keep_id)
        for article_id in group.duplicate_ids:
            if article_id == group.keep_id:
                continue
            article = _article(db, review, article_id)
            article.status, article.updated_by_id = "D", user.id
            marked += 1
    log_activity(db, user, f"marcou {marked} duplicado(s) em", review)
    db.commit()
    return {"marked": marked}


def _bibtex(articles: list[Article]) -> str:
    entries = []
    for article in articles:
        entry_type = re.sub(r"[^a-z]", "", article.document_type.casefold()) or "article"
        if entry_type in {"jour", "journalarticle"}:
            entry_type = "article"
        elif entry_type in {"conf", "cpaper", "conferencepaper"}:
            entry_type = "inproceedings"
        key = article.bibtex_key or f"art{article.id}"
        fields = {"title": article.title, "author": article.author, "journal": article.journal, "year": article.year,
                  "volume": article.volume, "pages": article.pages, "doi": article.doi, "url": article.url,
                  "abstract": article.abstract, "keywords": article.keywords, "publisher": article.publisher,
                  "issn": article.issn}
        body = ",\n".join(f"  {name} = {{{value.replace('{', '').replace('}', '')}}}"
                          for name, value in fields.items() if value)
        entries.append(f"@{entry_type}{{{key},\n{body}\n}}")
    return "\n\n".join(entries) + "\n"


@router.get("/reviews/{review_id}/articles-export")
def export_articles(
    review: MemberReview,
    db: DbSession,
    format: Literal["bibtex", "csv"] = "bibtex",
    source_id: int | None = None,
    status: Literal["U", "A", "R", "D"] | None = None,
) -> Response:
    articles = list(db.scalars(_filtered(review, source_id, status, None).order_by(Article.title)))
    if format == "bibtex":
        return Response(_bibtex(articles), media_type="application/x-bibtex",
                        headers={"Content-Disposition": f'attachment; filename="{review.name}.bib"'})
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["id", "status", "source", *ARTICLE_TEXT_FIELDS, "comments"])
    for article in articles:
        writer.writerow([article.id, ARTICLE_STATUSES[article.status], article.source.name if article.source else "",
                         *(getattr(article, field) for field in ARTICLE_TEXT_FIELDS), article.comments])
    return Response(buffer.getvalue(), media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{review.name}.csv"'})
