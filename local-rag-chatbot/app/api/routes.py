# from fastapi import APIRouter, UploadFile, File, HTTPException
# from app.api.models import (
#     UploadResponse, ScrapeRequest, ScrapeResponse,
#     QuestionRequest, QuestionResponse, StatusResponse
# )
# from app.services.file_service import file_service
# from app.services.scraper_service import scraper_service
# from app.services.qa_service import qa_service
# from app.core.vector_store import vector_store

# router = APIRouter()

# @router.post("/upload", response_model=UploadResponse)
# async def upload_file(file: UploadFile = File(...)):
#     """Upload and process a document"""
#     success, message, chunks = await file_service.process_upload(file)
    
#     return UploadResponse(
#         success=success,
#         message=message,
#         filename=file.filename if success else None,
#         chunks_created=chunks if success else None
#     )

# @router.post("/scrape", response_model=ScrapeResponse)
# async def scrape_website(request: ScrapeRequest):
#     """Scrape a website and add to knowledge base"""
#     success, message, chunks = scraper_service.scrape_url(str(request.url))
    
#     return ScrapeResponse(
#         success=success,
#         message=message,
#         url=str(request.url) if success else None,
#         chunks_created=chunks if success else None
#     )

# @router.post("/ask", response_model=QuestionResponse)
# async def ask_question(request: QuestionRequest):
#     """Ask a question based on uploaded documents"""
#     answer, sources, confidence = qa_service.answer_question(request.question)
    
#     return QuestionResponse(
#         success=True,
#         answer=answer,
#         sources=sources if sources else None,
#         confidence=confidence
#     )

# @router.get("/status", response_model=StatusResponse)
# async def get_status():
#     """Get system status"""
#     stats = vector_store.get_stats()
    
#     return StatusResponse(
#         status="ready",
#         documents_loaded=stats['total_documents'],
#         vector_store_ready=stats['total_vectors'] > 0
#     )

# @router.post("/clear")
# async def clear_database():
#     """Clear all documents from vector store"""
#     try:
#         vector_store.clear()
#         return {"success": True, "message": "All documents cleared"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/debug")
# async def debug_info():
#     """Debug vector store contents"""
#     stats = vector_store.get_stats()
    
#     # Get sample documents
#     sample_docs = []
#     if vector_store.documents:
#         for i, doc in enumerate(vector_store.documents[:3]):  # First 3 docs
#             sample_docs.append({
#                 "chunk_id": i,
#                 "preview": doc[:200] + "..." if len(doc) > 200 else doc,
#                 "metadata": vector_store.metadata[i] if i < len(vector_store.metadata) else None
#             })
    
#     return {
#         "total_documents": len(vector_store.documents),
#         "total_vectors": vector_store.index.ntotal if vector_store.index else 0,
#         "dimension": vector_store.dimension,
#         "sample_documents": sample_docs
#     }




from fastapi import APIRouter, UploadFile, File, HTTPException
import logging

from app.api.models import (
    UploadResponse, ScrapeRequest, ScrapeResponse,
    QuestionRequest, QuestionResponse, StatusResponse
)
from app.services.file_service import file_service
from app.services.scraper_service import scraper_service
from app.services.qa_service import qa_service
from app.core.vector_store import vector_store

#  ADD LOGGER
logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        success, message, chunks = await file_service.process_upload(file)
        
        return UploadResponse(
            success=success,
            message=message,
            filename=file.filename if success else None,
            chunks_created=chunks if success else None
        )
    except Exception as e:
        logger.error(f"Error in upload endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_website(request: ScrapeRequest):
    """Scrape a website and add to knowledge base"""
    try:
        success, message, chunks = scraper_service.scrape_url(str(request.url))
        
        return ScrapeResponse(
            success=success,
            message=message,
            url=str(request.url) if success else None,
            chunks_created=chunks if success else None
        )
    except Exception as e:
        logger.error(f"Error in scrape endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question based on uploaded documents"""
    try:
        #  CRITICAL FIX: Pass lower similarity threshold as model is not giving answers 
        answer, sources, confidence = qa_service.answer_question(
            request.question,
            similarity_threshold=0.0001  # Lowered from default 0.5
        )
        
        return QuestionResponse(
            success=True,
            answer=answer,
            sources=sources if sources else None,
            confidence=confidence
        )
    except Exception as e:
        logger.error(f"Error in ask endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get system status"""
    try:
        stats = vector_store.get_stats()
        
        return StatusResponse(
            status="ready",
            documents_loaded=stats['total_documents'],
            vector_store_ready=stats['total_vectors'] > 0
        )
    except Exception as e:
        logger.error(f"Error in status endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_database():
    """Clear all documents from vector store"""
    try:
        vector_store.clear()
        logger.info("Vector store cleared successfully")
        return {"success": True, "message": "All documents cleared"}
    except Exception as e:
        logger.error(f"Error clearing vector store: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/debug")
async def debug_info():
    """Debug vector store contents"""
    try:
        stats = vector_store.get_stats()
        
        # Get sample documents
        sample_docs = []
        if vector_store.documents:
            for i, doc in enumerate(vector_store.documents[:3]):  # First 3 docs
                sample_docs.append({
                    "chunk_id": i,
                    "preview": doc[:200] + "..." if len(doc) > 200 else doc,
                    "metadata": vector_store.metadata[i] if i < len(vector_store.metadata) else None
                })
        
        return {
            "total_documents": len(vector_store.documents),
            "total_vectors": vector_store.index.ntotal if vector_store.index else 0,
            "dimension": vector_store.dimension,
            "sample_documents": sample_docs,
            "status": "healthy" if stats['total_vectors'] > 0 else "empty"
        }
    except Exception as e:
        logger.error(f"Error in debug endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))