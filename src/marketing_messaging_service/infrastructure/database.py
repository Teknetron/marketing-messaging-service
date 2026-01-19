import os
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker


Base = declarative_base()


def _get_database_url() -> str:
    # `settings.py` is at: `.../src/marketing_messaging_service/config/settings.py`
    # Repo root is 4 levels up: config -> marketing_messaging_service -> src -> repo
    repo_root = Path(__file__).resolve().parents[3]
    default_db_path = (repo_root / "messaging.db").resolve()

    env_url = os.environ.get("DATABASE_URL")
    if not env_url:
        return f"sqlite:///{default_db_path}"

    # If someone sets a relative sqlite URL, normalize it to the repo root.
    if env_url.startswith("sqlite:///./"):
        rel = env_url.removeprefix("sqlite:///./")
        return f"sqlite:///{(repo_root / rel).resolve()}"

    return env_url



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
