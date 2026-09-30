import pytest
from fastapi.testclient import TestClient

from rsl_foundation import (
    ArtifactStore,
    AuditLog,
    AuthController,
    AuthService,
    BackupService,
    Role,
    User,
    UserRolePolicy,
)

from backend.api import app


def test_ca_01_observer_cannot_write():
    policy = UserRolePolicy()
    observer = User(id="u-obs", email="obs@example.com", role=Role.OBSERVADOR)

    with pytest.raises(PermissionError):
        policy.require_write(observer)


def test_ca_02_revisor_cannot_access_admin():
    policy = UserRolePolicy()
    revisor = User(id="u-r1", email="r1@example.com", role=Role.REVISOR)

    with pytest.raises(PermissionError):
        policy.require_admin(revisor)


def test_ca_03_audit_entry_created_on_change():
    audit = AuditLog()
    event = audit.record(
        entity_type="project",
        entity_id="p-1",
        action="update",
        actor_user_id="u-admin",
        previous_value={"name": "Antigo"},
        new_value={"name": "Novo"},
    )

    assert event["actor_user_id"] == "u-admin"
    assert len(audit.events) == 1
    assert audit.events[0]["new_value"]["name"] == "Novo"


def test_ca_04_audit_is_append_only():
    audit = AuditLog()
    audit.record(
        entity_type="project",
        entity_id="p-1",
        action="update",
        actor_user_id="u-admin",
        previous_value={"name": "A"},
        new_value={"name": "B"},
    )

    with pytest.raises(ValueError):
        audit.update_event("not-found", "new")

    with pytest.raises(ValueError):
        audit.delete_event("not-found")


def test_ca_05_request_without_token_returns_401():
    controller = AuthController()

    with pytest.raises(PermissionError, match="401"):
        controller.require_token(None)


def test_ca_06_same_artifact_name_creates_new_version():
    store = ArtifactStore()
    first = store.upload("pdf.pdf", b"one")
    second = store.upload("pdf.pdf", b"two")

    assert first["version"] == 1
    assert second["version"] == 2
    assert len(store.versions["pdf.pdf"]) == 2


def test_ca_07_restore_keeps_data_loss_within_24_hours():
    service = BackupService()
    backup = service.create_backup("snapshot", age_hours=8)
    restored = service.restore(backup)

    assert restored["data_loss_hours"] <= 24
    assert restored["integrity_ok"] is True


def test_ca_08_permissions_matrix_blocks_forbidden_access():
    policy = UserRolePolicy()
    observer = User(id="u-obs", email="obs@example.com", role=Role.OBSERVADOR)
    revisor = User(id="u-r1", email="r1@example.com", role=Role.REVISOR)

    with pytest.raises(PermissionError):
        policy.check_endpoint(observer, "create_project")

    with pytest.raises(PermissionError):
        policy.check_endpoint(revisor, "manage_users")

    assert policy.check_endpoint(revisor, "review_study") is True


def test_auth_service_login_and_token_validation():
    service = AuthService()
    user = User(id="u-admin", email="admin@example.com", role=Role.ADMIN)
    service.register_user(user, password="senha123")

    token = service.login("admin@example.com", "senha123")
    payload = service.validate_token(token)

    assert payload["user_id"] == user.id
    assert payload["role"] == Role.ADMIN.value


def test_auth_service_forbids_write_for_observer_token():
    service = AuthService()
    observer = User(id="u-obs", email="obs@example.com", role=Role.OBSERVADOR)
    service.register_user(observer, password="secret123")

    token = service.login("obs@example.com", "secret123")

    with pytest.raises(PermissionError):
        service.require_permission(token, "create_project")


def test_real_login_and_role_check_with_hash_validation():
    service = AuthService()
    user = User(id="u-admin", email="admin@example.com", role=Role.ADMIN)
    service.register_user(user, password="senha123")

    token = service.login("admin@example.com", "senha123")

    assert service._users["admin@example.com"]["password_hash"].startswith("scrypt$")
    assert service.validate_token(token)["email"] == "admin@example.com"
    assert service.require_permission(token, "manage_users") is True

    token_parts = token.split(".")
    forged_token = f"{token_parts[0]}.{token_parts[1]}.{'0' * len(token_parts[2])}"
    with pytest.raises(PermissionError, match="401"):
        service.validate_token(forged_token)

    with pytest.raises(PermissionError):
        service.require_permission(token, "not_a_real_endpoint")


def test_api_login_and_admin_user_creation_flow():
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert len(token.split(".")) == 3
        refresh_token = response.json()["refresh_token"]

        me = client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "admin@rsl.local"
        assert client.get("/api/v1/protected").status_code == 401
        assert client.get(
            "/api/v1/protected",
            headers={"Authorization": "Bearer invalid-token"},
        ).status_code == 401
        assert client.get("/api/v1/protected", headers={"Authorization": f"Bearer {token}"}).status_code == 200

        refreshed = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["refresh_token"] != refresh_token

        reused_refresh = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert reused_refresh.status_code == 401
        token = refreshed.json()["access_token"]

        create = client.post(
            "/api/v1/users",
            json={"email": "novo@rsl.local", "password": "senha456", "role": "revisor"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create.status_code == 200
        assert create.json()["email"] == "novo@rsl.local"

        created_login = client.post(
            "/api/v1/auth/login",
            json={"email": "novo@rsl.local", "password": "senha456"},
        )
        assert created_login.status_code == 200
        assert created_login.json()["user"]["role"] == "revisor"

        observer_login = client.post(
            "/api/v1/auth/login",
            json={"email": "observer@rsl.local", "password": "observer123"},
        )
        observer_token = observer_login.json()["access_token"]
        forbidden = client.post(
            "/api/v1/users",
            json={"email": "bad@rsl.local", "password": "senha456", "role": "admin"},
            headers={"Authorization": f"Bearer {observer_token}"},
        )
        assert forbidden.status_code == 403
        observer_users = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {observer_token}"},
        )
        assert observer_users.status_code == 403
        assert client.get(
            "/api/v1/protected",
            headers={"Authorization": f"Bearer {observer_token}"},
        ).status_code == 403

        invalid = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "errada"},
        )
        assert invalid.status_code == 401

        logout = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert logout.status_code == 204
        assert client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {token}"},
        ).status_code == 401


def test_api_user_and_refresh_session_survive_application_restart():
    with TestClient(app) as first_client:
        admin_login = first_client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        )
        admin_token = admin_login.json()["access_token"]
        create = first_client.post(
            "/api/v1/users",
            json={"email": "persistente@rsl.local", "password": "senha789", "role": "revisor"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert create.status_code == 200
        user_session = first_client.post(
            "/api/v1/auth/login",
            json={"email": "persistente@rsl.local", "password": "senha789"},
        ).json()

    with TestClient(app) as restarted_client:
        me = restarted_client.get(
            "/api/v1/me",
            headers={"Authorization": f"Bearer {user_session['access_token']}"},
        )
        assert me.status_code == 200
        assert me.json()["email"] == "persistente@rsl.local"

        refreshed = restarted_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_session["refresh_token"]},
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["user"]["role"] == "revisor"


def test_artifact_upload_is_project_scoped_hashed_and_versioned():
    with TestClient(app) as client:
        admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        ).json()
        admin_headers = {"Authorization": f"Bearer {admin_login['access_token']}"}
        project = client.post(
            "/api/v1/projects",
            headers=admin_headers,
            json={
                "title": "Projeto de artefatos",
                "objective": "Testar versões de arquivo.",
                "study_type": "systematic_literature_review",
                "members": [
                    {"email": "reviewer@rsl.local", "role": "revisor"},
                    {"email": "reviewer2@rsl.local", "role": "revisor"},
                    {"email": "third-reviewer@rsl.local", "role": "terceiro_revisor"},
                ],
            },
        ).json()
        url = f"/api/v1/projects/{project['id']}/artifacts/upload"
        first = client.post(
            url,
            headers=admin_headers,
            files={"file": ("source.pdf", b"pdf version one", "application/pdf")},
        )
        second = client.post(
            url,
            headers=admin_headers,
            files={"file": ("source.pdf", b"pdf version two", "application/pdf")},
        )
        assert first.status_code == 201, first.text
        assert second.status_code == 201
        assert first.json()["version"] == 1
        assert second.json()["version"] == 2
        assert first.json()["sha256"] != second.json()["sha256"]

        versions = client.get(
            f"/api/v1/projects/{project['id']}/artifacts/source.pdf/versions",
            headers=admin_headers,
        )
        assert versions.status_code == 200
        assert [artifact["version"] for artifact in versions.json()] == [1, 2]
