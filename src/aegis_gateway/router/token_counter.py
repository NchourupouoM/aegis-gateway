from typing import List
import tiktoken
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import ChatMessage


class TokenCounter:
    """Calculateur de tokens optimisé basé sur tiktoken."""

    def __init__(self, default_encoding: str = "o200k_base"):
        try:
            self.encoder = tiktoken.get_encoding(default_encoding)
        except Exception:
            logger.warning(
                f"Encoding {default_encoding} indisponible, fallback vers cl100k_base"
            )
            self.encoder = tiktoken.get_encoding("cl100k_base")

    def count_text_tokens(self, text: str) -> int:
        if not text:
            return 0
        return len(self.encoder.encode(text, disallowed_special=()))

    def count_messages_tokens(self, messages: List[ChatMessage]) -> int:
        """Calcule le nombre de tokens avec le framing de conversation chat format."""
        num_tokens = 0
        for message in messages:
            # +3 tokens d'overhead par message (format <|start|>role/name content <|end|>)
            num_tokens += 3
            num_tokens += self.count_text_tokens(message.content)
        num_tokens += 3  # Overhead de fin de prompt d'amorçage
        return num_tokens