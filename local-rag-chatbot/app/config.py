import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    APP_NAME = "Local RAG Assistant"
    APP_VERSION = "2.0.0"
    APP_DESCRIPTION = "AI-powered document Q&A system with Groq API"
    
    # Groq API settings
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"  # Fast and high quality
    
    # Embedding settings (using sentence-transformers locally)
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, 384 dimensions
    
    # Vector store settings
    VECTOR_DIMENSION = 384  # Changed from 768 to match all-MiniLM-L6-v2
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 3
    SIMILARITY_THRESHOLD = 0.3
    
    # Storage paths
    STORAGE_DIR = Path("app/storage")
    UPLOAD_DIR = STORAGE_DIR / "uploads"
    INDEX_DIR = STORAGE_DIR / "indices"
    
    # Create directories
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()