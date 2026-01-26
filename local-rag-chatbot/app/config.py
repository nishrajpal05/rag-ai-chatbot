from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Local RAG Chatbot"
    DEBUG: bool = True
    
    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "gemma:7b"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    
    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    MAX_FILE_SIZE_MB: int = 50
    
    # Retrieval Settings
    TOP_K_RESULTS: int = 4
    SIMILARITY_THRESHOLD: float = 0.35
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "app" / "storage" / "uploads"
    INDEX_DIR: Path = BASE_DIR / "app" / "storage" / "indices"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Create directories if they don't exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.INDEX_DIR.mkdir(parents=True, exist_ok=True)