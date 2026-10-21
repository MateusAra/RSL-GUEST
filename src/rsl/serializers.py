from __future__ import annotations

from typing import Any

from .models import Invite, Review, User


def user_public(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "full_name": user.full_name,
    }


def user_private(user: User) -> dict[str, Any]:
    return {**user_public(user), "email": user.email, "created_at": user.created_at.isoformat()}


def review_summary(review: Review, viewer: User) -> dict[str, Any]:
    return {
        "id": review.id,
        "name": review.name,
        "title": review.title,
        "description": review.description,
        "author": user_public(review.author),
        "co_authors": [user_public(user) for user in review.co_authors],
        "is_owner": review.author_id == viewer.id,
        "created_at": review.created_at.isoformat(),
        "updated_at": review.updated_at.isoformat(),
    }


def invite_out(invite: Invite) -> dict[str, Any]:
    return {
        "id": invite.id,
        "code": invite.code,
        "review": {"id": invite.review.id, "title": invite.review.title},
        "invited_by": user_public(invite.invited_by),
        "invitee_email": invite.invitee_email,
        "status": invite.status,
        "date_sent": invite.date_sent.isoformat(),
        "date_answered": None if invite.date_answered is None else invite.date_answered.isoformat(),
    }
