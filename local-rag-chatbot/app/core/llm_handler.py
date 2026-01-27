
import logging
import requests
from typing import Optional

logger = logging.getLogger(__name__)

class OllamaLLMHandler:
    def __init__(self, model_name: str = "gemma:7b", base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
        logger.info(f"Initialized Ollama LLM with model: {model_name}")
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response from Ollama"""
        try:
            logger.info(f" Generating response with {self.model_name}")
            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": 0.1,  # Low temperature for factual responses
                    "top_p": 0.9,
                    "top_k": 40
                }
            }
            
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=60  # 60 second timeout
            )
            
            if response.status_code != 200:
                logger.error(f" Ollama API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return "Error: Unable to generate response from LLM."
            
            result = response.json()
            answer = result.get('response', '').strip()
            
            logger.info(f" Generated {len(answer)} characters")
            return answer
            
        except requests.exceptions.Timeout:
            logger.error(" Ollama request timed out")
            return "Error: Request timed out. The model may be too slow."
        except requests.exceptions.ConnectionError:
            logger.error(" Cannot connect to Ollama. Is it running?")
            return "Error: Cannot connect to Ollama. Please ensure Ollama is running."
        except Exception as e:
            logger.error(f" Error generating response: {str(e)}")
            return f"Error: {str(e)}"
    
    def check_health(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code != 200:
                return False
            
            # Check if our model is available
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            
            # Check for exact match or base model name
            model_available = any(
                self.model_name in name or name.startswith(self.model_name.split(':')[0])
                for name in model_names
            )
            
            if model_available:
                logger.info(f" Model {self.model_name} is available")
            else:
                logger.warning(f" Model {self.model_name} not found. Available: {model_names}")
            
            return model_available
            
        except Exception as e:
            logger.error(f" Health check failed: {str(e)}")
            return False

#  CREATE SINGLETON INSTANCE
llm_handler = OllamaLLMHandler()