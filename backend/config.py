from dotenv import load_dotenv
import os


load_dotenv()


class Settings:
    def __init__(self) -> None:
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.tesseract_cmd = os.getenv(
            "TESSERACT_CMD",
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        )
        self.database_url = os.getenv("DATABASE_URL") or "sqlite:///./ai_cookbook.db"
        self.secret_key = os.getenv("SECRET_KEY") or "development-secret-key"
        self.algorithm = os.getenv("ALGORITHM", "HS256")
        self.frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


settings = Settings()
