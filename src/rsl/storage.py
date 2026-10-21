"""Recording of a search result (an imported file or an API run) with its studies."""

from __future__ import annotations

import secrets
from typing import Any

from sqlalchemy.orm import Session

from .models import Article, Review, SearchResult, Source, User
from .settings import Settings


def store_import(db: Session, settings: Settings, review: Review, source: Source, user: User,
                 records: list[dict[str, Any]], file_name: str, raw: bytes) -> SearchResult:
    """Keep the raw payload for audit and create one unclassified article per record (no commit)."""
    object_key = f"reviews/{review.id}/{secrets.token_hex(8)}-{file_name}"
    target = settings.storage_path / object_key
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)

    result = SearchResult(review_id=review.id, source_id=source.id, file_name=file_name, object_key=object_key,
                          imported_count=len(records), created_by_id=user.id)
    db.add(result)
    db.flush()
    for record in records:
        db.add(Article(review_id=review.id, source_id=source.id, search_result_id=result.id,
                       created_by_id=user.id, updated_by_id=user.id, **record))
    return result
