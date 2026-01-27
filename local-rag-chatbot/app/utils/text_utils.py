# import re
# from typing import List

# def clean_text(text: str) -> str:
#     """Clean and normalize text"""
#     # Remove extra whitespace
#     text = re.sub(r'\s+', ' ', text)
#     # Remove special characters but keep punctuation
#     text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
#     # Remove multiple newlines
#     text = re.sub(r'\n+', '\n', text)
#     return text.strip()

# def split_into_chunks(text: str, chunk_size: int, overlap: int) -> List[str]:
#     """
#     Split text into overlapping chunks
    
#     Args:
#         text: Input text
#         chunk_size: Maximum characters per chunk
#         overlap: Number of overlapping characters
#     """
#     if len(text) <= chunk_size:
#         return [text]
    
#     chunks = []
#     start = 0
    
#     while start < len(text):
#         end = start + chunk_size
        
#         # Try to break at sentence boundary
#         if end < len(text):
#             # Look for sentence end within last 200 chars of chunk
#             last_period = text.rfind('.', end - 200, end)
#             last_question = text.rfind('?', end - 200, end)
#             last_exclamation = text.rfind('!', end - 200, end)
            
#             sentence_end = max(last_period, last_question, last_exclamation)
            
#             if sentence_end != -1:
#                 end = sentence_end + 1
        
#         chunk = text[start:end].strip()
#         if chunk:
#             chunks.append(chunk)
        
#         # Move start position considering overlap
#         start = end - overlap if end < len(text) else end
    
#     return chunks

# def extract_keywords(text: str, top_n: int = 5) -> List[str]:
#     """Extract simple keywords from text (basic implementation)"""
#     # Remove common words
#     common_words = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'but', 'in', 'with', 'to', 'for', 'of', 'as', 'by'}
    
#     words = re.findall(r'\b\w+\b', text.lower())
#     word_freq = {}
    
#     for word in words:
#         if word not in common_words and len(word) > 3:
#             word_freq[word] = word_freq.get(word, 0) + 1
    
#     sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
#     return [word for word, freq in sorted_words[:top_n]]


# import re
# from typing import List, Dict

# def smart_chunk_text(
#     text: str, 
#     chunk_size: int = 1000, 
#     overlap: int = 200,
#     source: str = "unknown"
# ) -> List[Dict]:
#     """
#     Smart text chunking with sentence boundary awareness
    
#     Returns:
#         List of dicts with 'text' and 'metadata' keys
#     """
#     if not text or len(text.strip()) == 0:
#         return []
    
#     # Clean the text
#     text = text.strip()
#     text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    
#     # Split into sentences (basic approach)
#     sentences = re.split(r'(?<=[.!?])\s+', text)
    
#     chunks = []
#     current_chunk = ""
#     chunk_id = 0
    
#     for sentence in sentences:
#         # If adding this sentence exceeds chunk_size and we have content
#         if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
#             # Save current chunk
#             chunks.append({
#                 'text': current_chunk.strip(),
#                 'metadata': {
#                     'source': source,
#                     'chunk_id': chunk_id,
#                     'total_chunks': 0  # Will update later
#                 }
#             })
            
#             # Start new chunk with overlap
#             # Take last 'overlap' characters from current chunk
#             overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
#             current_chunk = overlap_text + " " + sentence
#             chunk_id += 1
#         else:
#             current_chunk += " " + sentence if current_chunk else sentence
    
#     # Add the last chunk
#     if current_chunk.strip():
#         chunks.append({
#             'text': current_chunk.strip(),
#             'metadata': {
#                 'source': source,
#                 'chunk_id': chunk_id,
#                 'total_chunks': 0
#             }
#         })
    
#     # Update total_chunks in metadata
#     total = len(chunks)
#     for chunk in chunks:
#         chunk['metadata']['total_chunks'] = total
    
#     return chunks



import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

def split_into_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Simple text splitting into chunks (legacy function)"""
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def smart_chunk_text(
    text: str, 
    chunk_size: int = 1000, 
    overlap: int = 200,
    source: str = "unknown"
) -> List[Dict]:
    """
    Smart text chunking with sentence boundary awareness
    
    Returns:
        List of dicts with 'text' and 'metadata' keys
    """
    if not text or len(text.strip()) == 0:
        return []
    
    # Clean the text
    text = clean_text(text)
    
    # Split into sentences (basic approach)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = ""
    chunk_id = 0
    
    for sentence in sentences:
        # If adding this sentence exceeds chunk_size and we have content
        if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
            # Save current chunk
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': {
                    'source': source,
                    'chunk_id': chunk_id,
                    'total_chunks': 0  # Will update later
                }
            })
            
            # Start new chunk with overlap
            overlap_text = current_chunk[-overlap:] if len(current_chunk) > overlap else current_chunk
            current_chunk = overlap_text + " " + sentence
            chunk_id += 1
        else:
            current_chunk += " " + sentence if current_chunk else sentence
    
    # Add the last chunk
    if current_chunk.strip():
        chunks.append({
            'text': current_chunk.strip(),
            'metadata': {
                'source': source,
                'chunk_id': chunk_id,
                'total_chunks': 0
            }
        })
    
    # Update total_chunks in metadata
    total = len(chunks)
    for chunk in chunks:
        chunk['metadata']['total_chunks'] = total
    
    return chunks