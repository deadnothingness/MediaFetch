from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://mediafetch:mediafetch123@localhost:5432/mediafetch_db")
    LLM_API_URL: str = os.getenv("LLM_API_URL", "http://localhost:11434/api/generate")  # для Ollama
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen2:0.5b")

settings = Settings()