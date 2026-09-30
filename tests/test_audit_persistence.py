import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError

from backend.api import app
from rsl_foundation.database import AuditEventRecord, build_engine


def test_user_creation_writes_append_only_audit_event():
    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        )
        token = login.json()["access_token"]
        created = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": "audit-test@example.com", "password": "audit-test-123", "role": "revisor"},
        )
        assert created.status_code == 200

        events = client.get(
            "/api/v1/audit-events",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert events.status_code == 200
        matching = [event for event in events.json() if event["entity_id"] == created.json()["id"]]
        assert len(matching) == 1
        assert matching[0]["action"] == "user_created"
        assert matching[0]["actor_user_id"] == "u-admin"
        assert matching[0]["new_value"]["email"] == "audit-test@example.com"


@pytest.mark.parametrize("operation", ["update", "delete"])
def test_database_rejects_audit_event_mutation(operation):
    engine = build_engine(os.environ["RSL_DATABASE_URL"])
    with TestClient(app) as client:
        login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@rsl.local", "password": "admin123"},
        )
        token = login.json()["access_token"]
        created = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={"email": f"immutable-{operation}@example.com", "password": "audit-test-123", "role": "revisor"},
        )
        event_id = client.get(
            "/api/v1/audit-events",
            headers={"Authorization": f"Bearer {token}"},
        ).json()[0]["id"]
        statement = (
            update(AuditEventRecord).where(AuditEventRecord.id == event_id).values(action="tampered")
            if operation == "update"
            else delete(AuditEventRecord).where(AuditEventRecord.id == event_id)
        )

    try:
        with engine.begin() as connection:
            with pytest.raises(DBAPIError):
                connection.execute(statement)
    finally:
        engine.dispose()