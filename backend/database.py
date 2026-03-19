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
