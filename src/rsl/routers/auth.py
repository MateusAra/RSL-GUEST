from __future__ import annotations

import re
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, or_, select

from ..deps import AppSettings, CurrentUser, DbSession, current_session
from ..models import AuthSession, Invite, User
from ..schemas import LoginRequest, PasswordChange, ProfileUpdate, RefreshRequest, SignupRequest
from ..security import AuthError, hash_password, issue_session, refresh_session, verify_password
from ..serializers import user_private

router = APIRouter(tags=["contas"])

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_email(email: str) -> str:
    email = email.strip().casefold()
    if not EMAIL_PATTERN.match(email):
        raise HTTPException(status_code=422, detail="Informe um e-mail válido.")
    return email


def _email_taken(db: DbSession, email: str, exclude_user_id: int | None = None) -> bool:
    query = select(User.id).where(User.email == email)
    if exclude_user_id is not None:
        query = query.where(User.id != exclude_user_id)
    return db.scalar(query) is not None


def _link_pending_invites(db: DbSession, user: User) -> None:
    for invite in db.scalars(select(Invite).where(Invite.invitee_email == user.email, Invite.invitee_id.is_(None))):
        invite.invitee_id = user.id


@router.post("/auth/signup", status_code=201)
def signup(payload: SignupRequest, db: DbSession, settings: AppSettings) -> dict[str, Any]:
    username = payload.username.strip()
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(status_code=422, detail="O usuário só pode ter letras, números, ponto, hífen e sublinhado.")
    email = normalize_email(payload.email)
    if db.scalar(select(User.id).where(func.lower(User.username) == username.casefold())) is not None:
        raise HTTPException(status_code=409, detail="Este nome de usuário já está em uso.")
    if _email_taken(db, email):
        raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail.")
    user = User(
        username=username,
        email=email,
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.flush()
    _link_pending_invites(db, user)
    db.commit()
    return {**issue_session(db, settings, user), "user": user_private(user)}


@router.post("/auth/login")
def login(payload: LoginRequest, db: DbSession, settings: AppSettings) -> dict[str, Any]:
    identifier = payload.login.strip().casefold()
    user = db.scalar(select(User).where(or_(func.lower(User.username) == identifier, User.email == identifier)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    return {**issue_session(db, settings, user), "user": user_private(user)}


@router.post("/auth/refresh")
def refresh(payload: RefreshRequest, db: DbSession, settings: AppSettings) -> dict[str, Any]:
    try:
        return refresh_session(db, settings, payload.refresh_token)
    except AuthError as exc:
        raise HTTPException(status_code=401, detail="Sessão expirada. Entre novamente.") from exc


@router.post("/auth/logout", status_code=204)
def logout(db: DbSession, session: Annotated[tuple[User, str], Depends(current_session)]) -> Response:
    record = db.get(AuthSession, session[1])
    if record is not None:
        db.delete(record)
        db.commit()
    return Response(status_code=204)


@router.get("/me")
def me(user: CurrentUser) -> dict[str, Any]:
    return user_private(user)


@router.patch("/me")
def update_me(payload: ProfileUpdate, db: DbSession, user: CurrentUser) -> dict[str, Any]:
    if payload.first_name is not None:
        user.first_name = payload.first_name.strip()
    if payload.last_name is not None:
        user.last_name = payload.last_name.strip()
    if payload.email is not None:
        email = normalize_email(payload.email)
        if _email_taken(db, email, exclude_user_id=user.id):
            raise HTTPException(status_code=409, detail="Já existe uma conta com este e-mail.")
        user.email = email
        _link_pending_invites(db, user)
    db.commit()
    return user_private(user)


@router.post("/me/password", status_code=204)
def change_password(payload: PasswordChange, db: DbSession, user: CurrentUser) -> Response:
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=422, detail="A senha atual está incorreta.")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return Response(status_code=204)
