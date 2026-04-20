import importlib
import shutil
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import close_all_sessions

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


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
        "backend.routes",
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

    models.Base.metadata.create_all(bind=database.engine)

    def override_get_db():
        db = database.SessionLocal()
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
    models.Base.metadata.drop_all(bind=database.engine)
    database.engine.dispose()

    if database_path.exists():
        database_path.unlink()
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture()
def user_credentials():
    return {
        "email": "tester@example.com",
        "password": "strong-password-123",
    }


@pytest.fixture()
def create_user(client):
    def _create_user(email: str, password: str):
        response = client.post(
            "/signup",
            json={"email": email, "password": password},
        )
        return response

    return _create_user


@pytest.fixture()
def login_user(client, create_user):
    def _login_user(email: str = "tester@example.com", password: str = "strong-password-123"):
        create_user(email, password)
        response = client.post(
            "/login",
            json={"email": email, "password": password},
        )
        return response

    return _login_user


@pytest.fixture()
def auth_headers(login_user):
    def _auth_headers(email: str = "tester@example.com", password: str = "strong-password-123"):
        login_response = login_user(email, password)
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _auth_headers
