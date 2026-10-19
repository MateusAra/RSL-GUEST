from __future__ import annotations

from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    REVISOR = "revisor"
    TERCEIRO_REVISOR = "terceiro_revisor"
    OBSERVADOR = "observador"
