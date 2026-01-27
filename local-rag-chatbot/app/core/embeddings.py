import logging
import requests
import numpy as np
from typing import List

logger = logging.getLogger(__name__)

class OllamaEmbeddings:
    def __init__(self, model_name: str = "nomic-embed-text", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.embed_url = f"{base_url}/api/embeddings"
        logger.info(f"Initialized Ollama Embeddings with model: {model_name}")
    
    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": text
            }
            
            response = requests.post(
                self.embed_url,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f" Embedding API error: {response.status_code}")
                raise Exception(f"Embedding failed: {response.text}")
            
            result = response.json()
            embedding = result.get('embedding', [])
            
            if not embedding:
                raise Exception("Empty embedding returned")
            
            logger.debug(f" Generated embedding: {len(embedding)} dimensions")
            return embedding
            
        except requests.exceptions.Timeout:
            logger.error(" Embedding request timed out")
            raise Exception("Embedding timeout")
        except requests.exceptions.ConnectionError:
            logger.error(" Cannot connect to Ollama for embeddings")
            raise Exception("Cannot connect to Ollama. Ensure it's running.")
        except Exception as e:
            logger.error(f" Error generating embedding: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        embeddings = []
        for i, text in enumerate(texts):
            logger.info(f"Embedding document {i+1}/{len(texts)}")
            embedding = self.embed_query(text)
            embeddings.append(embedding)
        return embeddings
    
    def check_health(self) -> bool:
        """Check if embedding model is available"""
        try:
            test_embedding = self.embed_query("test")
            return len(test_embedding) > 0
        except:
            return False

#  CREATE SINGLETON INSTANCE
embedding_model = OllamaEmbeddings()