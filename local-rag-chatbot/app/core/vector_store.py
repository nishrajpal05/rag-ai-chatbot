import faiss
import numpy as np
import pickle
from typing import List, Dict, Tuple
from pathlib import Path
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    def __init__(self, dimension: int = settings.VECTOR_DIMENSION, index_path: str = "app/storage/indices"):
        self.dimension = dimension
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)

        self.index_file = self.index_path / "faiss_index.bin"
        self.metadata_file = self.index_path / "metadata.pkl"

        if self.index_file.exists() and self.metadata_file.exists():
            self._load_index()
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.documents = []
            self.metadata = []
            logger.info(f"Created new FAISS index with dimension {dimension}")

    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict]):
        if not documents:
            return

        if len(documents) != len(embeddings) or len(embeddings) != len(metadata):
            raise ValueError(
                f"Mismatch: {len(documents)} docs, {len(embeddings)} embeddings, {len(metadata)} metadata"
            )

        embeddings_array = np.array(embeddings, dtype=np.float32)
        if embeddings_array.shape[1] != self.dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self.dimension}, got {embeddings_array.shape[1]}"
            )

        self.index.add(embeddings_array)
        self.documents.extend(documents)
        self.metadata.extend(metadata)

        logger.info(f"Added {len(documents)} documents. Total: {self.index.ntotal}")
        self._save_index()

    def search(self, query_embedding: List[float], k: int = 4) -> List[Tuple[str, float, Dict]]:
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        query_vector = np.array([query_embedding], dtype=np.float32)
        if query_vector.shape[1] != self.dimension:
            logger.error(
                "Query embedding dimension mismatch: expected %s got %s",
                self.dimension,
                query_vector.shape[1],
            )
            return []

        distances, indices = self.index.search(query_vector, min(k, self.index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1 and idx < len(self.documents):
                similarity = 1.0 / (1.0 + float(dist))
                results.append((self.documents[idx], similarity, self.metadata[idx]))

        return results

    def clear(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.metadata = []
        self._save_index()
        logger.info("Cleared vector store")

    def get_document_count(self) -> int:
        return self.index.ntotal

    def get_stats(self) -> Dict:
        return {
            "total_documents": len(self.documents),
            "total_vectors": self.index.ntotal if self.index else 0,
            "dimension": self.dimension,
            "index_type": type(self.index).__name__ if self.index else "None",
        }

    def _save_index(self):
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, "wb") as f:
                pickle.dump(
                    {
                        "documents": self.documents,
                        "metadata": self.metadata,
                        "dimension": self.dimension,
                    },
                    f,
                )
            logger.info(f"Saved index: {self.index.ntotal} documents")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")

    def _load_index(self):
        try:
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.metadata = data["metadata"]
                self.dimension = data["dimension"]
            logger.info(f"Loaded index: {self.index.ntotal} documents")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            self.metadata = []


vector_store = FAISSVectorStore()
