from alembic import context

from app.db import Base

target_metadata = Base.metadata


def run_migrations_online() -> None:
    # The caller (app.migrate) passes its own connection via config.attributes.
    connection = context.config.attributes["connection"]
    context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
    with context.begin_transaction():
        context.run_migrations()


run_migrations_online()
