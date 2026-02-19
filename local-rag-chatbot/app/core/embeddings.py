import logging
from sentence_transformers import SentenceTransformer
from typing import List
from app.config import settings

logger = logging.getLogger(__name__)

class LocalEmbeddings:
    def __init__(self):
        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        logger.info(f"✅ Embedding model loaded (dimension: {settings.VECTOR_DIMENSION})")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        try:
            logger.info(f"Generating embeddings for {len(texts)} documents...")
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            logger.info(f"✅ Generated {len(embeddings)} embeddings")
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embeddings: {str(e)}")
            raise
    
    def check_health(self) -> bool:
        """Check if embedding model is loaded"""
        try:
            test_embedding = self.embed_query("test")
            return len(test_embedding) == settings.VECTOR_DIMENSION
        except:
            return False

# Global singleton
embedding_model = LocalEmbeddings()