"""Connection pool for PostgreSQL using psycopg_pool."""
from __future__ import annotations

import os
from contextlib import contextmanager

import psycopg
from psycopg_pool import ConnectionPool

_conninfo = (
    f"dbname={os.getenv('POSTGRES_DB', 'autofabric')} "
    f"user={os.getenv('POSTGRES_USER', 'kim')} "
    f"host={os.getenv('POSTGRES_HOST', '127.0.0.1')} "
    f"port={os.getenv('POSTGRES_PORT', '5432')}"
)

_password = os.getenv("POSTGRES_PASSWORD", "")
if _password:
    _conninfo += f" password={_password}"

pool = ConnectionPool(conninfo=_conninfo, min_size=2, max_size=10, open=False)


def open_pool():
    """Call at app startup."""
    pool.open()


def close_pool():
    """Call at app shutdown."""
    pool.close()


@contextmanager
def get_conn():
    """Yield a connection from the pool. Auto-returns on exit."""
    with pool.connection() as conn:
        yield conn
