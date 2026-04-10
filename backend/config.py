from dotenv import load_dotenv
import os


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.openai_embedding_model = os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        )
        self.ocr_provider = os.getenv("OCR_PROVIDER", "google_vision")
        self.google_application_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        self.database_url = os.getenv("DATABASE_URL") or "sqlite:///./ai_cookbook.db"
        self.secret_key = os.getenv("SECRET_KEY")
        if not self.secret_key:
            raise ValueError("SECRET_KEY must be configured.")
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.recipe_corpus_path = os.getenv(
            "RECIPE_CORPUS_PATH",
            "backend/data/recipes_subset.json",
        )
        self.chroma_persist_directory = os.getenv(
            "CHROMA_PERSIST_DIRECTORY",
            "backend/data/chroma",
        )
        self.chroma_collection_name = os.getenv(
            "CHROMA_COLLECTION_NAME",
            "recipe_knowledge_base",
        )
        self.rag_candidate_count = int(os.getenv("RAG_CANDIDATE_COUNT", "10"))
        self.rag_context_count = int(os.getenv("RAG_CONTEXT_COUNT", "3"))
        self.embedding_batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "100"))
        self.max_ocr_upload_bytes = int(os.getenv("MAX_OCR_UPLOAD_BYTES", "5242880"))
        self.max_ocr_image_pixels = int(os.getenv("MAX_OCR_IMAGE_PIXELS", "20000000"))
        self.default_rate_limit_requests = int(os.getenv("DEFAULT_RATE_LIMIT_REQUESTS", "60"))
        self.default_rate_limit_window_seconds = int(
            os.getenv("DEFAULT_RATE_LIMIT_WINDOW_SECONDS", "900")
        )
        self.auth_rate_limit_requests = int(os.getenv("AUTH_RATE_LIMIT_REQUESTS", "5"))
        self.auth_rate_limit_window_seconds = int(
            os.getenv("AUTH_RATE_LIMIT_WINDOW_SECONDS", "900")
        )
        self.generate_rate_limit_requests = int(
            os.getenv("GENERATE_RATE_LIMIT_REQUESTS", "15")
        )
        self.generate_rate_limit_window_seconds = int(
            os.getenv("GENERATE_RATE_LIMIT_WINDOW_SECONDS", "900")
        )
        self.ocr_extract_rate_limit_requests = int(
            os.getenv("OCR_EXTRACT_RATE_LIMIT_REQUESTS", "10")
        )
        self.ocr_extract_rate_limit_window_seconds = int(
            os.getenv("OCR_EXTRACT_RATE_LIMIT_WINDOW_SECONDS", "900")
        )


settings = Settings()
