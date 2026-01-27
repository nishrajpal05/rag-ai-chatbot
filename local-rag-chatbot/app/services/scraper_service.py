# import requests
# from bs4 import BeautifulSoup
# from typing import Tuple, List
# from urllib.parse import urlparse
# from app.utils.text_utils import clean_text, split_into_chunks
# from app.core.vector_store import vector_store
# from app.config import settings

# class ScraperService:
#     """Web scraping service"""
    
#     def __init__(self):
#         self.timeout = 30
#         self.headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
#         }
    
#     def scrape_url(self, url: str) -> Tuple[bool, str, int]:
#         """
#         Scrape website and add to vector store
        
#         Returns:
#             Tuple of (success, message, chunks_count)
#         """
#         try:
#             # Fetch webpage
#             response = requests.get(url, headers=self.headers, timeout=self.timeout)
#             response.raise_for_status()
            
#             # Parse HTML
#             soup = BeautifulSoup(response.content, 'html.parser')
            
#             # Remove script and style elements
#             for element in soup(['script', 'style', 'nav', 'footer', 'header']):
#                 element.decompose()
            
#             # Extract text from paragraphs
#             paragraphs = soup.find_all(['p', 'article', 'section'])
            
#             if not paragraphs:
#                 # Fallback to all text
#                 text = soup.get_text(separator='\n', strip=True)
#             else:
#                 text = '\n\n'.join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
            
#             if not text or len(text) < 100:
#                 return False, "Not enough content found on the webpage", 0
            
#             # Clean text
#             text = clean_text(text)
            
#             # Split into chunks
#             chunks = split_into_chunks(text, settings.CHUNK_SIZE, settings.CHUNK_OVERLAP)
            
#             # Create metadata
#             domain = urlparse(url).netloc
#             metadata = [
#                 {
#                     "source": f"{domain} (Web)",
#                     "url": url,
#                     "chunk_id": i,
#                     "total_chunks": len(chunks)
#                 }
#                 for i in range(len(chunks))
#             ]
            
#             # Add to vector store
#             vector_store.add_documents(chunks, metadata)
            
#             return True, f"Successfully scraped {domain}", len(chunks)
            
#         except requests.exceptions.Timeout:
#             return False, "Request timed out. Website took too long to respond.", 0
        
#         except requests.exceptions.ConnectionError:
#             return False, "Could not connect to the website. Check the URL and your internet connection.", 0
        
#         except requests.exceptions.HTTPError as e:
#             if e.response.status_code == 403:
#                 return False, "Access forbidden. Website blocked the scraping request.", 0
#             elif e.response.status_code == 404:
#                 return False, "Page not found (404).", 0
#             else:
#                 return False, f"HTTP Error: {e.response.status_code}", 0
        
#         except Exception as e:
#             return False, f"Error scraping website: {str(e)}", 0

# # Global instance
# scraper_service = ScraperService()


import logging
import requests
from bs4 import BeautifulSoup
from typing import Tuple
from urllib.parse import urlparse

from app.core.embeddings import embedding_model
from app.core.vector_store import vector_store
from app.utils.text_utils import smart_chunk_text

logger = logging.getLogger(__name__)

class ScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_url(self, url: str) -> Tuple[bool, str, int]:
        """Scrape website and add to vector store"""
        try:
            logger.info(f" Scraping URL: {url}")
            
            # Fetch the webpage
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer"]):
                script.decompose()
            
            # Extract text from paragraphs
            paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
            text_content = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            if not text_content or len(text_content) < 50:
                logger.warning(f" Insufficient content from {url}")
                return False, "Insufficient content extracted from URL", 0
            
            logger.info(f" Extracted {len(text_content)} characters from {url}")
            
            # Get domain name for source
            domain = urlparse(url).netloc
            
            # Chunk the text
            chunks = smart_chunk_text(
                text_content,
                chunk_size=1000,
                overlap=200,
                source=f"{domain} ({url})"
            )
            
            logger.info(f"Created {len(chunks)} chunks")
            
            if not chunks:
                return False, "Failed to create chunks", 0
            
            # Extract text and metadata
            chunk_texts = [chunk['text'] for chunk in chunks]
            chunk_metadata = [chunk['metadata'] for chunk in chunks]
            
            # Generate embeddings
            logger.info(f" Generating embeddings for {len(chunk_texts)} chunks...")
            embeddings = embedding_model.embed_documents(chunk_texts)
            logger.info(f" Generated {len(embeddings)} embeddings")
            
            # FIX: Pass all three required arguments
            vector_store.add_documents(
                documents=chunk_texts,      # List of text strings
                embeddings=embeddings,      # List of embedding vectors
                metadata=chunk_metadata     # List of metadata dicts
            )
            
            logger.info(f" Added {len(chunks)} chunks from {domain} to vector store")
            
            return True, f"Successfully scraped {domain}", len(chunks)
            
        except requests.exceptions.RequestException as e:
            logger.error(f" Error fetching URL: {str(e)}")
            return False, f"Error fetching URL: {str(e)}", 0
        except Exception as e:
            logger.error(f" Error scraping URL: {str(e)}", exc_info=True)
            return False, f"Error: {str(e)}", 0

scraper_service = ScraperService()