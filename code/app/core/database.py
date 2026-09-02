from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by every model in app.models."""


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Build the engine on first use, not at import time.

    The API's request path talks to Supabase over REST, so DATABASE_URL is
    optional. Importing this module must not fail when it is unset.
    """
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL is not set")
    return create_engine(settings.database_url, pool_pre_ping=True)


def get_db():
    session = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())()
    try:
        yield session
    finally:
        session.close()
