import importlib
import shutil
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import close_all_sessions
from sqlalchemy.orm import sessionmaker


@pytest.fixture()
def client(monkeypatch):
    temp_dir = Path("backend/.pytest_tmp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    database_path = (temp_dir / f"test-{uuid.uuid4().hex}.db").resolve()

    monkeypatch.setenv("SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path.as_posix()}")
    monkeypatch.setenv("FRONTEND_ORIGIN", "http://testserver")

    for module_name in [
        "backend.main",
        "backend.routes.auth",
        "backend.routes.ocr",
        "backend.routes.rag_debug",
        "backend.routes.recipes",
        "backend.dependencies",
        "backend.security",
        "backend.models",
        "backend.database",
        "backend.config",
    ]:
        sys.modules.pop(module_name, None)

    database = importlib.import_module("backend.database")
    models = importlib.import_module("backend.models")
    main = importlib.import_module("backend.main")
    auth_routes = importlib.import_module("backend.routes.auth")
    recipe_routes = importlib.import_module("backend.routes.recipes")
    ocr_routes = importlib.import_module("backend.routes.ocr")
    rag_debug_routes = importlib.import_module("backend.routes.rag_debug")

    test_engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    models.Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    for module in [database, auth_routes, recipe_routes, ocr_routes, rag_debug_routes]:
        get_db = getattr(module, "get_db", None)
        if get_db is not None:
            main.app.dependency_overrides[get_db] = override_get_db

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()
    close_all_sessions()
    models.Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()
    database.engine.dispose()

    if database_path.exists():
        database_path.unlink()
    shutil.rmtree(temp_dir, ignore_errors=True)
