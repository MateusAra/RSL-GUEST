from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt import InvalidTokenError
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import AuthSession, User
from .settings import Settings

_SCRYPT_N, _SCRYPT_R, _SCRYPT_P = 2**14, 8, 1
ISSUER = "rsl-api"


class AuthError(Exception):
    """Invalid credentials or token (HTTP 401)."""


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P, dklen=32)
    return "$".join(("scrypt", str(_SCRYPT_N), str(_SCRYPT_R), str(_SCRYPT_P), salt.hex(), digest.hex()))


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "scrypt":
            return False
        candidate = hashlib.scrypt(
            password.encode("utf-8"), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=32
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _aware(value: datetime) -> datetime:
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def _session_response(settings: Settings, user: User, session_id: str, refresh_token: str) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    access_token = jwt.encode(
        {"sub": str(user.id), "sid": session_id, "iss": ISSUER, "iat": now,
         "exp": now + timedelta(minutes=settings.access_token_minutes)},
        settings.jwt_secret,
        algorithm="HS256",
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_minutes * 60,
    }


def issue_session(db: Session, settings: Settings, user: User) -> dict[str, Any]:
    session_id = secrets.token_urlsafe(24)
    refresh_token = secrets.token_urlsafe(48)
    db.add(
        AuthSession(
            id=session_id,
            user_id=user.id,
            refresh_token_hash=_token_hash(refresh_token),
            expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days),
        )
    )
    db.commit()
    return _session_response(settings, user, session_id, refresh_token)


def refresh_session(db: Session, settings: Settings, refresh_token: str) -> dict[str, Any]:
    record = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == _token_hash(refresh_token)))
    if record is None:
        raise AuthError("invalid refresh token")
    user = db.get(User, record.user_id)
    if user is None or _aware(record.expires_at) <= datetime.now(timezone.utc):
        db.delete(record)
        db.commit()
        raise AuthError("invalid refresh token")
    new_refresh_token = secrets.token_urlsafe(48)
    record.refresh_token_hash = _token_hash(new_refresh_token)
    record.expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_days)
    db.commit()
    return _session_response(settings, user, record.id, new_refresh_token)


def decode_access_token(settings: Settings, token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token, settings.jwt_secret, algorithms=["HS256"], issuer=ISSUER,
            options={"require": ["sub", "sid", "exp", "iat"]},
        )
    except InvalidTokenError as exc:
        raise AuthError("invalid token") from exc


def user_from_token(db: Session, settings: Settings, token: str) -> tuple[User, str]:
    payload = decode_access_token(settings, token)
    session = db.get(AuthSession, payload["sid"])
    user = db.get(User, int(payload["sub"]))
    if session is None or user is None or session.user_id != user.id:
        raise AuthError("invalid token")
    if _aware(session.expires_at) <= datetime.now(timezone.utc):
        raise AuthError("invalid token")
    return user, session.id
