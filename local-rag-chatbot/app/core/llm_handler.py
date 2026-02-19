import logging
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)

class GroqLLMHandler:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info(f"Initialized Groq LLM with model: {self.model}")
    
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate response from Groq API"""
        try:
            logger.info(f" Generating response with {self.model}")
            logger.debug(f"Prompt length: {len(prompt)} chars")
            
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions based only on provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=max_tokens,
                top_p=0.9,
            )
            
            answer = chat_completion.choices[0].message.content.strip()
            logger.info(f" Generated {len(answer)} characters")
            
            return answer
            
        except Exception as e:
            logger.error(f" Error generating response from Groq: {str(e)}")
            return f"Error: Unable to generate response. {str(e)}"
    
    def check_health(self) -> bool:
        """Check if Groq API is accessible"""
        try:
            # Try a simple completion
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=5
            )
            logger.info(" Groq API is healthy")
            return True
        except Exception as e:
            logger.error(f" Groq API health check failed: {str(e)}")
            return False

# Global singleton
llm_handler = GroqLLMHandler()