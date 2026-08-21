import re
from typing import List, Tuple
from aegis_gateway.domain.models import ChatMessage


class ComplexityAnalyzer:
    """Évalue la complexité cognitive d'une requête pour guider le routage FinOps."""

    # Mots-clés et motifs indicatifs d'un raisonnement complexe
    HIGH_REASONING_PATTERNS: List[Tuple[re.Pattern, float]] = [
        (
            re.compile(
                r"\b(mathematical proof|formal derivation|solve equation|differential equation)\b",
                re.IGNORECASE,
            ),
            0.85,
        ),
        (
            re.compile(
                r"\b(refactor architecture|system design|concurrency deadlock|assembly code|reverse engineer)\b",
                re.IGNORECASE,
            ),
            0.80,
        ),
        (
            re.compile(
                r"\b(step-by-step reasoning|chain of thought|critique this proof|logical deduction)\b",
                re.IGNORECASE,
            ),
            0.75,
        ),
        (
            re.compile(
                r"\b(write a complex python script|implement algorithm from scratch|dynamic programming)\b",
                re.IGNORECASE,
            ),
            0.70,
        ),
    ]

    # Mots-clés indicatifs de tâches légères / directes
    LOW_REASONING_PATTERNS: List[Tuple[re.Pattern, float]] = [
        (
            re.compile(
                r"\b(translate to|correct grammar|fix typos|summarize this in \d+ bullet points)\b",
                re.IGNORECASE,
            ),
            -0.40,
        ),
        (
            re.compile(
                r"\b(extract keywords|format as json|convert to csv|extract email addresses)\b",
                re.IGNORECASE,
            ),
            -0.35,
        ),
        (
            re.compile(
                r"\b(what is the capital of|who wrote|define the term)\b", re.IGNORECASE
            ),
            -0.30,
        ),
    ]

    def analyze_complexity(
        self, messages: List[ChatMessage], total_tokens: int
    ) -> float:
        """Calcule un score de complexité normalisé entre 0.0 et 1.0."""
        combined_text = " ".join([m.content for m in messages])
        base_score = 0.30  # Score médian de base

        # 1. Analyse des patterns à haut raisonnement
        for pattern, weight in self.HIGH_REASONING_PATTERNS:
            if pattern.search(combined_text):
                base_score += weight

        # 2. Analyse des patterns à faible complexité (réducteurs)
        for pattern, weight in self.LOW_REASONING_PATTERNS:
            if pattern.search(combined_text):
                base_score += weight

        # 3. Facteur taille de prompt : Les très gros contextes de lecture simple profitent à Gemini Flash
        if total_tokens > 4000:
            # Léger bonus d'efficacité pour le traitement bulk
            base_score = max(0.20, base_score - 0.15)

        # Clamping entre 0.0 et 1.0
        final_score = max(0.0, min(1.0, base_score))
        return round(final_score, 3)