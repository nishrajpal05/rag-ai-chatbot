import os
from pathlib import Path
from app.config import settings

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.xlsx', '.txt'}

def validate_file_extension(filename: str) -> bool:
    """Check if file extension is allowed"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS

def validate_file_size(file_size: int) -> bool:
    """Check if file size is within limit"""
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    return file_size <= max_bytes

def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal"""
    # Remove any path components
    filename = os.path.basename(filename)
    # Remove any special characters
    filename = "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-'))
    return filename