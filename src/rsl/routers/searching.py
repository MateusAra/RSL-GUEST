from __future__ import annotations

import time
from typing import Any, Literal

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import select

from ..crypto import encrypt
from ..deps import AppSettings, CurrentUser, DbSession, MemberReview
from ..models import RUN_STATUSES, SearchRun, SearchSession, UserApiKey
from ..search import CONNECTORS, PROVIDERS, SearchError, connector_info
from ..search.base import Filters
from ..search.runner import dispatch, load_credentials
from .conducting import _review_source

router = APIRouter(tags=["busca automática"])

DEFAULT_LIMIT = 1000


@router.get("/search/connectors")
def list_connectors() -> list[dict[str, Any]]:
    return [connector_info(key) for key in CONNECTORS]


# ---- the user's API keys -----------------------------------------------------

def _provider(provider: str) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise HTTPException(status_code=404, detail="Provedor de API desconhecido.")
    return PROVIDERS[provider]


def _stored_key(db: DbSession, user: CurrentUser, provider: str) -> UserApiKey | None:
    return db.scalar(select(UserApiKey).where(UserApiKey.user_id == user.id, UserApiKey.provider == provider))


@router.get("/me/api-keys")
def list_api_keys(db: DbSession, user: CurrentUser) -> list[dict[str, Any]]:
    stored = {item.provider: item for item in db.scalars(select(UserApiKey).where(UserApiKey.user_id == user.id))}
    return [
        {
            "provider": provider, "label": info["label"], "url": info["url"], "required": info["required"],
            "extra_label": info["extra"], "configured": provider in stored,
            "last_four": stored[provider].last_four if provider in stored else "",
            "has_extra": bool(stored[provider].extra) if provider in stored else False,
            "updated_at": stored[provider].updated_at.isoformat() if provider in stored else None,
            "connectors": [connector.label for connector in CONNECTORS.values() if connector.provider == provider],
        }
        for provider, info in PROVIDERS.items()
    ]


class ApiKeyIn(BaseModel):
    key: str = Field(min_length=4, max_length=500)
    extra: str = Field(default="", max_length=500)


@router.put("/me/api-keys/{provider}", status_code=204)
def save_api_key(provider: str, payload: ApiKeyIn, db: DbSession, user: CurrentUser, settings: AppSettings) -> Response:
    _provider(provider)
    key = payload.key.strip()
    stored = _stored_key(db, user, provider)
    if stored is None:
        stored = UserApiKey(user_id=user.id, provider=provider)
        db.add(stored)
    stored.secret, stored.extra, stored.last_four = encrypt(settings, key), encrypt(settings, payload.extra.strip()), key[-4:]
    db.commit()
    return Response(status_code=204)


@router.delete("/me/api-keys/{provider}", status_code=204)
def delete_api_key(provider: str, db: DbSession, user: CurrentUser) -> Response:
    _provider(provider)
    stored = _stored_key(db, user, provider)
    if stored is not None:
        db.delete(stored)
        db.commit()
    return Response(status_code=204)


@router.post("/me/api-keys/{provider}/test")
def test_api_key(provider: str, request: Request, db: DbSession, user: CurrentUser, settings: AppSettings) -> dict[str, Any]:
    info = _provider(provider)
    connector = CONNECTORS[info["test_connector"]](sleep=getattr(request.app.state, "search_sleep", time.sleep))
    try:
        credentials = load_credentials(db, settings, user.id, provider)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not credentials.key:
        raise HTTPException(status_code=422, detail="Salve a chave antes de testar.")
    probe = {"ieee": "software", "scopus": "TITLE(software)", "sciencedirect": "software", "springer": "software",
             "wos": "TS=(software)", "semantic_scholar": "software", "openalex": "software"}[connector.key]
    try:
        with httpx.Client(transport=getattr(request.app.state, "search_transport", None), follow_redirects=True) as client:
            page = next(iter(connector.pages(client, probe, Filters(), credentials, 1)), None)
    except SearchError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"ok": True, "total": None if page is None else page.total}


# ---- search runs ---------------------------------------------------------------

class RunIn(BaseModel):
    mode: Literal["preview", "import"]
    year_from: int | None = Field(default=None, ge=1900, le=2100)
    year_to: int | None = Field(default=None, ge=1900, le=2100)
    max_records: int = Field(default=DEFAULT_LIMIT, ge=1, le=5000)

    @model_validator(mode="after")
    def _years(self) -> RunIn:
        if self.year_from and self.year_to and self.year_from > self.year_to:
            raise ValueError("O ano inicial não pode ser maior que o final.")
        return self


def run_out(run: SearchRun) -> dict[str, Any]:
    return {
        "id": run.id, "source": {"id": run.source.id, "name": run.source.name}, "connector": run.connector,
        "connector_label": CONNECTORS[run.connector].label if run.connector in CONNECTORS else run.connector,
        "query": run.query, "year_from": run.year_from, "year_to": run.year_to, "max_records": run.max_records,
        "mode": run.mode, "status": run.status, "status_label": RUN_STATUSES[run.status],
        "total_reported": run.total_reported, "retrieved": run.retrieved, "imported": run.imported,
        "skipped_existing": run.skipped_existing, "warnings": run.warnings, "preview": run.preview, "error": run.error,
        "search_result_id": run.search_result_id, "user_id": run.user_id,
        "created_at": run.created_at.isoformat(),
        "finished_at": None if run.finished_at is None else run.finished_at.isoformat(),
    }


@router.post("/reviews/{review_id}/sources/{source_id}/search-runs", status_code=202)
def start_run(source_id: int, payload: RunIn, request: Request, review: MemberReview, db: DbSession,
              user: CurrentUser, settings: AppSettings) -> dict[str, Any]:
    source = _review_source(review, source_id)
    if source.connector not in CONNECTORS:
        raise HTTPException(status_code=422, detail="Esta fonte não tem busca automática; importe o arquivo exportado da base.")
    connector = CONNECTORS[source.connector]
    session = db.scalar(select(SearchSession).where(SearchSession.review_id == review.id, SearchSession.source_id == source.id))
    if session is None or not session.search_string.strip():
        raise HTTPException(status_code=422, detail="Salve a string desta fonte antes de executar a busca.")
    if connector.key_required:
        try:
            has_key = bool(load_credentials(db, settings, user.id, connector.provider).key)
        except ValueError:
            has_key = False
        if not has_key:
            raise HTTPException(status_code=422, detail=f"Cadastre sua chave do {connector.label} em Perfil › Chaves de API.")
    if db.scalar(select(SearchRun.id).where(SearchRun.review_id == review.id, SearchRun.source_id == source.id,
                                            SearchRun.status.in_(("queued", "running")))):
        raise HTTPException(status_code=409, detail="Já há uma busca em andamento nesta fonte.")
    run = SearchRun(review_id=review.id, source_id=source.id, user_id=user.id, connector=connector.key,
                    query=session.search_string, year_from=payload.year_from, year_to=payload.year_to,
                    max_records=min(payload.max_records, connector.max_records), mode=payload.mode, warnings=[])
    db.add(run)
    db.commit()
    dispatch(request.app.state, run.id)
    db.refresh(run)
    return run_out(run)


@router.get("/reviews/{review_id}/search-runs")
def list_runs(review: MemberReview, db: DbSession, source_id: int | None = None) -> list[dict[str, Any]]:
    query = select(SearchRun).where(SearchRun.review_id == review.id)
    if source_id is not None:
        query = query.where(SearchRun.source_id == source_id)
    return [run_out(run) for run in db.scalars(query.order_by(SearchRun.created_at.desc(), SearchRun.id.desc()))]


@router.get("/reviews/{review_id}/search-runs/{run_id}")
def get_run(run_id: int, review: MemberReview, db: DbSession) -> dict[str, Any]:
    run = db.get(SearchRun, run_id)
    if run is None or run.review_id != review.id:
        raise HTTPException(status_code=404, detail="Execução não encontrada nesta revisão.")
    return run_out(run)
