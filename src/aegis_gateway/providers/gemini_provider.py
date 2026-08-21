from typing import List, Tuple
from google import genai
from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import ChatMessage, ChatRequest
from aegis_gateway.providers.base import BaseLLMProvider


class GeminiProvider(BaseLLMProvider):
    """Adaptateur officiel pour les modèles Google Gemini (Gemini 2.0 / 1.5 Flash)."""

    def __init__(self):
        settings = get_settings()
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

    async def generate_completion(
        self,
        messages: List[ChatMessage],
        request: ChatRequest,
        model_name: str = "gemini-2.5-flash",
    ) -> Tuple[str, int, int]:
        logger.debug(
            f"[Gemini] Dispatching request to model={model_name} (temperature={request.temperature})"
        )

        # Concaténation structurée des messages pour Gemini
        contents = []
        for m in messages:
            role_tag = "user" if m.role.value in ["user", "system"] else "model"
            contents.append(f"[{role_tag.upper()}]: {m.content}")

        full_prompt = "\n\n".join(contents)

        response = await self.client.aio.models.generate_content(
            model=model_name,
            contents=full_prompt,
        )

        content = response.text or ""

        # Extraction des tokens de métadonnées Gemini si disponibles
        input_tokens = 0
        output_tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            input_tokens = getattr(
                response.usage_metadata, "prompt_token_count", 0
            ) or len(full_prompt.split())
            output_tokens = getattr(
                response.usage_metadata, "candidates_token_count", 0
            ) or len(content.split())
        else:
            input_tokens = len(full_prompt.split())
            output_tokens = len(content.split())

        return content, input_tokens, output_tokens