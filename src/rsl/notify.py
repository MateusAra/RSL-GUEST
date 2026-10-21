from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.orm import Session

from .models import Notification, Review


def notify(db: Session, user_ids: Iterable[int | None], kind: str, message: str, review: Review | None = None,
           link: str = "", exclude: int | None = None) -> None:
    """In-app notification for each user (deduplicated, never to the user who triggered it)."""
    for user_id in dict.fromkeys(user_ids):
        if user_id is None or user_id == exclude:
            continue
        db.add(Notification(user_id=user_id, review_id=None if review is None else review.id, kind=kind,
                            message=message[:500], link=link[:300]))
