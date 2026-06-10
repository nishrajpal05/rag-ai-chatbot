import logging
from typing import Optional

from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)


class GroqLLMHandler:
    def __init__(self):
        self.model = settings.GROQ_MODEL
        self.client: Optional[Groq] = None

        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            logger.info(f"Initialized Groq LLM with model: {self.model}")
        else:
            logger.warning("GROQ_API_KEY is missing. /ask will return a configuration error until it is set.")

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        if not self.client:
            return "Error: GROQ_API_KEY is not configured."

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that answers questions based only on provided context.",
                    },
                    {"role": "user", "content": prompt},
                ],
                model=self.model,
                temperature=0.1,
                max_tokens=max_tokens,
                top_p=0.9,
            )

            answer = chat_completion.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"Error generating response from Groq: {str(e)}")
            return f"Error: Unable to generate response. {str(e)}"

    def check_health(self) -> bool:
        if not self.client:
            return False

        try:
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model=self.model,
                max_tokens=5,
            )
            logger.info("Groq API is healthy")
            return True
        except Exception as e:
            logger.error(f"Groq API health check failed: {str(e)}")
            return False


llm_handler = GroqLLMHandler()
