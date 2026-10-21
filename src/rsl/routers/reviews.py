from __future__ import annotations

import re
import unicodedata
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import or_, select

from ..deps import CurrentUser, DbSession, MemberReview, OwnerReview, log_activity
from ..models import Activity, Review, User, review_coauthors
from ..schemas import ReviewCreate, ReviewUpdate
from ..serializers import review_summary, user_public

router = APIRouter(tags=["revisões"])


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.casefold()).strip("-")[:200] or "revisao"


def _unique_name(db: DbSession, author: User, title: str, exclude_id: int | None = None) -> str:
    base = slugify(title)
    candidate, suffix = base, 2
    while True:
        query = select(Review.id).where(Review.author_id == author.id, Review.name == candidate)
        if exclude_id is not None:
            query = query.where(Review.id != exclude_id)
        if db.scalar(query) is None:
            return candidate
        candidate, suffix = f"{base}-{suffix}", suffix + 1


@router.get("/reviews")
def list_reviews(db: DbSession, user: CurrentUser) -> list[dict[str, Any]]:
    coauthored = select(review_coauthors.c.review_id).where(review_coauthors.c.user_id == user.id)
    reviews = db.scalars(
        select(Review)
        .where(or_(Review.author_id == user.id, Review.id.in_(coauthored)))
        .order_by(Review.updated_at.desc())
    ).all()
    return [review_summary(review, user) for review in reviews]


@router.post("/reviews", status_code=201)
def create_review(payload: ReviewCreate, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Informe o título da revisão.")
    review = Review(
        name=_unique_name(db, user, title),
        title=title,
        description=payload.description.strip(),
        author_id=user.id,
    )
    db.add(review)
    db.flush()
    log_activity(db, user, "criou a revisão", review, title)
    db.commit()
    db.refresh(review)
    return review_summary(review, user)


@router.get("/reviews/{review_id}")
def get_review(review: MemberReview, user: CurrentUser) -> dict[str, Any]:
    return review_summary(review, user)


@router.patch("/reviews/{review_id}")
def update_review(payload: ReviewUpdate, review: MemberReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    if payload.title is not None:
        title = payload.title.strip()
        if not title:
            raise HTTPException(status_code=422, detail="Informe o título da revisão.")
        review.title = title
        review.name = _unique_name(db, review.author, title, exclude_id=review.id)
    if payload.description is not None:
        review.description = payload.description.strip()
    log_activity(db, user, "editou a revisão", review)
    db.commit()
    return review_summary(review, user)


@router.delete("/reviews/{review_id}", status_code=204)
def delete_review(review: OwnerReview, db: DbSession) -> Response:
    db.delete(review)
    db.commit()
    return Response(status_code=204)


@router.post("/reviews/{review_id}/leave", status_code=204)
def leave_review(review: MemberReview, db: DbSession, user: CurrentUser) -> Response:
    if review.author_id == user.id:
        raise HTTPException(status_code=422, detail="O autor principal não pode sair da própria revisão.")
    review.co_authors = [coauthor for coauthor in review.co_authors if coauthor.id != user.id]
    log_activity(db, user, "saiu da revisão", review)
    db.commit()
    return Response(status_code=204)


@router.delete("/reviews/{review_id}/coauthors/{user_id}", status_code=204)
def remove_coauthor(user_id: int, review: OwnerReview, db: DbSession, user: CurrentUser) -> Response:
    removed = next((coauthor for coauthor in review.co_authors if coauthor.id == user_id), None)
    if removed is None:
        raise HTTPException(status_code=404, detail="Coautor não encontrado.")
    review.co_authors = [coauthor for coauthor in review.co_authors if coauthor.id != user_id]
    log_activity(db, user, "removeu o coautor", review, removed.username)
    db.commit()
    return Response(status_code=204)


@router.get("/reviews/{review_id}/activities")
def list_activities(review: MemberReview, db: DbSession) -> list[dict[str, Any]]:
    activities = db.scalars(
        select(Activity).where(Activity.review_id == review.id).order_by(Activity.created_at.desc()).limit(50)
    ).all()
    return [
        {"user": user_public(item.user), "verb": item.verb, "target": item.target,
         "created_at": item.created_at.isoformat()}
        for item in activities
    ]
