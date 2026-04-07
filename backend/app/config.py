from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://mediafetch:mediafetch123@postgres:5432/mediafetch_db"

    # LLM
    LLM_API_URL: str = "http://localhost:42005/v1/chat/completions"
    LLM_MODEL: str = "coder-model"
    QWEN_API_KEY: str = ""

    # Frontend path (override in Docker)
    FRONTEND_PATH: str = str(Path(__file__).parent.parent.parent / "frontend")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()