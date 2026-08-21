from typing import List, Tuple
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import PIIMapping


class PIIDemasker:
    """Restaure les entités originales masquées dans la réponse du modèle."""

    def restore_pii(
        self, text: str, mappings: List[PIIMapping]
    ) -> Tuple[str, int]:
        """Remplace chaque placeholder par sa valeur originale dans le texte généré."""
        if not text or not mappings:
            return text, 0

        restored_text = text
        restored_count = 0

        for mapping in mappings:
            if mapping.placeholder in restored_text:
                restored_text = restored_text.replace(
                    mapping.placeholder, mapping.original_value
                )
                restored_count += 1

        if restored_count > 0:
            logger.debug(
                f"PII Restoration: {restored_count} entité(s) réinjectée(s) dans la réponse."
            )

        return restored_text, restored_count