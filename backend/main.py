from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import Base, engine, ensure_recipe_columns, ensure_user_profile_columns
from backend.rate_limit import RateLimitMiddleware, RateLimitRule
from backend.routes import auth, ocr, recipes


app = FastAPI(title="AI Cookbook API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    RateLimitMiddleware,
    default_rule=RateLimitRule(
        max_requests=settings.default_rate_limit_requests,
        window_seconds=settings.default_rate_limit_window_seconds,
    ),
    route_rules={
        "/signup": RateLimitRule(
            max_requests=settings.auth_rate_limit_requests,
            window_seconds=settings.auth_rate_limit_window_seconds,
        ),
        "/login": RateLimitRule(
            max_requests=settings.auth_rate_limit_requests,
            window_seconds=settings.auth_rate_limit_window_seconds,
        ),
        "/token": RateLimitRule(
            max_requests=settings.auth_rate_limit_requests,
            window_seconds=settings.auth_rate_limit_window_seconds,
        ),
        "/me": RateLimitRule(
            max_requests=settings.auth_rate_limit_requests,
            window_seconds=settings.auth_rate_limit_window_seconds,
        ),
        "/generate-recipe": RateLimitRule(
            max_requests=settings.generate_rate_limit_requests,
            window_seconds=settings.generate_rate_limit_window_seconds,
        ),
        "/ocr/extract": RateLimitRule(
            max_requests=settings.ocr_extract_rate_limit_requests,
            window_seconds=settings.ocr_extract_rate_limit_window_seconds,
        ),
    },
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
    }


app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(ocr.router)
