from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    storage_path: Path
    web_dist: Path
    secret_key: str = ""  # encrypts the users' API keys; derived from jwt_secret when empty
    access_token_minutes: int = 15
    refresh_token_days: int = 30


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ.get("RSL_DATABASE_URL", f"sqlite+pysqlite:///{(ROOT / 'rsl.sqlite3').as_posix()}"),
        jwt_secret=os.environ.get("RSL_JWT_SECRET", "development-only-secret-change-before-deployment-32b"),
        storage_path=Path(os.environ.get("RSL_STORAGE_PATH", ROOT / "storage")),
        web_dist=Path(os.environ.get("RSL_WEB_DIST", ROOT / "web" / "dist")),
        secret_key=os.environ.get("RSL_SECRET_KEY", ""),
    )
