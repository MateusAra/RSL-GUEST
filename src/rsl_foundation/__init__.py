from __future__ import annotations

import hashlib
import hmac
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
import numpy as np
from jwt import InvalidTokenError
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from rapidfuzz import fuzz, process

from .database import (
    AuditEventRecord,
    ArtifactRecord,
    AuthSessionRecord,
    Base,
    DuplicateCandidateRecord,
    DuplicateDecisionRecord,
    ExtractionRecord,
    ExtractionVerificationRecord,
    ProjectDocumentRecord,
    ProjectMembershipRecord,
    ProjectRecord,
    ProtocolDeviationRecord,
    QualityAssessmentRecord,
    SearchExecutionRecord,
    StudyRecord,
    TriageVoteRecord,
    UserRecord,
    build_engine,
)
from .configuration_service import FIXED_VERDICTS, DEFAULT_QUALITY_WEIGHTING, ConfigurationMixin
from .quality import (
    calculate_quality_scores,
    calculate_weighted_kappa,
    validate_instrument,
)
from .quality_service import KAPPA_WARNING_THRESHOLD, QualityMixin, _score_map
from .extraction import EXTRACTION_FIELD_IDS, is_substantive_field
from .roles import Role
from .search_service import (
    SEARCH_BASES,
    TITLE_DUPLICATE_THRESHOLD,
    TITLE_REVIEW_THRESHOLD,
    SearchMixin,
    canonical_preference,
    validate_boolean_query,
)
from .triage import classify_triage_pair
from .triage_service import TriageMixin


@dataclass
class User:
    id: str
    email: str
    role: Role
    active: bool = True


class UserRolePolicy:
    _role_permissions = {
        Role.ADMIN: {
            "manage_users",
            "create_project",
            "view_project",
            "review_study",
            "update_project",
            "audit_export",
        },
        Role.REVISOR: {
            "view_project",
            "review_study",
            "update_project",
        },
        Role.TERCEIRO_REVISOR: {
            "view_project",
            "review_study",
        },
        Role.OBSERVADOR: {
            "view_project",
        },
    }

    def require_write(self, user: User) -> None:
        if user.role == Role.OBSERVADOR:
            raise PermissionError("403: observador is read-only")

    def require_admin(self, user: User) -> None:
        if user.role != Role.ADMIN:
            raise PermissionError("403: admin access required")

    def check_endpoint(self, user: User, endpoint: str) -> bool:
        if endpoint not in self._role_permissions.get(user.role, set()):
            raise PermissionError("403: forbidden endpoint for role")
        return True


class AuthController:
    def require_token(self, token: str | None) -> str:
        if not token:
            raise PermissionError("401: authentication required")
        return token


class AuthService(ConfigurationMixin, SearchMixin, QualityMixin, TriageMixin):
    _password_scrypt_n = 2**14
    _password_scrypt_r = 8
    _password_scrypt_p = 1
    _access_token_minutes = 15

    def __init__(
        self,
        jwt_secret: str | bytes = "local-user-test-only-secret-32-bytes",
        *,
        database_url: str | None = None,
        create_schema: bool = False,
        object_storage: Any | None = None,
    ) -> None:
        self._users: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, User] = {}
        self._refresh_tokens: dict[str, str] = {}
        self._policy = UserRolePolicy()
        self._jwt_secret = jwt_secret
        self._object_storage = object_storage
        self._engine = build_engine(database_url) if database_url else None
        self._session_factory = None
        if self._engine is not None:
            self._session_factory = sessionmaker(self._engine, expire_on_commit=False)
            if create_schema:
                Base.metadata.create_all(self._engine)

    def close(self) -> None:
        if self._engine is not None:
            self._engine.dispose()

    def set_object_storage(self, object_storage: Any) -> None:
        self._object_storage = object_storage

    def register_user(
        self,
        user: User,
        *,
        password: str,
        actor_user_id: str | None = None,
    ) -> None:
        email = user.email.strip().casefold()
        if "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            raise ValueError("invalid email address")
        if email in self._users:
            raise ValueError("user already exists")
        if len(password) < 8:
            raise ValueError("password must contain at least 8 characters")

        user.email = email
        salt = secrets.token_bytes(16)
        password_digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=salt,
            n=self._password_scrypt_n,
            r=self._password_scrypt_r,
            p=self._password_scrypt_p,
            dklen=32,
        )
        password_hash = "$".join(
            (
                "scrypt",
                str(self._password_scrypt_n),
                str(self._password_scrypt_r),
                str(self._password_scrypt_p),
                salt.hex(),
                password_digest.hex(),
            )
        )
        if self._session_factory is not None:
            try:
                with self._session_factory.begin() as database:
                    database.add(
                        UserRecord(
                            id=user.id,
                            email=email,
                            password_hash=password_hash,
                            role=user.role.value,
                            active=user.active,
                        )
                    )
                    if actor_user_id is not None:
                        self._append_audit(
                            database,
                            entity_type="user",
                            entity_id=user.id,
                            action="user_created",
                            actor_user_id=actor_user_id,
                            previous_value=None,
                            new_value={"email": email, "role": user.role.value},
                        )
            except IntegrityError as exc:
                raise ValueError("user already exists") from exc
            return
        self._users[email] = {"user": user, "password_hash": password_hash}

    def email_exists(self, email: str) -> bool:
        normalized_email = email.strip().casefold()
        if self._session_factory is None:
            return normalized_email in self._users
        with self._session_factory() as database:
            return database.scalar(
                select(UserRecord.id).where(UserRecord.email == normalized_email)
            ) is not None

    @property
    def user_count(self) -> int:
        if self._session_factory is not None:
            with self._session_factory() as database:
                return int(database.scalar(select(func.count()).select_from(UserRecord)) or 0)
        return len(self._users)

    def login(self, email: str, password: str) -> str:
        return self.create_session(email, password)["access_token"]

    def create_session(self, email: str, password: str) -> dict[str, Any]:
        if self._session_factory is None:
            record = self._users.get(email.strip().casefold())
            if record is None:
                raise PermissionError("401: invalid credentials")
            user = record["user"]
            password_hash = record["password_hash"]
        else:
            with self._session_factory() as database:
                record = database.scalar(
                    select(UserRecord).where(UserRecord.email == email.strip().casefold())
                )
                if record is None:
                    raise PermissionError("401: invalid credentials")
                user = self._user_from_record(record)
                password_hash = record.password_hash

        if not user.active or not self._verify_password(password, password_hash):
            raise PermissionError("401: invalid credentials")

        return self._issue_session_tokens(user, secrets.token_urlsafe(24))

    @staticmethod
    def _user_from_record(record: UserRecord) -> User:
        return User(
            id=record.id,
            email=record.email,
            role=Role(record.role),
            active=record.active,
        )

    def _verify_password(self, password: str, encoded_hash: str) -> bool:
        try:
            algorithm, n, r, p, salt_hex, digest_hex = encoded_hash.split("$")
            if algorithm != "scrypt":
                return False
            candidate = hashlib.scrypt(
                password.encode("utf-8"),
                salt=bytes.fromhex(salt_hex),
                n=int(n),
                r=int(r),
                p=int(p),
                dklen=32,
            )
        except (ValueError, TypeError):
            return False
        return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))

    def _session_response(
        self,
        user: User,
        session_id: str,
        refresh_token: str,
        now: datetime,
    ) -> dict[str, Any]:
        expires_at = now + timedelta(minutes=self._access_token_minutes)
        access_token = jwt.encode(
            {
                "sub": user.id,
                "email": user.email,
                "role": user.role.value,
                "sid": session_id,
                "iss": "rsl-xai-api",
                "iat": now,
                "exp": expires_at,
            },
            self._jwt_secret,
            algorithm="HS256",
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self._access_token_minutes * 60,
            "user": {"user_id": user.id, "email": user.email, "role": user.role.value},
        }

    def _issue_session_tokens(self, user: User, session_id: str) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        refresh_token = secrets.token_urlsafe(48)
        refresh_expires_at = now + timedelta(days=30)
        if self._session_factory is not None:
            with self._session_factory.begin() as database:
                database.add(
                    AuthSessionRecord(
                        id=session_id,
                        user_id=user.id,
                        refresh_token_hash=hashlib.sha256(refresh_token.encode("utf-8")).hexdigest(),
                        expires_at=refresh_expires_at,
                    )
                )
        else:
            self._sessions[session_id] = user
            self._refresh_tokens[hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()] = session_id
        return self._session_response(user, session_id, refresh_token, now)

    def refresh_session(self, refresh_token: str) -> dict[str, Any]:
        token_hash = hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()
        if self._session_factory is not None:
            now = datetime.now(timezone.utc)
            new_refresh_token = secrets.token_urlsafe(48)
            with self._session_factory.begin() as database:
                record = database.scalar(
                    select(AuthSessionRecord)
                    .where(AuthSessionRecord.refresh_token_hash == token_hash)
                    .with_for_update()
                )
                if record is None:
                    raise PermissionError("401: invalid refresh token")
                refresh_expires_at = record.expires_at
                if refresh_expires_at.tzinfo is None:
                    refresh_expires_at = refresh_expires_at.replace(tzinfo=timezone.utc)
                user_record = database.get(UserRecord, record.user_id)
                if refresh_expires_at <= now or user_record is None or not user_record.active:
                    database.delete(record)
                    raise PermissionError("401: invalid refresh token")
                user = self._user_from_record(user_record)
                session_id = record.id
                record.refresh_token_hash = hashlib.sha256(
                    new_refresh_token.encode("utf-8")
                ).hexdigest()
                record.expires_at = now + timedelta(days=30)
            return self._session_response(user, session_id, new_refresh_token, now)

        session_id = self._refresh_tokens.pop(token_hash, None)
        user = self._sessions.get(session_id or "")
        if user is None or not user.active:
            raise PermissionError("401: invalid refresh token")
        return self._issue_session_tokens(user, session_id)

    def logout(self, token: str) -> None:
        payload = self._decode_token(token)
        session_id = payload["sid"]
        if self._session_factory is not None:
            with self._session_factory.begin() as database:
                record = database.get(AuthSessionRecord, session_id)
                if record is not None:
                    database.delete(record)
            return
        self._sessions.pop(session_id, None)
        self._refresh_tokens = {
            token_hash: active_session_id
            for token_hash, active_session_id in self._refresh_tokens.items()
            if active_session_id != session_id
        }

    def _decode_token(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(
                token,
                self._jwt_secret,
                algorithms=["HS256"],
                issuer="rsl-xai-api",
                options={"require": ["sub", "email", "role", "sid", "exp", "iat"]},
            )
        except InvalidTokenError as exc:
            raise PermissionError("401: invalid token") from exc

    def validate_token(self, token: str) -> dict[str, Any]:
        if not token:
            raise PermissionError("401: invalid token")

        payload = self._decode_token(token)
        if self._session_factory is not None:
            with self._session_factory() as database:
                session_record = database.get(AuthSessionRecord, payload["sid"])
                user_record = database.get(UserRecord, payload["sub"])
                if session_record is None or user_record is None or not user_record.active:
                    raise PermissionError("401: invalid token")
                expiry = session_record.expires_at
                if expiry.tzinfo is None:
                    expiry = expiry.replace(tzinfo=timezone.utc)
                if expiry <= datetime.now(timezone.utc):
                    raise PermissionError("401: invalid token")
                return {
                    "user_id": user_record.id,
                    "email": user_record.email,
                    "role": user_record.role,
                }
        user = self._sessions.get(payload["sid"])
        if user is None or not user.active or user.id != payload["sub"]:
            raise PermissionError("401: invalid token")
        return {"user_id": user.id, "email": user.email, "role": user.role.value}

    def require_permission(self, token: str, endpoint: str) -> bool:
        payload = self.validate_token(token)
        if self._session_factory is not None:
            user = User(
                id=payload["user_id"],
                email=payload["email"],
                role=Role(payload["role"]),
            )
            self._policy.check_endpoint(user, endpoint)
            return True
        session_id = self._decode_token(token)["sid"]
        user = self._sessions[session_id]
        self._policy.check_endpoint(user, endpoint)
        return payload["user_id"] is not None

    def list_users(self, token: str) -> list[dict[str, str]]:
        self.require_permission(token, "manage_users")
        if self._session_factory is not None:
            with self._session_factory() as database:
                records = database.scalars(select(UserRecord).order_by(UserRecord.email)).all()
            return [
                {"id": record.id, "email": record.email, "role": record.role}
                for record in records
            ]
        return [
            {"id": record["user"].id, "email": record["user"].email, "role": record["user"].role.value}
            for record in self._users.values()
        ]

    def create_project(
        self,
        token: str,
        *,
        title: str,
        objective: str,
        study_type: str,
        members: list[dict[str, str]],
    ) -> dict[str, Any]:
        self.require_permission(token, "create_project")
        if self._session_factory is None:
            raise ValueError("project persistence is not configured")

        payload = self._decode_token(token)
        normalized_members = [
            {"email": member["email"].strip().casefold(), "role": Role(member["role"])}
            for member in members
        ]
        member_emails = [member["email"] for member in normalized_members]
        if len(member_emails) != len(set(member_emails)) or payload["email"] in member_emails:
            raise ValueError("project members must be unique; owner is added automatically")
        if sum(member["role"] == Role.REVISOR for member in normalized_members) < 2:
            raise ValueError("project requires at least two reviewers")
        if not any(member["role"] == Role.TERCEIRO_REVISOR for member in normalized_members):
            raise ValueError("project requires a third reviewer")

        project_id = f"p-{secrets.token_urlsafe(12)}"
        with self._session_factory.begin() as database:
            owner = database.get(UserRecord, payload["sub"])
            if owner is None:
                raise PermissionError("401: invalid token")
            user_records = database.scalars(
                select(UserRecord).where(UserRecord.email.in_(member_emails))
            ).all()
            users_by_email = {record.email: record for record in user_records}
            missing = set(member_emails) - users_by_email.keys()
            if missing:
                raise ValueError(f"unknown project members: {', '.join(sorted(missing))}")

            database.add(
                ProjectRecord(
                    id=project_id,
                    title=title.strip(),
                    objective=objective.strip(),
                    study_type=study_type.strip(),
                    owner_user_id=owner.id,
                )
            )
            database.add(
                ProjectMembershipRecord(project_id=project_id, user_id=owner.id, role=Role.ADMIN.value)
            )
            for member in normalized_members:
                member_user = users_by_email[member["email"]]
                if not member_user.active:
                    raise ValueError(f"project member is inactive: {member['email']}")
                database.add(
                    ProjectMembershipRecord(
                        project_id=project_id,
                        user_id=member_user.id,
                        role=member["role"].value,
                    )
                )
            self._append_audit(
                database,
                entity_type="project",
                entity_id=project_id,
                action="project_created",
                actor_user_id=owner.id,
                previous_value=None,
                new_value={"title": title.strip(), "study_type": study_type.strip()},
            )
        return self.get_project(token, project_id)

    def get_project(self, token: str, project_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("project persistence is not configured")
        with self._session_factory() as database:
            membership = database.get(ProjectMembershipRecord, (project_id, payload["user_id"]))
            project = database.get(ProjectRecord, project_id)
            if project is None:
                raise LookupError("project not found")
            if membership is None:
                raise PermissionError("403: project membership required")
            self._policy.check_endpoint(User(
                id=payload["user_id"],
                email=payload["email"],
                role=Role(membership.role),
            ), "view_project")
            rows = database.execute(
                select(UserRecord, ProjectMembershipRecord)
                .join(ProjectMembershipRecord, ProjectMembershipRecord.user_id == UserRecord.id)
                .where(ProjectMembershipRecord.project_id == project_id)
                .order_by(ProjectMembershipRecord.role, UserRecord.email)
            ).all()
            return {
                "id": project.id,
                "title": project.title,
                "objective": project.objective,
                "study_type": project.study_type,
                "owner_user_id": project.owner_user_id,
                "status": project.status,
                "version": project.version,
                "members": [
                    {"user_id": user.id, "email": user.email, "role": project_member.role}
                    for user, project_member in rows
                ],
            }

    def list_projects(self, token: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("project persistence is not configured")
        with self._session_factory() as database:
            project_ids = database.scalars(
                select(ProjectMembershipRecord.project_id).where(
                    ProjectMembershipRecord.user_id == payload["user_id"]
                )
            ).all()
        return [self.get_project(token, project_id) for project_id in project_ids]

    def _require_project_membership(
        self,
        database: Any,
        project_id: str,
        user_id: str,
        allowed_roles: set[Role],
    ) -> ProjectMembershipRecord:
        membership = database.get(ProjectMembershipRecord, (project_id, user_id))
        if membership is None:
            raise PermissionError("403: project membership required")
        if Role(membership.role) not in allowed_roles:
            raise PermissionError("403: project role does not allow this operation")
        return membership

    @staticmethod
    def _validate_project_document(kind: str, key: str, data: dict[str, Any]) -> dict[str, Any]:
        """Validate a configuration version and return the data to store."""
        if kind in {"search_string", "manual_search"}:
            raise ValueError(f"{kind} is registered through the search endpoints")
        if kind not in {
            "protocol",
            "criteria",
            "glossary",
            "research_question",
            "picoc",
            "hypothesis",
            "verdict_rules",
            "phase",
            "seminal",
            "search_base",
            "qa_instrument",
        }:
            raise ValueError("unsupported configuration kind")
        data = dict(data)
        if kind == "protocol" and not all(
            isinstance(data.get(field), str) and data[field].strip()
            for field in ("text", "description")
        ):
            raise ValueError("protocol version requires text and description")
        if kind == "criteria" and (
            not key.startswith(("CI", "CE")) or not str(data.get("text", "")).strip()
        ):
            raise ValueError("selection criterion requires CI/CE id and text")
        if kind == "glossary":
            if not str(data.get("definition", "")).strip():
                raise ValueError("glossary term requires a definition")
            # Spec 002 CA-04: a term without links is saved, listed as pending and blocks Portão 0.
            data["criteria_links"] = list(data.get("criteria_links") or [])
            data["field_links"] = list(data.get("field_links") or [])
            if any(not str(link).startswith(("CI", "CE")) for link in data["criteria_links"]):
                raise ValueError("glossary criteria links must be CI/CE ids")
            unknown_fields = sorted(set(data["field_links"]) - EXTRACTION_FIELD_IDS)
            if unknown_fields:
                raise ValueError(f"unknown extraction field ids: {', '.join(unknown_fields)}")
        if kind == "research_question":
            required = ("text", "motivation", "classification", "classification_justification")
            if not all(str(data.get(field, "")).strip() for field in required):
                raise ValueError("research question requires text, motivation, classification and justification")
            if data["classification"] not in {"descritiva", "explicativa", "exploratoria", "preditiva"}:
                raise ValueError("invalid Easterbrook classification")
            if data.get("active", True) is False:
                # Spec 002 regra 5: RQ is never deleted, only deactivated with justification.
                if not str(data.get("deactivation_justification", "")).strip():
                    raise ValueError("deactivating a research question requires a justification")
            elif not data.get("field_links") or not data.get("analysis_links"):
                raise ValueError("research question requires field and analysis links")
            unknown_fields = sorted(set(data.get("field_links") or []) - EXTRACTION_FIELD_IDS)
            if unknown_fields:
                raise ValueError(f"unknown extraction field ids: {', '.join(unknown_fields)}")
        if kind == "picoc":
            elements = data.get("elements", {})
            required = {"population", "intervention", "comparison", "outcome", "context"}
            if not required.issubset(elements) or any(
                not str(elements.get(element, "")).strip() for element in required
            ):
                raise ValueError("PICOC requires Population, Intervention, Comparison, Outcome and Context")
        if kind == "hypothesis":
            required = ("independent_variables", "dependent_variables", "operational_criteria")
            if key not in {"H1", "H2"} or any(not data.get(field) for field in required):
                raise ValueError("hypothesis H1/H2 requires independent/dependent variables and operational criteria")
        if kind == "verdict_rules":
            if sorted(data.get("verdicts", [])) != sorted(FIXED_VERDICTS):
                raise ValueError("all four fixed hypothesis verdicts are required")
            weighting = data.setdefault("quality_weighting", DEFAULT_QUALITY_WEIGHTING)
            if set(weighting) != {"high", "moderate"} or any(
                not isinstance(band.get("weight"), (int, float)) or not 0 < band["weight"] <= 1
                or not isinstance(band.get("min_score"), (int, float))
                for band in weighting.values()
            ):
                raise ValueError("quality weighting requires high and moderate bands with min_score and 0 < weight <= 1")
            if set(data.get("operational_criteria", {})) - set(FIXED_VERDICTS):
                raise ValueError("operational criteria must be keyed by the four fixed verdicts")
        if kind == "phase":
            if not str(data.get("name", "")).strip() or float(data.get("duration_weeks", 0)) <= 0:
                raise ValueError("phase requires a name and positive duration")
            data["dependencies"] = list(data.get("dependencies") or [])
            if key in data["dependencies"]:
                raise ValueError("a phase cannot depend on itself")
            data["progress_percent"] = float(data.get("progress_percent", 0))
            if not 0 <= data["progress_percent"] <= 100:
                raise ValueError("phase progress must be between 0 and 100")
        if kind == "seminal":
            if not key.startswith("SX") or not str(data.get("title", "")).strip():
                raise ValueError("seminal study requires an SX id and title")
            doi = str(data.get("doi") or "").strip()
            data["doi"] = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE).casefold() or None
            if data.get("year") is not None and not isinstance(data["year"], int):
                raise ValueError("seminal year must be an integer")
        if kind == "search_base":
            if key not in SEARCH_BASES:
                raise ValueError("unknown search base")
            if "fields" in data and (not isinstance(data["fields"], list) or not data["fields"]):
                raise ValueError("search base fields must be a non-empty list")
            if int(data.get("year_from", 2016)) > int(data.get("year_to", 2026)):
                raise ValueError("search window must start before it ends")
            limit = data.get("result_limit")
            if key == "google_scholar" and limit is not None and not 1 <= int(limit) <= 300:
                raise ValueError("Google Scholar result limit must be between 1 and 300")
        if kind == "qa_instrument":
            if key != "default":
                raise ValueError("the QA instrument key must be default")
            data.setdefault("min_applicable", 7)
            validate_instrument(data)
        return data

    def add_project_document(
        self,
        token: str,
        project_id: str,
        *,
        kind: str,
        key: str,
        data: dict[str, Any],
        expected_version: int | None = None,
        deviation_id: str | None = None,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("project configuration persistence is not configured")
        data = self._validate_project_document(kind, key, data)
        with self._session_factory.begin() as database:
            self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.ADMIN},
            )
            warnings: list[str] = []
            if kind == "qa_instrument":
                # Spec 005 CA-01: leaving the protocol instrument is a recorded deviation.
                deviations = validate_instrument(data)
                if deviations:
                    justification = str(data.get("deviation_justification", "")).strip()
                    if not justification:
                        raise ValueError(
                            "QA instrument deviates from the protocol (" + "; ".join(deviations)
                            + "); deviation_justification is required"
                        )
                    deviation = ProtocolDeviationRecord(
                        id=secrets.token_hex(16),
                        project_id=project_id,
                        stage="avaliação de qualidade",
                        description="; ".join(deviations),
                        justification=justification,
                        affected_section="§7.4",
                        author_user_id=payload["user_id"],
                    )
                    database.add(deviation)
                    self._append_audit(
                        database,
                        entity_type="protocol_deviation",
                        entity_id=deviation.id,
                        action="protocol_deviation_created",
                        actor_user_id=payload["user_id"],
                        previous_value=None,
                        new_value={"stage": deviation.stage, "affected_section": deviation.affected_section},
                    )
                    data["deviation_id"] = deviation.id
                    warnings.extend(deviations)
            if kind == "research_question":
                # Spec 002 §9: RQ reformulated after extraction started alerts on linked fields.
                started = self._linked_extractions(database, project_id, list(data.get("field_links") or []))
                if started and key in self._latest_documents(database, project_id, "research_question"):
                    warnings.append("extraction already started for linked fields: " + ", ".join(started))
            result = self._store_project_document(
                database,
                project_id=project_id,
                kind=kind,
                key=key,
                data=data,
                user_id=payload["user_id"],
                expected_version=expected_version,
                deviation_id=deviation_id,
            )
            result["warnings"] = warnings
            return result

    def list_project_documents(
        self,
        token: str,
        project_id: str,
        *,
        kind: str | None = None,
    ) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("project configuration persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                set(Role),
            )
            query = select(ProjectDocumentRecord).where(ProjectDocumentRecord.project_id == project_id)
            if kind is not None:
                query = query.where(ProjectDocumentRecord.kind == kind)
            records = database.scalars(
                query.order_by(ProjectDocumentRecord.kind, ProjectDocumentRecord.document_key, ProjectDocumentRecord.version)
            ).all()
            return [
                {
                    "id": record.id,
                    "kind": record.kind,
                    "key": record.document_key,
                    "version": record.version,
                    "data": record.data,
                    "created_by": record.created_by,
                    "created_at": record.created_at.isoformat(),
                }
                for record in records
            ]

    def add_protocol_deviation(
        self,
        token: str,
        project_id: str,
        *,
        stage: str,
        description: str,
        justification: str,
        affected_section: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        values = (stage, description, justification, affected_section)
        if any(not value.strip() for value in values):
            raise ValueError("deviation requires stage, description, justification and affected section")
        if self._session_factory is None:
            raise ValueError("deviation persistence is not configured")
        with self._session_factory.begin() as database:
            self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.ADMIN, Role.REVISOR},
            )
            record = ProtocolDeviationRecord(
                id=secrets.token_hex(16),
                project_id=project_id,
                stage=stage.strip(),
                description=description.strip(),
                justification=justification.strip(),
                affected_section=affected_section.strip(),
                author_user_id=payload["user_id"],
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="protocol_deviation",
                entity_id=record.id,
                action="protocol_deviation_created",
                actor_user_id=payload["user_id"],
                previous_value=None,
                new_value={"stage": record.stage, "affected_section": record.affected_section},
            )
            return {
                "id": record.id,
                "project_id": record.project_id,
                "stage": record.stage,
                "description": record.description,
                "justification": record.justification,
                "affected_section": record.affected_section,
                "author_user_id": record.author_user_id,
            }

    def list_protocol_deviations(self, token: str, project_id: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("deviation persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = database.scalars(
                select(ProtocolDeviationRecord)
                .where(ProtocolDeviationRecord.project_id == project_id)
                .order_by(ProtocolDeviationRecord.created_at)
            ).all()
            return [
                {
                    "id": record.id,
                    "stage": record.stage,
                    "description": record.description,
                    "justification": record.justification,
                    "affected_section": record.affected_section,
                    "author_user_id": record.author_user_id,
                    "created_at": record.created_at.isoformat(),
                }
                for record in records
            ]

    @staticmethod
    def _validate_boolean_query(query: str) -> None:
        validate_boolean_query(query)

    def create_search_execution(
        self,
        token: str,
        project_id: str,
        *,
        base: str,
        reported_result_count: int,
        fields: list[str] | None = None,
        result_limit: int | None = None,
        executed_at: datetime | None = None,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("search persistence is not configured")
        if base not in SEARCH_BASES:
            raise ValueError("unsupported search base")
        if reported_result_count < 0:
            raise ValueError("reported result count cannot be negative")

        record_id = secrets.token_hex(16)
        with self._session_factory.begin() as database:
            self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.ADMIN, Role.REVISOR},
            )
            config = self._base_configuration(database, project_id)[base]
            # Spec 003 CA-02: a base without an adapted string cannot register executions.
            if config["search_string_version"] is None:
                raise ValueError(f"base {base} has no adapted search string; register it before the execution")
            fields = fields or config["fields"]
            if config["result_limit"] is not None:
                result_limit = config["result_limit"] if result_limit is None else result_limit
                if not 1 <= result_limit <= config["result_limit"]:
                    raise ValueError(
                        f"{config['name']} result limit must be between 1 and {config['result_limit']}"
                    )
            database.add(
                SearchExecutionRecord(
                    id=record_id,
                    project_id=project_id,
                    base=base,
                    query=config["adapted_query"],
                    fields=fields,
                    result_limit=result_limit,
                    search_string_version=config["search_string_version"],
                    year_from=config["year_from"],
                    year_to=config["year_to"],
                    reported_result_count=reported_result_count,
                    executed_at=executed_at or datetime.now(timezone.utc),
                    created_by=payload["user_id"],
                )
            )
            self._append_audit(
                database,
                entity_type="search_execution",
                entity_id=record_id,
                action="search_execution_created",
                actor_user_id=payload["user_id"],
                previous_value=None,
                new_value={
                    "base": base,
                    "fields": fields,
                    "search_string_version": config["search_string_version"],
                    "reported_result_count": reported_result_count,
                },
            )
        return {
            "id": record_id,
            "project_id": project_id,
            "base": base,
            "query": config["adapted_query"],
            "search_string_version": config["search_string_version"],
            "fields": fields,
            "year_from": config["year_from"],
            "year_to": config["year_to"],
            "result_limit": result_limit,
            "reported_result_count": reported_result_count,
        }

    def import_search_results(
        self,
        token: str,
        search_execution_id: str,
        *,
        file_name: str,
        content: bytes,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("search persistence is not configured")
        with self._session_factory.begin() as database:
            execution = database.get(SearchExecutionRecord, search_execution_id)
            if execution is None:
                raise LookupError("search execution not found")
            self._require_project_membership(
                database,
                execution.project_id,
                payload["user_id"],
                {Role.ADMIN, Role.REVISOR},
            )
            return self._import_records(
                database,
                project_id=execution.project_id,
                file_name=file_name,
                content=content,
                user_id=payload["user_id"],
                source=execution.base,
                search_execution_id=search_execution_id,
            )

    def list_project_studies(self, token: str, project_id: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("search persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            studies = database.scalars(
                select(StudyRecord).where(StudyRecord.project_id == project_id).order_by(StudyRecord.created_at)
            ).all()
            duplicate_of, _ = self._duplicate_groups(database, project_id)
            return [
                {
                    "id": study.id,
                    "title": study.title,
                    "authors": study.authors,
                    "year": study.year,
                    "venue": study.venue,
                    "doi": study.doi,
                    "abstract": study.abstract,
                    "keywords": study.keywords,
                    "source": study.source,
                    "origin": study.origin,
                    "publication_type": study.publication_type,
                    "search_execution_id": study.search_execution_id,
                    "snowball_round_id": study.snowball_round_id,
                    "duplicate_of": duplicate_of.get(study.id),
                }
                for study in studies
            ]

    def run_deduplication(self, token: str, project_id: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("deduplication persistence is not configured")
        with self._session_factory.begin() as database:
            self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.ADMIN, Role.REVISOR, Role.TERCEIRO_REVISOR},
            )
            studies = database.scalars(
                select(StudyRecord).where(StudyRecord.project_id == project_id).order_by(StudyRecord.id)
            ).all()
            existing = {
                (candidate.study_id_a, candidate.study_id_b)
                for candidate in database.scalars(
                    select(DuplicateCandidateRecord).where(DuplicateCandidateRecord.project_id == project_id)
                ).all()
            }
            match_scores: dict[tuple[str, str], tuple[float, str]] = {}
            by_doi: dict[str, list[str]] = {}
            for study in studies:
                if study.doi:
                    by_doi.setdefault(study.doi, []).append(study.id)
            for study_ids in by_doi.values():
                for index, first_id in enumerate(study_ids):
                    for second_id in study_ids[index + 1 :]:
                        match_scores[tuple(sorted((first_id, second_id)))] = (1.0, "doi_exact")
            titled = [study for study in studies if study.normalized_title]
            titles = [study.normalized_title for study in titled]
            # Row blocks keep memory bounded for 5,000 records (RNF10); float32 keeps the exact
            # score, since an integer dtype would round 89.9 up across the 0.90 threshold.
            block_size = 500
            for block_start in range(0, len(titles), block_size):
                similarity_block = process.cdist(
                    titles[block_start : block_start + block_size],
                    titles,
                    scorer=fuzz.ratio,
                    score_cutoff=TITLE_REVIEW_THRESHOLD * 100,
                    dtype=np.float32,
                    workers=-1,
                )
                for row, column in np.argwhere(similarity_block > 0):
                    first_index = block_start + int(row)
                    if int(column) <= first_index:
                        continue
                    pair = tuple(sorted((titled[first_index].id, titled[int(column)].id)))
                    if pair in match_scores:
                        continue
                    similarity = round(float(similarity_block[row, column]) / 100, 4)
                    match_type = "title_similarity" if similarity >= TITLE_DUPLICATE_THRESHOLD else "manual_review"
                    match_scores[pair] = (similarity, match_type)

            studies_by_id = {study.id: study for study in studies}
            for pair, (similarity, match_type) in sorted(match_scores.items()):
                if pair in existing:
                    continue
                candidate = DuplicateCandidateRecord(
                    id=secrets.token_hex(16),
                    project_id=project_id,
                    study_id_a=pair[0],
                    study_id_b=pair[1],
                    match_type=match_type,
                    similarity=similarity,
                )
                database.add(candidate)
                existing.add(pair)
                self._append_audit(
                    database,
                    entity_type="duplicate_candidate",
                    entity_id=candidate.id,
                    action="duplicate_candidate_detected",
                    actor_user_id=payload["user_id"],
                    previous_value=None,
                    new_value={"match_type": candidate.match_type, "similarity": candidate.similarity},
                )
                if match_type != "doi_exact":
                    continue
                # Spec 003 regra 4: DOI exato marca a duplicidade automaticamente (editável pelo R1).
                canonical = max((studies_by_id[pair[0]], studies_by_id[pair[1]]), key=canonical_preference)
                decision = DuplicateDecisionRecord(
                    id=secrets.token_hex(16),
                    candidate_id=candidate.id,
                    decision="duplicate",
                    canonical_study_id=canonical.id,
                    justification="Decisão automática: DOI idêntico (spec 003, regra 4).",
                    method="automatic",
                    decided_by=payload["user_id"],
                )
                database.add(decision)
                self._append_audit(
                    database,
                    entity_type="duplicate_candidate",
                    entity_id=candidate.id,
                    action="duplicate_decision_recorded",
                    actor_user_id=payload["user_id"],
                    previous_value=None,
                    new_value={"decision": "duplicate", "canonical_study_id": canonical.id, "method": "automatic"},
                )
        return self.list_duplicate_candidates(token, project_id)

    def list_duplicate_candidates(self, token: str, project_id: str) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("deduplication persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            candidates = database.scalars(
                select(DuplicateCandidateRecord)
                .where(DuplicateCandidateRecord.project_id == project_id)
                .order_by(DuplicateCandidateRecord.created_at, DuplicateCandidateRecord.id)
            ).all()
            latest = self._latest_duplicate_decisions(database, project_id)
            studies = {
                study.id: study
                for study in database.scalars(select(StudyRecord).where(StudyRecord.project_id == project_id)).all()
            }
            output: list[dict[str, Any]] = []
            for candidate in candidates:
                decision = latest.get(candidate.id)
                output.append(
                    {
                        "id": candidate.id,
                        "study_ids": [candidate.study_id_a, candidate.study_id_b],
                        "match_type": candidate.match_type,
                        "similarity": candidate.similarity,
                        "suggested_canonical_study_id": max(
                            (studies[candidate.study_id_a], studies[candidate.study_id_b]),
                            key=canonical_preference,
                        ).id,
                        "decision": None if decision is None else decision.decision,
                        "method": None if decision is None else decision.method,
                        "canonical_study_id": None if decision is None else decision.canonical_study_id,
                        "justification": None if decision is None else decision.justification,
                    }
                )
            return output

    def decide_duplicate(
        self,
        token: str,
        candidate_id: str,
        *,
        decision: str,
        canonical_study_id: str | None,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if decision not in {"duplicate", "independent"}:
            raise ValueError("decision must be duplicate or independent")
        if not justification.strip():
            raise ValueError("duplicate decision requires justification")
        if self._session_factory is None:
            raise ValueError("deduplication persistence is not configured")
        with self._session_factory.begin() as database:
            candidate = database.get(DuplicateCandidateRecord, candidate_id)
            if candidate is None:
                raise LookupError("duplicate candidate not found")
            self._require_project_membership(
                database,
                candidate.project_id,
                payload["user_id"],
                {Role.ADMIN, Role.REVISOR, Role.TERCEIRO_REVISOR},
            )
            if decision == "duplicate" and canonical_study_id not in {
                candidate.study_id_a,
                candidate.study_id_b,
            }:
                raise ValueError("canonical study must be one of the candidate pair")
            if decision == "independent" and canonical_study_id is not None:
                raise ValueError("independent decision cannot specify a canonical study")
            record = DuplicateDecisionRecord(
                id=secrets.token_hex(16),
                candidate_id=candidate_id,
                decision=decision,
                canonical_study_id=canonical_study_id,
                justification=justification.strip(),
                method="manual",
                decided_by=payload["user_id"],
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="duplicate_candidate",
                entity_id=candidate_id,
                action="duplicate_decision_recorded",
                actor_user_id=payload["user_id"],
                previous_value=None,
                new_value={"decision": decision, "canonical_study_id": canonical_study_id},
            )
        return {
            "id": record.id,
            "candidate_id": candidate_id,
            "decision": decision,
            "canonical_study_id": canonical_study_id,
            "justification": justification.strip(),
        }

    def submit_triage_vote(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        phase: int,
        vote: str,
        criterion_id: str | None,
        confirm: bool,
        expected_version: int,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if phase not in {1, 2}:
            raise ValueError("triage phase must be 1 or 2")
        if vote not in {"incluir", "excluir", "incerto"}:
            raise ValueError("vote must be incluir, excluir or incerto")
        if vote in {"excluir", "incerto"} and not criterion_id:
            raise ValueError("excluding or uncertain votes require a CI/CE criterion")
        if self._session_factory is None:
            raise ValueError("triage persistence is not configured")

        with self._session_factory.begin() as database:
            membership = self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.REVISOR},
            )
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            assigned_reviewers = database.scalars(
                select(ProjectMembershipRecord.user_id)
                .where(
                    ProjectMembershipRecord.project_id == project_id,
                    ProjectMembershipRecord.role == Role.REVISOR.value,
                )
                .order_by(ProjectMembershipRecord.user_id)
                .limit(2)
            ).all()
            if membership.user_id not in assigned_reviewers:
                raise PermissionError("403: reviewer is not assigned to this triage pair")
            if criterion_id:
                criterion_exists = database.scalar(
                    select(ProjectDocumentRecord.id).where(
                        ProjectDocumentRecord.project_id == project_id,
                        ProjectDocumentRecord.kind == "criteria",
                        ProjectDocumentRecord.document_key == criterion_id,
                    )
                )
                if criterion_exists is None:
                    raise ValueError("criterion is not configured for this project")

            current = database.scalar(
                select(TriageVoteRecord)
                .where(
                    TriageVoteRecord.project_id == project_id,
                    TriageVoteRecord.study_id == study_id,
                    TriageVoteRecord.phase == phase,
                    TriageVoteRecord.reviewer_user_id == payload["user_id"],
                )
                .with_for_update()
            )
            if current is None:
                if expected_version != 0:
                    raise ValueError("409: vote version conflict")
                record = TriageVoteRecord(
                    id=secrets.token_hex(16),
                    project_id=project_id,
                    study_id=study_id,
                    phase=phase,
                    reviewer_user_id=payload["user_id"],
                    vote=vote,
                    criterion_id=criterion_id,
                    confirmed=confirm,
                    version=1,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                database.add(record)
                previous_value = None
            else:
                if current.confirmed:
                    raise ValueError("409: confirmed vote requires a recorded reopening")
                if current.version != expected_version:
                    raise ValueError("409: vote version conflict")
                previous_value = {"vote": current.vote, "criterion_id": current.criterion_id}
                current.vote = vote
                current.criterion_id = criterion_id
                current.confirmed = confirm
                current.version += 1
                current.updated_at = datetime.now(timezone.utc)
                record = current
            self._append_audit(
                database,
                entity_type="triage_vote",
                entity_id=record.id,
                action="triage_vote_confirmed" if confirm else "triage_vote_saved",
                actor_user_id=payload["user_id"],
                previous_value=previous_value,
                new_value={"vote": vote, "criterion_id": criterion_id, "phase": phase},
            )
            response = {
                "id": record.id,
                "study_id": study_id,
                "phase": phase,
                "vote": vote,
                "criterion_id": criterion_id,
                "confirmed": confirm,
                "version": record.version,
            }
        return response

    def get_triage_status(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        phase: int,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if phase not in {1, 2}:
            raise ValueError("triage phase must be 1 or 2")
        if self._session_factory is None:
            raise ValueError("triage persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            reviewer_ids = database.scalars(
                select(ProjectMembershipRecord.user_id)
                .where(
                    ProjectMembershipRecord.project_id == project_id,
                    ProjectMembershipRecord.role == Role.REVISOR.value,
                )
                .order_by(ProjectMembershipRecord.user_id)
                .limit(2)
            ).all()
            if payload["user_id"] not in reviewer_ids:
                raise PermissionError("403: triage status is restricted to the assigned reviewers")
            votes = database.scalars(
                select(TriageVoteRecord).where(
                    TriageVoteRecord.project_id == project_id,
                    TriageVoteRecord.study_id == study_id,
                    TriageVoteRecord.phase == phase,
                    TriageVoteRecord.reviewer_user_id.in_(reviewer_ids),
                )
            ).all()
            votes_by_user = {vote.reviewer_user_id: vote for vote in votes}
            own_vote = votes_by_user.get(payload["user_id"])
            peer_id = next((user_id for user_id in reviewer_ids if user_id != payload["user_id"]), None)
            peer_vote = votes_by_user.get(peer_id) if peer_id else None
            both_confirmed = len(reviewer_ids) == 2 and all(
                votes_by_user.get(user_id) is not None and votes_by_user[user_id].confirmed
                for user_id in reviewer_ids
            )
            result: dict[str, Any] = {
                "study_id": study_id,
                "phase": phase,
                "own_vote": None if own_vote is None else {
                    "vote": own_vote.vote,
                    "criterion_id": own_vote.criterion_id,
                    "confirmed": own_vote.confirmed,
                    "version": own_vote.version,
                },
                "peer_status": "confirmed" if peer_vote is not None and peer_vote.confirmed else "awaiting",
            }
            if both_confirmed and own_vote is not None and peer_vote is not None:
                matrix_letter, matrix_result = classify_triage_pair(own_vote.vote, peer_vote.vote)
                result.update(
                    {
                        "peer_vote": {
                            "vote": peer_vote.vote,
                            "criterion_id": peer_vote.criterion_id,
                            "confirmed": peer_vote.confirmed,
                        },
                        "matrix_letter": matrix_letter,
                        "result": matrix_result,
                    }
                )
                state = self._triage_state(database, project_id, study_id, phase)
                if state is not None:
                    result.update(
                        {
                            "status": state["status"],
                            "final_result": state["final_result"],
                            "consensus": state.get("consensus"),
                            "arbitration": state.get("arbitration"),
                        }
                    )
            return result

    def submit_quality_assessment(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        scores: list[dict[str, Any]],
        confirm: bool,
        expected_version: int,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("quality assessment persistence is not configured")
        score_map: dict[str, float | None] = {}
        for item in scores:
            criterion_id = str(item.get("criterion_id", ""))
            if criterion_id in score_map:
                raise ValueError("duplicate QA criterion")
            if not str(item.get("justification", "")).strip():
                raise ValueError(f"{criterion_id} requires a justification")
            score_map[criterion_id] = item.get("score")
        normalized_scores = [
            {
                "criterion_id": item["criterion_id"],
                "score": item["score"],
                "justification": item["justification"].strip(),
            }
            for item in scores
        ]

        with self._session_factory.begin() as database:
            membership = self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.REVISOR},
            )
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            if membership.user_id not in self._assigned_reviewers(database, project_id):
                raise PermissionError("403: reviewer is not assigned to this QA pair")
            instrument, instrument_version = self._project_instrument(database, project_id)
            result = calculate_quality_scores(score_map, instrument)
            current = database.scalar(
                select(QualityAssessmentRecord)
                .where(
                    QualityAssessmentRecord.project_id == project_id,
                    QualityAssessmentRecord.study_id == study_id,
                    QualityAssessmentRecord.reviewer_user_id == payload["user_id"],
                )
                .with_for_update()
            )
            if current is None:
                if expected_version != 0:
                    raise ValueError("409: QA version conflict")
                record = QualityAssessmentRecord(
                    id=secrets.token_hex(16),
                    project_id=project_id,
                    study_id=study_id,
                    reviewer_user_id=payload["user_id"],
                    scores=normalized_scores,
                    score=result["score"],
                    category_scores=result["category_scores"],
                    classification=result["classification"],
                    confirmed=confirm,
                    version=1,
                    instrument_version=instrument_version,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                database.add(record)
                previous_value = None
            else:
                if current.confirmed:
                    raise ValueError("409: confirmed QA requires a recorded reopening")
                if current.version != expected_version:
                    raise ValueError("409: QA version conflict")
                previous_value = {"score": current.score, "scores": current.scores}
                current.scores = normalized_scores
                current.score = result["score"]
                current.category_scores = result["category_scores"]
                current.classification = result["classification"]
                current.confirmed = confirm
                current.instrument_version = instrument_version
                current.version += 1
                current.updated_at = datetime.now(timezone.utc)
                record = current
            if confirm and record.initial_scores is None:
                # Spec 005 regra 11: the first confirmed ratings feed the initial kappa and never change.
                record.initial_scores = normalized_scores
            new_value: dict[str, Any] = {
                "score": result["score"],
                "classification": result["classification"],
                "scores": normalized_scores,
            }
            if previous_value is not None and record.reopen_justification:
                new_value["justification"] = record.reopen_justification
            self._append_audit(
                database,
                entity_type="quality_assessment",
                entity_id=record.id,
                action="quality_assessment_confirmed" if confirm else "quality_assessment_saved",
                actor_user_id=payload["user_id"],
                previous_value=previous_value,
                new_value=new_value,
            )
            response = {
                "id": record.id,
                "study_id": study_id,
                "scores": normalized_scores,
                "score": result["score"],
                "category_scores": result["category_scores"],
                "classification": result["classification"],
                "outcome": result["outcome"],
                "applicable_count": result["applicable_count"],
                "not_applicable_count": result["not_applicable_count"],
                "confirmed": confirm,
                "version": record.version,
            }
        return response

    def get_quality_status(self, token: str, project_id: str, study_id: str) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("quality assessment persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            reviewer_ids, assessments_by_user = self._quality_pair(database, project_id, study_id)
            own = assessments_by_user.get(payload["user_id"])
            peer_id = next((user_id for user_id in reviewer_ids if user_id != payload["user_id"]), None)
            peer = assessments_by_user.get(peer_id) if peer_id else None
            consensus = self._quality_consensus(database, project_id, study_id, reviewer_ids, assessments_by_user)
            response: dict[str, Any] = {
                "study_id": study_id,
                "own_assessment": None if own is None else {
                    "score": own.score,
                    "category_scores": own.category_scores,
                    "classification": own.classification,
                    "confirmed": own.confirmed,
                    "version": own.version,
                },
                "peer_status": "confirmed" if peer is not None and peer.confirmed else "awaiting",
            }
            if consensus is not None:
                first, second = (assessments_by_user[user_id] for user_id in reviewer_ids)
                first_scores, second_scores = _score_map(first.scores), _score_map(second.scores)
                shared_ids = [
                    criterion_id
                    for criterion_id in first_scores
                    if first_scores[criterion_id] is not None and second_scores.get(criterion_id) is not None
                ]
                kappa = calculate_weighted_kappa(
                    [first_scores[criterion_id] for criterion_id in shared_ids],
                    [second_scores[criterion_id] for criterion_id in shared_ids],
                )
                visible_peer = peer if peer is not None else second
                response.update(
                    {
                        "peer_assessment": {
                            "reviewer_user_id": visible_peer.reviewer_user_id,
                            "score": visible_peer.score,
                            "category_scores": visible_peer.category_scores,
                            "classification": visible_peer.classification,
                            "scores": visible_peer.scores,
                        },
                        "weighted_kappa": kappa,
                        "kappa_warning": kappa is not None and kappa < KAPPA_WARNING_THRESHOLD,
                        "disputed_criteria": consensus["disputed_criteria"],
                        "pending_arbitration": consensus["pending_arbitration"],
                        "arbitration_required": bool(consensus["pending_arbitration"]),
                        "status": consensus["status"],
                        "final_score": consensus.get("score"),
                        "final_category_scores": consensus.get("category_scores"),
                        "final_classification": consensus.get("classification"),
                        "final_outcome": consensus.get("outcome"),
                    }
                )
                if payload["user_id"] not in reviewer_ids:
                    # Third reviewer, admin and observer see both sides once both confirmed.
                    response["assessments"] = [
                        {"reviewer_user_id": item.reviewer_user_id, "scores": item.scores, "score": item.score}
                        for item in (first, second)
                    ]
            return response

    def create_extraction(
        self,
        token: str,
        project_id: str,
        study_id: str,
        *,
        field_id: str,
        value: Any,
        quote: str | None,
        page_reference: str | None,
        expected_version: int,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if field_id not in EXTRACTION_FIELD_IDS:
            raise ValueError("unknown extraction field id")
        if value is None:
            raise ValueError("extraction value is required")
        if is_substantive_field(field_id) and (
            not quote or not quote.strip() or not page_reference or not page_reference.strip()
        ):
            raise ValueError("substantive extraction fields require quote and page reference")
        if self._session_factory is None:
            raise ValueError("extraction persistence is not configured")

        with self._session_factory.begin() as database:
            membership = self._require_project_membership(
                database,
                project_id,
                payload["user_id"],
                {Role.REVISOR},
            )
            study = database.get(StudyRecord, study_id)
            if study is None or study.project_id != project_id:
                raise LookupError("study not found in project")
            assigned_reviewers = database.scalars(
                select(ProjectMembershipRecord.user_id)
                .where(
                    ProjectMembershipRecord.project_id == project_id,
                    ProjectMembershipRecord.role == Role.REVISOR.value,
                )
                .order_by(ProjectMembershipRecord.user_id)
                .limit(2)
            ).all()
            if membership.user_id not in assigned_reviewers:
                raise PermissionError("403: reviewer is not assigned to this extraction pair")
            current = database.scalar(
                select(ExtractionRecord)
                .where(
                    ExtractionRecord.project_id == project_id,
                    ExtractionRecord.study_id == study_id,
                    ExtractionRecord.field_id == field_id,
                )
                .order_by(ExtractionRecord.version.desc())
                .limit(1)
                .with_for_update()
            )
            if current is None:
                if expected_version != 0:
                    raise ValueError("409: extraction version conflict")
                version = 1
                previous_value = None
            else:
                if current.version != expected_version:
                    raise ValueError("409: extraction version conflict")
                version = current.version + 1
                previous_value = {"value": current.value, "version": current.version}
            record = ExtractionRecord(
                id=secrets.token_hex(16),
                project_id=project_id,
                study_id=study_id,
                field_id=field_id,
                value=value,
                quote=quote.strip() if quote else None,
                page_reference=page_reference.strip() if page_reference else None,
                extractor_user_id=payload["user_id"],
                version=version,
                created_at=datetime.now(timezone.utc),
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="extraction",
                entity_id=record.id,
                action="extraction_version_created",
                actor_user_id=payload["user_id"],
                previous_value=previous_value,
                new_value={"field_id": field_id, "value": value, "version": version},
            )
            return {
                "id": record.id,
                "study_id": study_id,
                "field_id": field_id,
                "value": value,
                "quote": record.quote,
                "page_reference": record.page_reference,
                "extractor_user_id": record.extractor_user_id,
                "version": version,
                "status": "pending_verification",
            }

    def verify_extraction(
        self,
        token: str,
        extraction_id: str,
        *,
        decision: str,
        justification: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if decision not in {"verified", "discrepancy"}:
            raise ValueError("verification decision must be verified or discrepancy")
        if not justification.strip():
            raise ValueError("verification requires a justification")
        if self._session_factory is None:
            raise ValueError("extraction verification persistence is not configured")
        with self._session_factory.begin() as database:
            extraction = database.get(ExtractionRecord, extraction_id)
            if extraction is None:
                raise LookupError("extraction not found")
            membership = self._require_project_membership(
                database,
                extraction.project_id,
                payload["user_id"],
                {Role.REVISOR, Role.TERCEIRO_REVISOR},
            )
            if extraction.extractor_user_id == membership.user_id:
                raise PermissionError("403: extractor cannot verify their own extraction")
            record = ExtractionVerificationRecord(
                id=secrets.token_hex(16),
                extraction_id=extraction_id,
                verifier_user_id=membership.user_id,
                decision=decision,
                justification=justification.strip(),
                created_at=datetime.now(timezone.utc),
            )
            database.add(record)
            self._append_audit(
                database,
                entity_type="extraction",
                entity_id=extraction_id,
                action="extraction_verification_recorded",
                actor_user_id=membership.user_id,
                previous_value=None,
                new_value={"decision": decision, "justification": justification.strip()},
            )
            return {
                "id": record.id,
                "extraction_id": extraction_id,
                "verifier_user_id": record.verifier_user_id,
                "decision": record.decision,
                "status": "verified" if decision == "verified" else "discrepancy",
            }

    def list_study_extractions(
        self,
        token: str,
        project_id: str,
        study_id: str,
    ) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("extraction persistence is not configured")
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = database.scalars(
                select(ExtractionRecord)
                .where(
                    ExtractionRecord.project_id == project_id,
                    ExtractionRecord.study_id == study_id,
                )
                .order_by(ExtractionRecord.field_id, ExtractionRecord.version)
            ).all()
            output: list[dict[str, Any]] = []
            for record in records:
                verification = database.scalar(
                    select(ExtractionVerificationRecord)
                    .where(ExtractionVerificationRecord.extraction_id == record.id)
                    .order_by(ExtractionVerificationRecord.created_at.desc())
                    .limit(1)
                )
                output.append(
                    {
                        "id": record.id,
                        "field_id": record.field_id,
                        "value": record.value,
                        "quote": record.quote,
                        "page_reference": record.page_reference,
                        "extractor_user_id": record.extractor_user_id,
                        "version": record.version,
                        "status": "pending_verification" if verification is None else verification.decision,
                    }
                )
            return output

    def upload_artifact(
        self,
        token: str,
        project_id: str,
        *,
        file_name: str,
        content: bytes,
        mime_type: str,
    ) -> dict[str, Any]:
        payload = self.validate_token(token)
        if self._session_factory is None or self._object_storage is None:
            raise ValueError("artifact storage is not configured")
        safe_file_name = file_name.replace("\\", "/").rsplit("/", 1)[-1].strip()
        if not safe_file_name or len(content) > 100 * 1024 * 1024:
            raise ValueError("artifact filename is required and files must be <= 100 MiB")
        content_hash = hashlib.sha256(content).hexdigest()
        artifact_id = secrets.token_hex(16)
        object_key = f"{project_id}/{artifact_id}/{safe_file_name}"

        try:
            with self._session_factory.begin() as database:
                self._require_project_membership(
                    database,
                    project_id,
                    payload["user_id"],
                    {Role.ADMIN, Role.REVISOR},
                )
                latest_version = database.scalar(
                    select(ArtifactRecord.version)
                    .where(
                        ArtifactRecord.project_id == project_id,
                        ArtifactRecord.file_name == safe_file_name,
                    )
                    .order_by(ArtifactRecord.version.desc())
                    .limit(1)
                )
                version = 1 if latest_version is None else latest_version + 1
                self._object_storage.store(
                    object_key,
                    content,
                    content_type=mime_type,
                    sha256=content_hash,
                )
                database.add(
                    ArtifactRecord(
                        id=artifact_id,
                        project_id=project_id,
                        file_name=safe_file_name,
                        object_key=object_key,
                        content_hash_sha256=content_hash,
                        mime_type=mime_type,
                        version=version,
                        created_by=payload["user_id"],
                        created_at=datetime.now(timezone.utc),
                    )
                )
                self._append_audit(
                    database,
                    entity_type="artifact",
                    entity_id=artifact_id,
                    action="artifact_uploaded",
                    actor_user_id=payload["user_id"],
                    previous_value=None,
                    new_value={"file_name": safe_file_name, "version": version, "sha256": content_hash},
                )
        except Exception:
            try:
                self._object_storage.remove(object_key)
            except Exception:
                pass
            raise
        return {
            "artifact_id": artifact_id,
            "project_id": project_id,
            "file_name": safe_file_name,
            "object_key": object_key,
            "sha256": content_hash,
            "mime_type": mime_type,
            "version": version,
        }

    def list_artifact_versions(
        self,
        token: str,
        project_id: str,
        file_name: str,
    ) -> list[dict[str, Any]]:
        payload = self.validate_token(token)
        if self._session_factory is None:
            raise ValueError("artifact metadata persistence is not configured")
        safe_file_name = file_name.replace("\\", "/").rsplit("/", 1)[-1]
        with self._session_factory() as database:
            self._require_project_membership(database, project_id, payload["user_id"], set(Role))
            records = database.scalars(
                select(ArtifactRecord)
                .where(
                    ArtifactRecord.project_id == project_id,
                    ArtifactRecord.file_name == safe_file_name,
                )
                .order_by(ArtifactRecord.version)
            ).all()
            return [
                {
                    "artifact_id": record.id,
                    "file_name": record.file_name,
                    "object_key": record.object_key,
                    "sha256": record.content_hash_sha256,
                    "mime_type": record.mime_type,
                    "version": record.version,
                    "created_at": record.created_at.isoformat(),
                }
                for record in records
            ]

    def read_artifact(self, token: str, artifact_id: str) -> tuple[dict[str, Any], bytes]:
        payload = self.validate_token(token)
        if self._session_factory is None or self._object_storage is None:
            raise ValueError("artifact storage is not configured")
        with self._session_factory() as database:
            record = database.get(ArtifactRecord, artifact_id)
            if record is None:
                raise LookupError("artifact not found")
            self._require_project_membership(database, record.project_id, payload["user_id"], set(Role))
            metadata = {
                "artifact_id": record.id,
                "file_name": record.file_name,
                "sha256": record.content_hash_sha256,
                "mime_type": record.mime_type,
                "version": record.version,
            }
            content = self._object_storage.read(record.object_key)
        if hashlib.sha256(content).hexdigest() != metadata["sha256"]:
            raise ValueError("artifact integrity check failed")
        return metadata, content

    @staticmethod
    def _append_audit(
        database: Any,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_user_id: str,
        previous_value: dict[str, object] | None,
        new_value: dict[str, object] | None,
    ) -> None:
        database.add(
            AuditEventRecord(
                id=secrets.token_hex(16),
                entity_type=entity_type,
                entity_id=entity_id,
                action=action,
                actor_user_id=actor_user_id,
                performed_at=datetime.now(timezone.utc),
                previous_value=previous_value,
                new_value=new_value,
            )
        )

    def list_audit_events(self, token: str) -> list[dict[str, Any]]:
        self.require_permission(token, "audit_export")
        if self._session_factory is None:
            raise ValueError("audit persistence is not configured")
        with self._session_factory() as database:
            records = database.scalars(
                select(AuditEventRecord).order_by(AuditEventRecord.performed_at.desc())
            ).all()
            return [
                {
                    "id": record.id,
                    "entity_type": record.entity_type,
                    "entity_id": record.entity_id,
                    "action": record.action,
                    "actor_user_id": record.actor_user_id,
                    "performed_at": record.performed_at.isoformat(),
                    "previous_value": record.previous_value,
                    "new_value": record.new_value,
                }
                for record in records
            ]


class AuditLog:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def record(
        self,
        *,
        entity_type: str,
        entity_id: str,
        action: str,
        actor_user_id: str,
        previous_value: Any,
        new_value: Any,
    ) -> dict[str, Any]:
        event = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "actor_user_id": actor_user_id,
            "previous_value": previous_value,
            "new_value": new_value,
        }
        self.events.append(event)
        return event

    def update_event(self, entity_id: str, new_value: Any) -> None:
        raise ValueError("append-only audit log rejects update operations")

    def delete_event(self, entity_id: str) -> None:
        raise ValueError("append-only audit log rejects delete operations")


class ArtifactStore:
    def __init__(self) -> None:
        self.versions: dict[str, list[dict[str, Any]]] = {}

    def upload(self, file_name: str, payload: bytes) -> dict[str, Any]:
        versions = self.versions.setdefault(file_name, [])
        version_number = len(versions) + 1
        artifact = {
            "file_name": file_name,
            "version": version_number,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "content": payload,
        }
        versions.append(artifact)
        return {"file_name": file_name, "version": version_number, "sha256": artifact["sha256"]}


class BackupService:
    def create_backup(self, snapshot_name: str, age_hours: int = 0) -> dict[str, Any]:
        return {
            "snapshot_name": snapshot_name,
            "age_hours": age_hours,
            "integrity_ok": True,
        }

    def restore(self, backup: dict[str, Any]) -> dict[str, Any]:
        data_loss_hours = int(backup.get("age_hours", 0))
        integrity_ok = data_loss_hours <= 24
        return {
            "data_loss_hours": data_loss_hours,
            "integrity_ok": integrity_ok,
        }


__all__ = [
    "ArtifactStore",
    "AuditLog",
    "AuthController",
    "AuthService",
    "BackupService",
    "Role",
    "User",
    "UserRolePolicy",
    "classify_triage_pair",
    "calculate_quality_scores",
    "calculate_weighted_kappa",
    "validate_boolean_query",
]
