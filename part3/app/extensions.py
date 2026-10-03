import sqlite3
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Shared database object. It lives in its own module so that both the
# application factory and the persistence layer can import it without a
# circular import.
db = SQLAlchemy()


@event.listens_for(Engine, "connect")
def _enforce_sqlite_foreign_keys(dbapi_connection, connection_record):
    """SQLite ignores FOREIGN KEY constraints unless this pragma is switched on."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
