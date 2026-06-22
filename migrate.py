from pathlib import Path

from app.core.database import engine


BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "migrations"


def ensure_schema_migrations(cursor) -> None:
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            filename VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )


def get_applied_migrations(cursor) -> set[str]:
    cursor.execute("SELECT filename FROM schema_migrations")
    return {row[0] for row in cursor.fetchall()}


def run_migrations() -> None:
    if not MIGRATIONS_DIR.exists():
        raise RuntimeError(f"Migration directory not found: {MIGRATIONS_DIR}")

    migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"), key=lambda path: path.name)
    connection = engine.raw_connection()

    try:
        cursor = connection.cursor()
        try:
            ensure_schema_migrations(cursor)
            connection.commit()
            applied_migrations = get_applied_migrations(cursor)

            for migration_file in migration_files:
                filename = migration_file.name
                if filename in applied_migrations:
                    print(f"Skipped: {filename}")
                    continue

                print(f"Running migration: {filename}")
                sql = migration_file.read_text(encoding="utf-8").strip()

                try:
                    if sql:
                        cursor.execute(sql)
                    cursor.execute(
                        """
                        INSERT INTO schema_migrations (filename)
                        VALUES (%s)
                        ON CONFLICT (filename) DO NOTHING
                        """,
                        (filename,),
                    )
                    connection.commit()
                    applied_migrations.add(filename)
                except Exception:
                    connection.rollback()
                    print(f"Failed: {filename}")
                    raise
        finally:
            cursor.close()
    finally:
        connection.close()

    print("Migration completed")


if __name__ == "__main__":
    run_migrations()
