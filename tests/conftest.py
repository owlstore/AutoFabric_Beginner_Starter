"""Shared test fixtures."""
from __future__ import annotations

import contextlib
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


class FakeCursor:
    """Minimal cursor that returns empty results by default."""

    def __init__(self):
        self._rows: list = []
        self._description = None

    def execute(self, query: str, params=None):
        q = query.strip().upper()
        if q.startswith("INSERT") and "RETURNING" in q:
            # Simulate a RETURNING row with plausible defaults
            now = datetime.now()
            self._rows = [(
                1, "test-project", "test desc", "requirement",
                "active", "medium", now, now,
            )]
        elif q.startswith("SELECT"):
            self._rows = []
        else:
            self._rows = []

    def fetchone(self):
        return self._rows[0] if self._rows else None

    def fetchall(self):
        return self._rows

    def close(self):
        pass


class FakeConn:
    """Fake DB connection."""

    def __init__(self):
        self.cursor_instance = FakeCursor()

    def cursor(self):
        return self.cursor_instance

    def commit(self):
        pass


@contextlib.contextmanager
def fake_get_conn():
    yield FakeConn()


@pytest.fixture(autouse=True)
def _mock_db():
    """Patch DB pool so tests run without PostgreSQL."""
    with patch("app.db.pool.get_conn", side_effect=fake_get_conn):
        yield


@pytest.fixture()
def client(_mock_db):
    from app.main import app
    return TestClient(app)
