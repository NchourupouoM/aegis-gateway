from typing import List, Tuple
from openai import AsyncOpenAI
from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import ChatMessage, ChatRequest
from aegis_gateway.providers.base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """Adaptateur officiel pour les modèles OpenAI (GPT-4o, GPT-4o-mini)."""

    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def generate_completion(
        self,
        messages: List[ChatMessage],
        request: ChatRequest,
        model_name: str = "gpt-4o",
    ) -> Tuple[str, int, int]:
        logger.debug(
            f"[OpenAI] Dispatching request to model={model_name} (temperature={request.temperature})"
        )

        formatted_messages = [
            {"role": m.role.value, "content": m.content} for m in messages
        ]

        response = await self.client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        choice = response.choices[0]
        content = choice.message.content or ""
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0

        return content, input_tokens, output_tokens