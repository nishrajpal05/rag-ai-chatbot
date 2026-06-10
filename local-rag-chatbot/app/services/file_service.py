import logging
from pathlib import Path
from typing import Tuple

from fastapi import UploadFile

from app.core.document_processor import document_processor
from app.core.embeddings import embedding_model
from app.core.vector_store import vector_store
from app.utils.text_utils import smart_chunk_text
from app.utils.validators import sanitize_filename, validate_file_extension, validate_file_size

logger = logging.getLogger(__name__)


class FileService:
    def __init__(self):
        self.upload_dir = Path("app/storage/uploads")
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def process_upload(self, file: UploadFile) -> Tuple[bool, str, int]:
        try:
            if not file.filename:
                return False, "Missing filename", 0

            safe_filename = sanitize_filename(file.filename)
            if not validate_file_extension(safe_filename):
                return False, "Unsupported file type", 0

            content = await file.read()
            if not validate_file_size(len(content)):
                return False, "File exceeds size limit", 0

            logger.info(f"Processing file: {safe_filename}")

            file_path = self.upload_dir / safe_filename
            with open(file_path, "wb") as f:
                f.write(content)

            text = document_processor.extract_text(str(file_path))
            if not text or len(text.strip()) < 10:
                return False, "No text content found in file", 0

            chunks = smart_chunk_text(
                text,
                chunk_size=1000,
                overlap=200,
                source=safe_filename,
            )
            if not chunks:
                return False, "Failed to create chunks", 0

            chunk_texts = [chunk["text"] for chunk in chunks]
            chunk_metadata = [chunk["metadata"] for chunk in chunks]

            embeddings = embedding_model.embed_documents(chunk_texts)
            vector_store.add_documents(
                documents=chunk_texts,
                embeddings=embeddings,
                metadata=chunk_metadata,
            )

            logger.info(f"Added {len(chunks)} chunks to vector store")
            return True, f"Successfully processed {safe_filename}", len(chunks)

        except Exception as e:
            logger.error(f"Error processing file: {str(e)}", exc_info=True)
            return False, f"Error: {str(e)}", 0


file_service = FileService()
