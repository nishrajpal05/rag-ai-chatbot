import logging
import os
from pathlib import Path
from typing import Tuple
from fastapi import UploadFile

from app.core.document_processor import document_processor
from app.core.embeddings import embedding_model
from app.core.vector_store import vector_store
from app.utils.text_utils import smart_chunk_text

logger = logging.getLogger(__name__)

class FileService:
    def __init__(self):
        self.upload_dir = Path("app/storage/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def process_upload(self, file: UploadFile) -> Tuple[bool, str, int]:
        """Process uploaded file and add to vector store"""
        try:
            logger.info(f" Processing file: {file.filename}")
            
            # Save file temporarily
            file_path = self.upload_dir / file.filename
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            logger.info(f" Saved file to: {file_path}")
            
            # Extract text based on file type
            text = document_processor.extract_text(str(file_path))
            
            if not text or len(text.strip()) < 10:
                logger.warning(f" No text extracted from {file.filename}")
                return False, "No text content found in file", 0
            
            logger.info(f" Extracted {len(text)} characters")
            
            # Chunk the text
            chunks = smart_chunk_text(
                text, 
                chunk_size=1000, 
                overlap=200,
                source=file.filename
            )
            
            logger.info(f" Created {len(chunks)} chunks")
            
            if not chunks:
                return False, "Failed to create chunks", 0
            
            # Extract just the text from chunks (they contain metadata too)
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_metadata = [chunk['metadata'] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f" Generating embeddings for {len(chunk_texts)} chunks...")
            embeddings = embedding_model.embed_documents(chunk_texts)
            logger.info(f" Generated {len(embeddings)} embeddings")
            
            #  FIX: Pass all three required arguments
            vector_store.add_documents(
                documents=chunk_texts,      # List of text strings
                embeddings=embeddings,      # List of embedding vectors
                metadata=chunk_metadata     # List of metadata dicts
            )
            
            logger.info(f" Added {len(chunks)} chunks to vector store")
            
            return True, f"Successfully processed {file.filename}", len(chunks)
            
        except Exception as e:
            logger.error(f" Error processing file: {str(e)}", exc_info=True)
            return False, f"Error: {str(e)}", 0

file_service = FileService()