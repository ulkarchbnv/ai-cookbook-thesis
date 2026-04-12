from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_image_model: str = "gpt-image-1"

    # OCR
    ocr_provider: str = "google_vision"
    google_application_credentials: str | None = None

    # Database
    database_url: str = "sqlite:///./ai_cookbook.db"

    # Auth
    secret_key: str
    algorithm: str = "HS256"

    # CORS
    frontend_origin: str = "http://localhost:5173"

    # RAG / ChromaDB
    recipe_corpus_path: str = "backend/data/recipes_subset.json"
    chroma_persist_directory: str = "backend/data/chroma"
    chroma_collection_name: str = "recipe_knowledge_base"
    rag_candidate_count: int = 10
    rag_context_count: int = 3
    embedding_batch_size: int = 100

    # Media
    recipe_thumbnail_directory: str = "backend/media/recipe_thumbnails"

    # Upload limits
    max_ocr_upload_bytes: int = 5_242_880
    max_ocr_image_pixels: int = 20_000_000

    # Rate limiting
    default_rate_limit_requests: int = 60
    default_rate_limit_window_seconds: int = 900
    auth_rate_limit_requests: int = 5
    auth_rate_limit_window_seconds: int = 900
    generate_rate_limit_requests: int = 15
    generate_rate_limit_window_seconds: int = 900
    ocr_extract_rate_limit_requests: int = 10
    ocr_extract_rate_limit_window_seconds: int = 900

    @field_validator("secret_key")
    @classmethod
    def secret_key_must_be_set(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("SECRET_KEY must be configured and cannot be empty.")
        return value


settings = Settings()