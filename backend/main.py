from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.config import settings
from backend.database import engine
from backend.rate_limit import RateLimitMiddleware, RateLimitRule
from backend.routes import auth, ocr, rag_debug, recipes


app = FastAPI(title="AI Cookbook API")
Path("backend/media").mkdir(parents=True, exist_ok=True)

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




app.mount("/media", StaticFiles(directory="backend/media"), name="media")


@app.get("/")
def read_root():
    return {
        "message": "AI Cookbook backend is running",
    }


app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(ocr.router)
app.include_router(rag_debug.router)