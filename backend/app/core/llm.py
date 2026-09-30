from openai import AsyncOpenAI

from app.core.config import settings


client = AsyncOpenAI(
    api_key=settings.llm_api_key,
    base_url=settings.llm_base_url,
)
