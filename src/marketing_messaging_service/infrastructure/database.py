import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


Base = declarative_base()


def _get_database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if url:
        return url
    return "sqlite:///./messaging.db"


DATABASE_URL = _get_database_url()

engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    future=True,
)


@contextmanager
def create_session() -> Iterator[Session]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
