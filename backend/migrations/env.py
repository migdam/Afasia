"""Alembic's environment: the app's own database and models (backlog P3-1)."""
from alembic import context

from app.db import models  # noqa: F401 - registers every table on Base
from app.db.database import Base, engine


def run(connection):
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        # SQLite can't alter most of a table in place; batch mode copies it.
        render_as_batch=connection.dialect.name == "sqlite",
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise SystemExit("Offline (SQL script) migrations aren't set up; run them against a database.")

# The app passes its own connection (database.migrate); the alembic command
# line connects with DATABASE_URL.
connection = context.config.attributes.get("connection")
if connection is not None:
    run(connection)
else:
    with engine.begin() as connection:
        run(connection)
