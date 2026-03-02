import os
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def build_database_url() -> str:
    db = _require_env("POSTGRES_DB")
    user = _require_env("POSTGRES_USER")
    password = _require_env("POSTGRES_PASSWORD")
    host = _require_env("POSTGRES_HOST")
    port = _require_env("POSTGRES_PORT")

    # SQLAlchemy URL using psycopg v3
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def create_db_engine() -> Engine:
    # pool_pre_ping = checks stale connections (good reliability habit)
    return create_engine(build_database_url(), pool_pre_ping=True)