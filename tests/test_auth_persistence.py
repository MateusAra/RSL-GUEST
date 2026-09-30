import pytest

from rsl_foundation import AuthService, Role, User


def test_users_and_refresh_sessions_survive_service_restart(tmp_path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'auth.sqlite'}"
    jwt_secret = "a-test-signing-key-with-at-least-32-bytes"
    user = User(id="u-persisted", email="persisted@example.com", role=Role.REVISOR)

    first_service = AuthService(
        jwt_secret=jwt_secret,
        database_url=database_url,
        create_schema=True,
    )
    first_service.register_user(user, password="senha-segura-123")
    first_session = first_service.create_session(user.email, "senha-segura-123")

    restarted_service = AuthService(jwt_secret=jwt_secret, database_url=database_url)
    assert restarted_service.validate_token(first_session["access_token"])["user_id"] == user.id

    rotated_session = restarted_service.refresh_session(first_session["refresh_token"])
    assert rotated_session["refresh_token"] != first_session["refresh_token"]
    assert restarted_service.validate_token(rotated_session["access_token"])["email"] == user.email

    with pytest.raises(PermissionError, match="401"):
        restarted_service.refresh_session(first_session["refresh_token"])


def test_user_registration_rejects_duplicate_email_case_insensitively(tmp_path):
    database_url = f"sqlite+pysqlite:///{tmp_path / 'auth.sqlite'}"
    service = AuthService(database_url=database_url, create_schema=True)
    service.register_user(
        User(id="u-one", email="Researcher@example.com", role=Role.ADMIN),
        password="senha-segura-123",
    )

    with pytest.raises(ValueError, match="already exists"):
        service.register_user(
            User(id="u-two", email="researcher@example.com", role=Role.REVISOR),
            password="outra-senha-456",
        )