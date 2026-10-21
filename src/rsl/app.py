from __future__ import annotations

from contextlib import asynccontextmanager

from alembic import command
from alembic.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .db import Database
from .routers import analysis, auth, collaboration, conducting, insights, invites, planning, reporting, reviews, synthesis
from .settings import ROOT, Settings, load_settings

API_PREFIX = "/api/v1"


def run_migrations(database_url: str) -> None:
    config = Config(str(ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(ROOT / "migrations"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.attributes["from_app"] = True
    command.upgrade(config, "head")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        run_migrations(settings.database_url)
        yield
        app.state.database.engine.dispose()

    app = FastAPI(title="RSL API", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.database = Database(settings.database_url)
    for module in (auth, reviews, invites, planning, conducting, analysis, insights, reporting, synthesis, collaboration):
        app.include_router(module.router, prefix=API_PREFIX)

    index = settings.web_dist / "index.html"
    if index.exists():
        app.mount("/assets", StaticFiles(directory=settings.web_dist / "assets"), name="assets")

        @app.get("/{path:path}", include_in_schema=False)
        def spa(path: str) -> FileResponse:
            # Client-side routes fall back to the SPA entry point; unknown API paths stay 404.
            if path.startswith("api/"):
                raise HTTPException(status_code=404)
            candidate = settings.web_dist / path
            if path and candidate.is_file() and settings.web_dist in candidate.resolve().parents:
                return FileResponse(candidate)
            return FileResponse(index)

    return app


app = create_app()
