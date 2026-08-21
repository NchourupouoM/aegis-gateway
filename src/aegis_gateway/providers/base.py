from abc import ABC, abstractmethod
from typing import List, Tuple
from aegis_gateway.domain.models import ChatMessage, ChatRequest


class BaseLLMProvider(ABC):
    """Interface unifiée pour tous les fournisseurs de modèles LLM."""

    @abstractmethod
    async def generate_completion(
        self,
        messages: List[ChatMessage],
        request: ChatRequest,
        model_name: str,
    ) -> Tuple[str, int, int]:
        """Exécute l'appel LLM.

        Retourne un tuple : (texte_généré, input_tokens, output_tokens)
        """
        pass