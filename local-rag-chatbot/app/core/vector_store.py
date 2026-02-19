import faiss
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class FAISSVectorStore:
    def __init__(self, dimension: int = 384, index_path: str = "app/storage/indices"):
        """
        Initialize FAISS vector store with cosine similarity support
        
        Args:
            dimension: Embedding dimension (384 for all-MiniLM-L6-v2)
            index_path: Path to store index files
        """
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.index_path / "faiss_index.bin"
        self.metadata_file = self.index_path / "metadata.pkl"
        
        # Initialize or load existing index
        if self.index_file.exists():
            self._load_index()
        else:
            # Use IndexFlatL2 for L2 distance (will normalize for cosine similarity)
            self.index = faiss.IndexFlatL2(dimension)
            self.documents = []
            self.metadata = []
            logger.info(f"✅ Created new FAISS index with dimension {dimension}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        """
        Add documents with embeddings to vector store
        Embeddings are normalized for cosine similarity
        """
        if not documents:
            logger.warning("No documents to add")
            return
        
        # Validate inputs
        if len(documents) != len(embeddings) != len(metadata):
            raise ValueError(
                f"Length mismatch: {len(documents)} docs, "
                f"{len(embeddings)} embeddings, {len(metadata)} metadata"
            )
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # ✅ CRITICAL: Normalize embeddings for cosine similarity
        # After normalization, L2 distance is related to cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Add to FAISS index
        self.index.add(embeddings_array)
        
        # Store documents and metadata
        self.documents.extend(documents)
        self.metadata.extend(metadata)
        
        logger.info(f"✅ Added {len(documents)} documents. Total: {self.index.ntotal}")
        
        # Save immediately after adding
        self._save_index()
    
    def search(self, query_embedding: List[float], k: int = 4) -> List[Tuple[str, float, Dict]]:
        """
        Search for similar documents using cosine similarity
        
        Args:
            query_embedding: Query vector
            k: Number of results to return
            
        Returns:
            List of (document, similarity_score, metadata) tuples
            Similarity scores are in range [0, 1] where 1 is most similar
        """
        if self.index.ntotal == 0:
            logger.warning("⚠️ Vector store is EMPTY!")
            return []
        
        # Convert query to numpy array
        query_vector = np.array([query_embedding], dtype=np.float32)
        
        # ✅ CRITICAL: Normalize query vector for cosine similarity
        faiss.normalize_L2(query_vector)
        
        # Search FAISS (returns L2 distances for normalized vectors)
        k_actual = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k_actual)
        
        logger.info(f"🔍 FAISS Search Results (top {k_actual}):")
        results = []
        
        for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
            if idx != -1 and idx < len(self.documents):
                # ✅ Convert L2 distance to cosine similarity
                # For normalized vectors: cosine_sim = 1 - (L2_dist^2 / 2)
                # This gives us a similarity score in range [0, 1]
                similarity = float(1.0 - (dist ** 2 / 2.0))
                
                # Clamp to [0, 1] range (handle floating point errors)
                similarity = max(0.0, min(1.0, similarity))
                
                doc = self.documents[idx]
                meta = self.metadata[idx]
                
                results.append((doc, similarity, meta))
                
                # Debug logging
                source_name = meta.get('source', 'Unknown')[:50]
                logger.info(f"  [{i+1}] L2_dist={dist:.4f} → Cosine_Sim={similarity:.4f}")
                logger.info(f"      Source: {source_name}")
                logger.info(f"      Preview: {doc[:100]}...")
        
        # Sort by similarity (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        if not results:
            logger.warning("❌ No results found in search!")
        else:
            logger.info(f"✅ Best similarity score: {results[0][1]:.4f}")
        
        return results
    
    def clear(self):
        """Clear all data from vector store"""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        self._save_index()
        logger.info("✅ Cleared vector store")
    
    def get_document_count(self) -> int:
        """Get total number of documents in store"""
        return self.index.ntotal
    
    def get_stats(self) -> Dict:
        """Get vector store statistics"""
        return {
            'total_documents': len(self.documents),
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': type(self.index).__name__ if self.index else 'None',
            'storage_path': str(self.index_path)
        }
    
    def _save_index(self):
        """Persist index and metadata to disk"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, str(self.index_file))
            
            # Save metadata and documents
            with open(self.metadata_file, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata,
                    'dimension': self.dimension
                }, f)
            
            logger.info(f"💾 Saved index: {self.index.ntotal} vectors to {self.index_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to save index: {e}", exc_info=True)
    
    def _load_index(self):
        """Load index and metadata from disk"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(str(self.index_file))
            
            # Load metadata and documents
            with open(self.metadata_file, 'rb') as f:
                data = pickle.load(f)
                self.documents = data['documents']
                self.metadata = data['metadata']
                self.dimension = data['dimension']
            
            logger.info(f"✅ Loaded index: {self.index.ntotal} vectors from {self.index_path}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load index: {e}")
            logger.info("Creating new index instead")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadata = []

# ✅ Global singleton instance
vector_store = FAISSVectorStore()