"""Execution of a search run outside the request (a thread with its own database session)."""

from __future__ import annotations

import json
import logging
import threading
import time
from collections.abc import Callable
from typing import Any

import httpx
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from ..crypto import decrypt
from ..db import Database, utcnow
from ..deps import log_activity
from ..importers import normalize_title
from ..models import Article, Review, SearchRun, User, UserApiKey
from ..settings import Settings
from ..storage import store_import
from . import CONNECTORS
from .base import Credentials, Filters, SearchError

logger = logging.getLogger(__name__)
PREVIEW_SIZE = 10
PREVIEW_FIELDS = ("title", "author", "year", "journal", "doi", "url")


def load_credentials(db: Session, settings: Settings, user_id: int | None, provider: str | None) -> Credentials:
    if user_id is None or provider is None:
        return Credentials()
    stored = db.scalar(select(UserApiKey).where(UserApiKey.user_id == user_id, UserApiKey.provider == provider))
    if stored is None:
        return Credentials()
    return Credentials(key=decrypt(settings, stored.secret), extra=decrypt(settings, stored.extra))


def _identity(record: dict[str, Any]) -> str:
    return f"doi:{record['doi']}" if record.get("doi") else f"title:{normalize_title(record.get('title', ''))}"


def _new_records(db: Session, run: SearchRun, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop the records already in the review for this source (re-runs update the search) and repeats within the run."""
    seen = {
        _identity({"doi": doi, "title": title})
        for doi, title in db.execute(select(Article.doi, Article.title).where(
            Article.review_id == run.review_id, Article.source_id == run.source_id))
    }
    fresh = []
    for record in records:
        identity = _identity(record)
        if identity in seen or identity == "title:":
            continue
        seen.add(identity)
        fresh.append(record)
    return fresh


def execute_run(database: Database, settings: Settings, run_id: int, transport: httpx.BaseTransport | None = None,
                sleep: Callable[[float], None] = time.sleep) -> None:
    with database.sessions() as db:
        run = db.get(SearchRun, run_id)
        if run is None or run.status != "queued":
            return
        run.status, run.started_at = "running", utcnow()
        db.commit()
        try:
            _fetch_and_store(db, settings, run, transport, sleep)
            run.status = "done"
        except SearchError as exc:
            db.rollback()
            run.status, run.error = "failed", str(exc)
        except Exception:  # noqa: BLE001 - the run must always end with a status the user can see
            logger.exception("search run %s failed", run_id)
            db.rollback()
            run.status, run.error = "failed", "Erro inesperado durante a busca. Nada foi importado."
        run.finished_at = utcnow()
        db.commit()


def _fetch_and_store(db: Session, settings: Settings, run: SearchRun, transport: httpx.BaseTransport | None,
                     sleep: Callable[[float], None]) -> None:
    connector = CONNECTORS[run.connector](sleep=sleep)
    try:
        credentials = load_credentials(db, settings, run.user_id, connector.provider)
    except ValueError as exc:
        raise SearchError(str(exc)) from exc
    if connector.key_required and not credentials.key:
        raise SearchError(f"Cadastre sua chave do {connector.label} no Perfil antes de buscar.")

    preview = run.mode == "preview"
    limit = PREVIEW_SIZE if preview else run.max_records
    records: list[dict[str, Any]] = []
    raw: list[str] = []
    warnings: list[str] = []
    with httpx.Client(transport=transport, follow_redirects=True) as client:
        for page in connector.pages(client, run.query, Filters(run.year_from, run.year_to), credentials, limit):
            if run.total_reported is None:
                run.total_reported = page.total
            records.extend(page.records)
            raw.append(page.raw)
            warnings.extend(item for item in page.warnings if item not in warnings)
            run.retrieved = len(records)
            db.commit()  # progress, read by the page while the run goes on
            if preview:
                break
    records = records[:limit]
    run.retrieved, run.warnings = len(records), warnings
    if preview:
        run.preview = [{field: record.get(field, "") for field in PREVIEW_FIELDS} for record in records]
        return

    fresh = _new_records(db, run, records)
    review, user = db.get(Review, run.review_id), db.get(User, run.user_id)
    stamp = utcnow().strftime("%Y-%m-%d-%H%M")
    payload = json.dumps({"connector": run.connector, "query": run.query, "year_from": run.year_from,
                          "year_to": run.year_to, "pages": raw}, ensure_ascii=False).encode("utf-8")
    result = store_import(db, settings, review, run.source, user, fresh, f"api-{run.connector}-{stamp}.json", payload)
    run.search_result_id = result.id
    run.imported, run.skipped_existing = len(fresh), len(records) - len(fresh)
    log_activity(db, user, f"buscou pela API e importou {len(fresh)} estudo(s) de", review, run.source.name)


def dispatch(state: Any, run_id: int) -> None:
    """Run in the background; tests set state.search_inline to run in the request with a mock transport."""
    arguments = (state.database, state.settings, run_id, getattr(state, "search_transport", None),
                 getattr(state, "search_sleep", time.sleep))
    if getattr(state, "search_inline", False):
        execute_run(*arguments)
    else:
        threading.Thread(target=execute_run, args=arguments, name=f"search-run-{run_id}", daemon=True).start()


def mark_interrupted(database: Database) -> None:
    with database.sessions() as db:
        db.execute(update(SearchRun).where(SearchRun.status.in_(("queued", "running"))).values(
            status="failed", error="Busca interrompida pelo reinício do servidor. Nada foi importado.",
            finished_at=utcnow()))
        db.commit()
