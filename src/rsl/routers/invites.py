from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select

from ..db import utcnow
from ..deps import CurrentUser, DbSession, OwnerReview, log_activity
from ..models import Invite, User
from ..schemas import InviteCreate
from ..serializers import invite_out, review_summary
from .auth import normalize_email

router = APIRouter(tags=["convites"])


@router.post("/reviews/{review_id}/invites", status_code=201)
def create_invite(payload: InviteCreate, review: OwnerReview, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    email = normalize_email(payload.email)
    if email == user.email:
        raise HTTPException(status_code=422, detail="Você já é o autor principal desta revisão.")
    if any(coauthor.email == email for coauthor in review.co_authors):
        raise HTTPException(status_code=409, detail="Esta pessoa já é coautora da revisão.")
    pending = db.scalar(
        select(Invite.id).where(
            Invite.review_id == review.id, Invite.invitee_email == email, Invite.status == "pending"
        )
    )
    if pending is not None:
        raise HTTPException(status_code=409, detail="Já existe um convite pendente para este e-mail.")
    invitee = db.scalar(select(User).where(User.email == email))
    invite = Invite(
        review_id=review.id,
        invited_by_id=user.id,
        invitee_email=email,
        invitee_id=None if invitee is None else invitee.id,
        code=str(uuid.uuid4()),
    )
    db.add(invite)
    log_activity(db, user, "convidou", review, email)
    db.commit()
    db.refresh(invite)
    return {**invite_out(invite), "has_account": invitee is not None}


@router.get("/reviews/{review_id}/invites")
def list_review_invites(review: OwnerReview, db: DbSession) -> list[dict[str, Any]]:
    invites = db.scalars(
        select(Invite).where(Invite.review_id == review.id).order_by(Invite.date_sent.desc())
    ).all()
    return [invite_out(invite) for invite in invites]


@router.delete("/reviews/{review_id}/invites/{invite_id}", status_code=204)
def cancel_invite(invite_id: int, review: OwnerReview, db: DbSession) -> Response:
    invite = db.get(Invite, invite_id)
    if invite is None or invite.review_id != review.id or invite.status != "pending":
        raise HTTPException(status_code=404, detail="Convite pendente não encontrado.")
    db.delete(invite)
    db.commit()
    return Response(status_code=204)


@router.get("/invites")
def my_invites(db: DbSession, user: CurrentUser) -> list[dict[str, Any]]:
    invites = db.scalars(
        select(Invite)
        .where(Invite.invitee_email == user.email, Invite.status == "pending")
        .order_by(Invite.date_sent.desc())
    ).all()
    return [invite_out(invite) for invite in invites]


def _my_pending_invite(db: DbSession, user: User, code: str) -> Invite:
    invite = db.scalar(select(Invite).where(Invite.code == code))
    if invite is None or invite.invitee_email != user.email:
        raise HTTPException(status_code=404, detail="Convite não encontrado.")
    if invite.status != "pending":
        raise HTTPException(status_code=409, detail="Este convite já foi respondido.")
    return invite


@router.post("/invites/{code}/accept")
def accept_invite(code: str, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    invite = _my_pending_invite(db, user, code)
    review = invite.review
    if not review.is_member(user):
        review.co_authors.append(user)
    invite.status, invite.invitee_id, invite.date_answered = "accepted", user.id, utcnow()
    log_activity(db, user, "entrou como coautor", review)
    db.commit()
    return review_summary(review, user)


@router.post("/invites/{code}/reject")
def reject_invite(code: str, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    invite = _my_pending_invite(db, user, code)
    invite.status, invite.invitee_id, invite.date_answered = "rejected", user.id, utcnow()
    db.commit()
    return invite_out(invite)
