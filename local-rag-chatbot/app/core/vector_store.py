import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    def __init__(self, dimension: int = 768, index_path: str = "app/storage/indices"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.index_path / "faiss_index.bin"
        self.metadata_file = self.index_path / "metadata.pkl"
        
        # Initialize or load existing index
        if self.index_file.exists():
            self._load_index()
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.documents = []
            self.metadata = []
            logger.info(f"Created new FAISS index with dimension {dimension}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        """Add documents with embeddings to vector store"""
        if not documents:
            return
        
        # Validate inputs
        if len(documents) != len(embeddings) != len(metadata):
            raise ValueError(f"Mismatch: {len(documents)} docs, {len(embeddings)} embeddings, {len(metadata)} metadata")
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        logger.info(f" Added {len(documents)} documents. Total: {self.index.ntotal}")
        
        # Save immediately
        self._save_index()
    
    def search(self, query_embedding: List[float], k: int = 4) -> List[Tuple[str, float, Dict]]:
        """Search with CORRECTED similarity scoring"""
        if self.index.ntotal == 0:
            logger.warning(" Vector store is EMPTY!")
            return []
        
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # Search FAISS (returns L2 distances)
        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))
        
        logger.info(f" FAISS Search Results:")
        results = []
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1 and idx < len(self.documents):
                #  Convert L2 distance to similarity score
                # L2 distance: 0 = identical, higher = more different
                # Normalize to 0-1 similarity score
                similarity = 1.0 / (1.0 + float(dist))
                
                doc = self.documents[idx]
                meta = self.metadata[idx]
                
                results.append((doc, similarity, meta))
                
                # Debug logging
                logger.info(f"  [{i+1}] L2={dist:.4f} → Similarity={similarity:.4f} | {meta.get('source', 'N/A')[:50]}")
                logger.info(f"      Text preview: {doc[:100]}...")
        
        if not results:
            logger.warning(" No results found in search!")
        
        return results
    
    def clear(self):
        """Clear all data"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        self._save_index()
        logger.info(" Cleared vector store")
    
    def get_document_count(self) -> int:
        """Get total document count"""
        return self.index.ntotal
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_documents': len(self.documents),
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else 'None'
        }
    
    def _save_index(self):
        """Persist index and metadata to disk"""
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata,
                    'dimension': self.dimension
                }, f)
            logger.info(f" Saved index: {self.index.ntotal} documents")
        except Exception as e:
            logger.error(f" Failed to save index: {e}")
    
    def _load_index(self):
        """Load index and metadata from disk"""
        try:
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
                self.dimension = data['dimension']
            logger.info(f" Loaded index: {self.index.ntotal} documents")
        except Exception as e:
            logger.error(f" Failed to load index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadata = []

# Global singleton
vector_store = FAISSVectorStore()