from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from .models import Activity, Review, User
from .security import AuthError, user_from_token
from .settings import Settings


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Iterator[Session]:
    yield from request.app.state.database.session()


DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def bearer_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Autenticação necessária.")
    return authorization.removeprefix("Bearer ")


def current_session(
    db: DbSession, settings: AppSettings, token: Annotated[str, Depends(bearer_token)]
) -> tuple[User, str]:
    try:
        return user_from_token(db, settings, token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada.") from exc


def current_user(session: Annotated[tuple[User, str], Depends(current_session)]) -> User:
    return session[0]


CurrentUser = Annotated[User, Depends(current_user)]


def member_review(review_id: int, db: DbSession, user: CurrentUser) -> Review:
    """The review if the user is its author or a co-author; 404 otherwise (as in Parsifal)."""
    review = db.get(Review, review_id)
    if review is None or not review.is_member(user):
        raise HTTPException(status_code=404, detail="Revisão não encontrada.")
    return review


MemberReview = Annotated[Review, Depends(member_review)]


def owner_review(review: MemberReview, user: CurrentUser) -> Review:
    if review.author_id != user.id:
        raise HTTPException(status_code=403, detail="Apenas o autor principal pode fazer isso.")
    return review


OwnerReview = Annotated[Review, Depends(owner_review)]


def log_activity(db: Session, user: User, verb: str, review: Review | None = None, target: str = "") -> None:
    db.add(Activity(user_id=user.id, review_id=None if review is None else review.id, verb=verb, target=target[:500]))
