from sqlalchemy import text
from sqlalchemy.orm import Session


def print_db_connection_info(db: Session) -> None:
    # Works when the Session is bound to an Engine/Connection
    bind = db.get_bind()
    engine = bind.engine if hasattr(bind, "engine") else bind

    print("SQLAlchemy URL:", engine.url)
    # For SQLite, this resolves the on-disk path (or shows in-memory)
    if engine.dialect.name == "sqlite":
        raw_path = engine.url.database  # e.g. /abs/path/to/messaging.db or :memory:
        print("SQLite database:", raw_path)

    # Optional: prove it by asking the DB
    if engine.dialect.name == "sqlite":
        print("SQLite PRAGMA database_list:", db.execute(text("PRAGMA database_list")).all())
    elif engine.dialect.name == "postgresql":
        print("Postgres current_database():", db.execute(text("select current_database()")).scalar_one())
    elif engine.dialect.name == "mysql":
        print("MySQL database():", db.execute(text("select database()")).scalar_one())
