import re
from typing import List, Tuple
from aegis_gateway.core.logger import logger


class OutputModerator:
    """Détecte les fuites de clés de sécurité, de variables d'environnement ou de consignes système."""

    LEAK_PATTERNS: List[Tuple[str, re.Pattern]] = [
        (
            "API Key / Secret Token Leak",
            re.compile(
                r"(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|Bearer\s+[a-zA-Z0-9_\-\.]{25,})",
                re.IGNORECASE,
            ),
        ),
        (
            "Internal System Prompt Disclosure",
            re.compile(
                r"(INTERNAL_SYSTEM_INSTRUCTIONS:|SYSTEM_CONFIDENTIAL_PROMPT:|<\|system\|>)",
                re.IGNORECASE,
            ),
        ),
        (
            "Environment Variable / Database Credentials",
            re.compile(
                r"(DATABASE_URL=postgres|AWS_SECRET_ACCESS_KEY=|PRIVATE_KEY=)",
                re.IGNORECASE,
            ),
        ),
    ]

    def inspect_output(self, text: str) -> Tuple[bool, List[str]]:
        """Vérifie la sécurité du contenu généré.

        Retourne (is_safe: bool, detected_violations: List[str])
        """
        if not text:
            return True, []

        detected_leaks: List[str] = []

        for pattern_name, regex in self.LEAK_PATTERNS:
            if regex.search(text):
                detected_leaks.append(pattern_name)

        if detected_leaks:
            logger.critical(
                f"EGRESS VIOLATION : Fuite critique détectée dans la sortie du LLM: {detected_leaks}"
            )
            return False, detected_leaks

        return True, []