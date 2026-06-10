import os
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from project root (.env and .ENV)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")
load_dotenv(PROJECT_ROOT / ".ENV")


class Settings:
    APP_NAME = "Local RAG Assistant"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "AI-powered document Q&A system with Groq API"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Upload limits
    MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "25"))

    # Groq API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # Embedding settings (using sentence-transformers locally)
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    # Vector store settings
    VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "384"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
    TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "3"))
    SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))

    # Storage paths
    STORAGE_DIR = Path("app/storage")
    UPLOAD_DIR = STORAGE_DIR / "uploads"
    INDEX_DIR = STORAGE_DIR / "indices"

    # Create directories
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


settings = Settings()
