import logging
import numpy as np
from typing import Dict
from app.core.vector_store import vector_store
from app.core.llm_handler import llm_handler
from app.core.embeddings import embedding_model
from app.utils.prompts import RAG_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k
    
    def retrieve_and_generate(
        self, 
        query: str, 
        similarity_threshold: float = 0.3  # ✅ Adjusted for new embeddings
    ) -> Dict:
        """Retrieve relevant chunks and generate answer"""
        
        logger.info("=" * 60)
        logger.info(f" NEW QUERY: {query}")
        logger.info(f" Threshold: {similarity_threshold}")
        
        # Step 1: Generate query embedding
        query_embedding = embedding_model.embed_query(query)
        logger.info(f" Query embedding: {len(query_embedding)} dimensions")
        
        # Step 2: Search vector store
        results = vector_store.search(query_embedding, k=self.top_k)
        logger.info(f" Retrieved {len(results)} results from vector store")
        
        # LOG ALL SCORES
        if results:
            for i, (doc, score, meta) in enumerate(results):
                logger.info(f"  Result {i+1}: score={score:.4f}, source={meta.get('source', 'N/A')}")
                logger.info(f"    Preview: {doc[:80]}...")
        else:
            logger.warning(" NO RESULTS FROM VECTOR STORE!")
        
        # Step 3: Filter by similarity threshold
        filtered_results = [
            (doc, score, meta) for doc, score, meta in results 
            if score >= similarity_threshold
        ]
        
        logger.info(f"✅ Filtered: {len(filtered_results)}/{len(results)} passed threshold")
        
        if not filtered_results:
            logger.warning(" FILTERING REMOVED ALL RESULTS!")
            if results:
                best_score = results[0][1]
                logger.warning(f"   Best score was {best_score:.4f}, needed {similarity_threshold}")
            
            return {
                "answer": "I cannot find this information in the provided documents.",
                "sources": [],
                "confidence": "low"
            }
        
        # Step 4: Build context
        context_parts = []
        sources = []
        scores = []
        
        for doc, score, metadata in filtered_results:
            source = metadata.get('source', 'Unknown')
            chunk_id = metadata.get('chunk_id', 0)
            context_parts.append(f"[Source: {source}, Chunk {chunk_id}]\n{doc}")
            sources.append(f"{source} (chunk {chunk_id})")
            scores.append(score)
        
        context = "\n\n---\n\n".join(context_parts)
        logger.info(f"📝 Context built: {len(context)} characters")
        
        # Step 5: Generate answer
        from app.utils.prompts import RAG_SYSTEM_PROMPT
        prompt = RAG_SYSTEM_PROMPT.format(context=context, question=query)
        logger.info(f" Sending to Groq LLM (prompt length: {len(prompt)} chars)...")
        
        answer = llm_handler.generate(prompt)
        logger.info(f"✅ LLM response: {answer[:100]}...")
        
        # Calculate confidence (adjusted thresholds for cosine similarity)
        avg_score = sum(scores) / len(scores)
        confidence = "high" if avg_score > 0.5 else "medium" if avg_score > 0.3 else "low"
        
        logger.info(f"🎯 Final confidence: {confidence} (avg_score={avg_score:.4f})")
        logger.info("=" * 60)
        
        return {
            "answer": answer,
            "sources": list(set(sources)),
            "confidence": confidence
        }

retriever = RAGRetriever()