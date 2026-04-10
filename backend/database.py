from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_recipe_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("recipes"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("recipes")}
    statements: list[str] = []

    if "preferences" not in existing_columns:
        statements.append("ALTER TABLE recipes ADD COLUMN preferences TEXT NOT NULL DEFAULT '[]'")
    if "allergies" not in existing_columns:
        statements.append("ALTER TABLE recipes ADD COLUMN allergies TEXT NOT NULL DEFAULT '[]'")
    if "image_cache_key" not in existing_columns:
        statements.append("ALTER TABLE recipes ADD COLUMN image_cache_key VARCHAR")
    if "image_path" not in existing_columns:
        statements.append("ALTER TABLE recipes ADD COLUMN image_path VARCHAR")
    if "image_prompt" not in existing_columns:
        statements.append("ALTER TABLE recipes ADD COLUMN image_prompt TEXT")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
        if "image_cache_key" not in existing_columns:
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_recipes_image_cache_key ON recipes (image_cache_key)")
            )


def ensure_user_profile_columns() -> None:
    inspector = inspect(engine)
    if not inspector.has_table("users"):
        return

    existing_columns = {column["name"] for column in inspector.get_columns("users")}
    statements: list[str] = []

    if "preferences" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN preferences TEXT NOT NULL DEFAULT '[]'")
    if "allergies" not in existing_columns:
        statements.append("ALTER TABLE users ADD COLUMN allergies TEXT NOT NULL DEFAULT '[]'")

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
