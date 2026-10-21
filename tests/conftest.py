from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from rsl.app import create_app
from rsl.settings import Settings

API = "/api/v1"


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    settings = Settings(
        database_url=f"sqlite+pysqlite:///{(tmp_path / 'test.sqlite3').as_posix()}",
        jwt_secret="test-signing-key-for-rsl-api-with-32-bytes",
        storage_path=tmp_path / "storage",
        web_dist=tmp_path / "no-web-build",
    )
    with TestClient(create_app(settings), base_url="http://testserver" + API) as test_client:
        yield test_client


@pytest.fixture
def signup(client: TestClient) -> Callable[..., dict[str, str]]:
    """Create an account and return its auth headers."""

    def _signup(username: str = "ana", email: str | None = None, password: str = "senha-segura") -> dict[str, str]:
        response = client.post("/auth/signup", json={
            "username": username, "email": email or f"{username}@example.com", "password": password,
            "first_name": username.title(),
        })
        assert response.status_code == 201, response.text
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _signup


@pytest.fixture
def review(client: TestClient, signup) -> tuple[int, dict[str, str]]:
    headers = signup("dona")
    response = client.post("/reviews", headers=headers, json={"title": "Revisão de teste", "description": "Teste"})
    assert response.status_code == 201, response.text
    return response.json()["id"], headers
