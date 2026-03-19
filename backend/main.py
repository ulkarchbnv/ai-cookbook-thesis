from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import Base, engine, ensure_recipe_columns, ensure_user_profile_columns
from backend.routes import auth, ocr, recipes


app = FastAPI(title="AI Cookbook API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_recipe_columns()
    ensure_user_profile_columns()


@app.get("/")
def read_root():
    return {
        "message": "AI Cookbook backend is running",
        "database_configured": bool(settings.database_url),
        "openai_key_loaded": bool(settings.openai_api_key),
    }


app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(ocr.router)
