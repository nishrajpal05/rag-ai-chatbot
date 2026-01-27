
import logging
from app.core.retriever import retriever

logger = logging.getLogger(__name__)

class QAService:
    def answer_question(self, question: str, similarity_threshold: float = 0.5):
        """Answer question using RAG with configurable threshold"""
        try:
            logger.info(f" Processing question: {question}")
            logger.info(f" Using similarity threshold: {similarity_threshold}")
            
            #  Pass threshold to retriever
            result = retriever.retrieve_and_generate(
                query=question,
                similarity_threshold=similarity_threshold
            )
            
            answer = result.get('answer', 'I cannot find this information in the provided documents.')
            sources = result.get('sources', [])
            confidence = result.get('confidence', 'low')
            
            logger.info(f" Generated answer with {confidence} confidence")
            
            return answer, sources, confidence
            
        except Exception as e:
            logger.error(f" Error in QA service: {str(e)}")
            return "An error occurred while processing your question.", [], "low"

qa_service = QAService()