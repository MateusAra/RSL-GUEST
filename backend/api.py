from __future__ import annotations

import os
import sys
import csv
import json
from io import StringIO
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Header, HTTPException, Response, UploadFile, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from alembic import command
from alembic.config import Config

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from rsl_foundation import AuthService, Role, User
from rsl_foundation.object_storage import FileSystemObjectStorage, S3ObjectStorage

JWT_SECRET = os.environ.get("RSL_JWT_SECRET", "local-user-test-only-secret-change-before-deployment")
DATABASE_URL = os.environ.get("RSL_DATABASE_URL", "sqlite+pysqlite:///./rsl_xai.sqlite3")
if os.environ.get("OBJECT_STORAGE_BACKEND", "minio").casefold() == "filesystem":
    object_storage = FileSystemObjectStorage(os.environ.get("ARTIFACT_STORAGE_PATH", "./artifact-data"))
else:
    object_storage = S3ObjectStorage(
        endpoint=os.environ.get("MINIO_ENDPOINT", "127.0.0.1:9000"),
        access_key=os.environ.get("MINIO_ACCESS_KEY", "rsl-local-access"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "rsl-local-secret-change-before-deploy"),
        bucket=os.environ.get("MINIO_BUCKET", "rsl-artifacts"),
        secure=os.environ.get("MINIO_SECURE", "false").casefold() == "true",
    )
service = AuthService(JWT_SECRET, database_url=DATABASE_URL, object_storage=object_storage)


def get_token_from_header(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="401: authentication required")
    return authorization.replace("Bearer ", "", 1)


def permission_http_status(error: PermissionError) -> int:
    return 401 if str(error).startswith("401:") else 403


class LoginRequest(BaseModel):
    email: str
    password: str


class UserCreateRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)
    role: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ProjectMemberRequest(BaseModel):
    email: str
    role: str


class ProjectCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    objective: str = Field(min_length=1, max_length=4000)
    study_type: str = Field(min_length=1, max_length=100)
    members: list[ProjectMemberRequest]


class ProjectDocumentRequest(BaseModel):
    data: dict[str, Any]


class ProtocolDeviationRequest(BaseModel):
    stage: str
    description: str
    justification: str
    affected_section: str


class SearchExecutionRequest(BaseModel):
    base: str
    query: str
    fields: list[str]
    result_limit: int | None = None


class DuplicateDecisionRequest(BaseModel):
    decision: str
    canonical_study_id: str | None = None
    justification: str


class TriageVoteRequest(BaseModel):
    phase: int
    vote: str
    criterion_id: str | None = None
    confirm: bool = False
    expected_version: int


class QualityScoreItem(BaseModel):
    criterion_id: str
    score: float | None
    justification: str


class QualityAssessmentRequest(BaseModel):
    scores: list[QualityScoreItem]
    confirm: bool = False
    expected_version: int


class ExtractionCreateRequest(BaseModel):
    field_id: str
    value: Any
    quote: str | None = None
    page_reference: str | None = None
    expected_version: int


class ExtractionVerificationRequest(BaseModel):
    decision: str
    justification: str


def seed_data() -> None:
    seed_users = (
        User(id="u-admin", email="admin@rsl.local", role=Role.ADMIN),
        User(id="u-r1", email="reviewer@rsl.local", role=Role.REVISOR),
        User(id="u-r2", email="reviewer2@rsl.local", role=Role.REVISOR),
        User(id="u-r3", email="third-reviewer@rsl.local", role=Role.TERCEIRO_REVISOR),
        User(id="u-obs", email="observer@rsl.local", role=Role.OBSERVADOR),
    )
    seed_passwords = ("admin123", "reviewer123", "reviewer2123", "reviewer3123", "observer123")
    for user, password in zip(seed_users, seed_passwords):
        if not service.email_exists(user.email):
            service.register_user(user, password=password)


@asynccontextmanager
async def lifespan(_: FastAPI):
    migration_config = Config(str(ROOT / "alembic.ini"))
    migration_config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))
    command.upgrade(migration_config, "head")
    seed_data()
    try:
        yield
    finally:
        service.close()


app = FastAPI(title="RSL XAI API", version="0.1.0", lifespan=lifespan)


@app.post("/api/v1/auth/login")
def login(payload: LoginRequest) -> dict[str, Any]:
    try:
        return service.create_session(payload.email, payload.password)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.post("/api/v1/auth/refresh")
def refresh(payload: RefreshRequest) -> dict[str, Any]:
    try:
        return service.refresh_session(payload.refresh_token)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.post("/api/v1/auth/logout", status_code=204)
def logout(authorization: str | None = Header(default=None)) -> Response:
    token = get_token_from_header(authorization)
    try:
        service.logout(token)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return Response(status_code=204)


@app.get("/api/v1/users")
def list_users(authorization: str | None = Header(default=None)) -> list[dict[str, str]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_users(token)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/users")
def create_user(
    payload: UserCreateRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)

    try:
        service.require_permission(token, "manage_users")
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc

    try:
        role = Role(payload.role)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="invalid role") from exc

    user = User(id=f"u-{service.user_count + 1}", email=payload.email, role=role)
    try:
        actor_user_id = service.validate_token(token)["user_id"]
        service.register_user(
            user,
            password=payload.password,
            actor_user_id=actor_user_id,
        )
    except ValueError as exc:
        status_code = 409 if str(exc) == "user already exists" else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return {"id": user.id, "email": user.email, "role": user.role.value}


@app.get("/api/v1/audit-events")
def list_audit_events(authorization: str | None = Header(default=None)) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_audit_events(token)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.get("/api/v1/audit-events/export")
def export_audit_events(
    format: str = "json",
    authorization: str | None = Header(default=None),
) -> Response:
    token = get_token_from_header(authorization)
    try:
        events = service.list_audit_events(token)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    if format == "json":
        return Response(json.dumps(events, ensure_ascii=False), media_type="application/json")
    if format != "csv":
        raise HTTPException(status_code=400, detail="format must be json or csv")
    output = StringIO()
    columns = [
        "id",
        "entity_type",
        "entity_id",
        "action",
        "actor_user_id",
        "performed_at",
        "previous_value",
        "new_value",
    ]
    writer = csv.DictWriter(output, fieldnames=columns)
    writer.writeheader()
    for event in events:
        writer.writerow(
            {
                **event,
                "previous_value": json.dumps(event["previous_value"], ensure_ascii=False),
                "new_value": json.dumps(event["new_value"], ensure_ascii=False),
            }
        )
    return Response(output.getvalue(), media_type="text/csv; charset=utf-8")


@app.post("/api/v1/projects", status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreateRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.create_project(
            token,
            title=payload.title,
            objective=payload.objective,
            study_type=payload.study_type,
            members=[member.model_dump() for member in payload.members],
        )
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/projects")
def list_projects(authorization: str | None = Header(default=None)) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_projects(token)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}")
def get_project(project_id: str, authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.get_project(token, project_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/configuration/{kind}/{document_key}", status_code=201)
def add_project_configuration(
    project_id: str,
    kind: str,
    document_key: str,
    payload: ProjectDocumentRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.add_project_document(
            token,
            project_id,
            kind=kind,
            key=document_key,
            data=payload.data,
        )
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/configuration")
def list_project_configuration(
    project_id: str,
    kind: str | None = None,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_project_documents(token, project_id, kind=kind)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/deviations", status_code=201)
def create_protocol_deviation(
    project_id: str,
    payload: ProtocolDeviationRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.add_protocol_deviation(token, project_id, **payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/deviations")
def list_protocol_deviations(
    project_id: str,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_protocol_deviations(token, project_id)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/search-executions", status_code=201)
def create_search_execution(
    project_id: str,
    payload: SearchExecutionRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.create_search_execution(token, project_id, **payload.model_dump())
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/search-executions/{search_execution_id}/imports", status_code=201)
async def import_search_results(
    search_execution_id: str,
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        content = await file.read(50 * 1024 * 1024 + 1)
        return service.import_search_results(
            token,
            search_execution_id,
            file_name=file.filename or "import",
            content=content,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/studies")
def list_project_studies(
    project_id: str,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_project_studies(token, project_id)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/deduplication/run")
def run_deduplication(
    project_id: str,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        candidates = service.run_deduplication(token, project_id)
        return {"candidates": candidates}
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/duplicate-candidates")
def list_duplicate_candidates(
    project_id: str,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_duplicate_candidates(token, project_id)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/duplicate-candidates/{candidate_id}/decision")
def decide_duplicate(
    candidate_id: str,
    payload: DuplicateDecisionRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.decide_duplicate(token, candidate_id, **payload.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/studies/{study_id}/triage-votes", status_code=201)
def submit_triage_vote(
    project_id: str,
    study_id: str,
    payload: TriageVoteRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.submit_triage_vote(token, project_id, study_id, **payload.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if str(exc).startswith("409:") else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/studies/{study_id}/triage-status")
def get_triage_status(
    project_id: str,
    study_id: str,
    phase: int = 1,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.get_triage_status(token, project_id, study_id, phase=phase)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/studies/{study_id}/quality-assessments", status_code=201)
def submit_quality_assessment(
    project_id: str,
    study_id: str,
    payload: QualityAssessmentRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.submit_quality_assessment(
            token,
            project_id,
            study_id,
            scores=[item.model_dump() for item in payload.scores],
            confirm=payload.confirm,
            expected_version=payload.expected_version,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if str(exc).startswith("409:") else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/studies/{study_id}/quality-status")
def get_quality_status(
    project_id: str,
    study_id: str,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.get_quality_status(token, project_id, study_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/studies/{study_id}/extractions", status_code=201)
def create_extraction(
    project_id: str,
    study_id: str,
    payload: ExtractionCreateRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.create_extraction(token, project_id, study_id, **payload.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        status_code = 409 if str(exc).startswith("409:") else 422
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/studies/{study_id}/extractions")
def list_study_extractions(
    project_id: str,
    study_id: str,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_study_extractions(token, project_id, study_id)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.post("/api/v1/extractions/{extraction_id}/verification", status_code=201)
def verify_extraction(
    extraction_id: str,
    payload: ExtractionVerificationRequest,
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.verify_extraction(token, extraction_id, **payload.model_dump())
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/api/v1/projects/{project_id}/artifacts/upload", status_code=201)
async def upload_artifact(
    project_id: str,
    file: UploadFile = File(...),
    authorization: str | None = Header(default=None),
) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        content = await file.read(100 * 1024 * 1024 + 1)
        return service.upload_artifact(
            token,
            project_id,
            file_name=file.filename or "",
            content=content,
            mime_type=file.content_type or "application/octet-stream",
        )
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/api/v1/projects/{project_id}/artifacts/{file_name:path}/versions")
def list_artifact_versions(
    project_id: str,
    file_name: str,
    authorization: str | None = Header(default=None),
) -> list[dict[str, Any]]:
    token = get_token_from_header(authorization)
    try:
        return service.list_artifact_versions(token, project_id, file_name)
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc


@app.get("/api/v1/artifacts/{artifact_id}/content")
def get_artifact_content(
    artifact_id: str,
    authorization: str | None = Header(default=None),
) -> Response:
    token = get_token_from_header(authorization)
    try:
        metadata, content = service.read_artifact(token, artifact_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return Response(
        content,
        media_type=metadata["mime_type"],
        headers={"Content-Disposition": f'attachment; filename="{metadata["file_name"]}"'},
    )


@app.get("/api/v1/me")
def me(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        return service.validate_token(token)
    except PermissionError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@app.get("/api/v1/protected")
def protected(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    token = get_token_from_header(authorization)
    try:
        service.require_permission(token, "review_study")
    except PermissionError as exc:
        raise HTTPException(status_code=permission_http_status(exc), detail=str(exc)) from exc

    return {"status": "ok", "message": "review access granted"}


app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")
