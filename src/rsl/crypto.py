"""Symmetric encryption of the users' API keys at rest."""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from .settings import Settings


def _fernet(settings: Settings) -> Fernet:
    material = settings.secret_key or f"api-keys:{settings.jwt_secret}"
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(material.encode("utf-8")).digest()))


def encrypt(settings: Settings, value: str) -> str:
    return _fernet(settings).encrypt(value.encode("utf-8")).decode("ascii") if value else ""


def decrypt(settings: Settings, token: str) -> str:
    if not token:
        return ""
    try:
        return _fernet(settings).decrypt(token.encode("ascii")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Não foi possível ler a chave salva; cadastre-a de novo no Perfil.") from exc
