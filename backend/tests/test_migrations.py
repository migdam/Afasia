"""The database's schema comes from Alembic migrations, and a database made
before them is brought up to date with its data kept (backlog P3-1)."""
import sqlalchemy as sa
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.db.database import Base, engine, migrate
from app.db import models  # noqa: F401 - registers every table on Base


def differences(bind):
    with bind.connect() as connection:
        return compare_metadata(MigrationContext.configure(connection), Base.metadata)


def test_migrations_make_exactly_the_schema_the_models_describe(tmp_path):
    fresh = sa.create_engine(f"sqlite:///{tmp_path}/fresh.db")

    migrate(fresh)

    assert differences(fresh) == []
    assert "alembic_version" in sa.inspect(fresh).get_table_names()


def test_a_database_made_before_migrations_keeps_its_data_and_gets_new_tables(tmp_path):
    old = sa.create_engine(f"sqlite:///{tmp_path}/old.db")
    # As the app made it before (create_all), at a time without some newer tables.
    newer = {"time_zones", "consents"}
    Base.metadata.create_all(old, tables=[t for n, t in Base.metadata.tables.items() if n not in newer])
    with old.begin() as connection:
        connection.execute(sa.text(
            "INSERT INTO users (email, username, hashed_password, role, is_active) "
            "VALUES ('pat@example.com', 'pat', 'x', 'PATIENT', 1)"))

    migrate(old)

    assert newer <= set(sa.inspect(old).get_table_names())
    assert differences(old) == []
    with old.connect() as connection:
        assert connection.execute(sa.text("SELECT username FROM users")).scalars().all() == ["pat"]


def test_migrating_again_changes_nothing(tmp_path):
    database = sa.create_engine(f"sqlite:///{tmp_path}/again.db")
    migrate(database)

    migrate(database)

    assert differences(database) == []


def test_the_app_migrates_its_database_when_it_starts(client):
    assert "alembic_version" in sa.inspect(engine).get_table_names()
