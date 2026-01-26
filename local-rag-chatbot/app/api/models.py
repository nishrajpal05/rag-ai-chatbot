from pydantic import BaseModel, HttpUrl, validator
from typing import Optional, List

class UploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    chunks_created: Optional[int] = None

class ScrapeRequest(BaseModel):
    url: HttpUrl
    
class ScrapeResponse(BaseModel):
    success: bool
    message: str
    url: Optional[str] = None
    chunks_created: Optional[int] = None

class QuestionRequest(BaseModel):
    question: str
    
    @validator('question')
    def question_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Question cannot be empty')
        return v.strip()

class QuestionResponse(BaseModel):
    success: bool
    answer: str
    sources: Optional[List[str]] = None
    confidence: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    documents_loaded: int
    vector_store_ready: bool