from typing import Dict
from aegis_gateway.domain.models import LLMProvider


class ModelPricingCatalog:
    """Catalogue FinOps des coûts LLM (prix par million de tokens USD)."""

    # Format : (prix_input_par_million, prix_output_par_million)
    PRICING_PER_MILLION: Dict[str, tuple[float, float]] = {
        # Modèles Premium / Deep Reasoning
        "gpt-4o": (2.50, 10.00),
        "gpt-4o-2024-08-06": (2.50, 10.00),
        # Modèles Fast / Économiques
        "gpt-4o-mini": (0.15, 0.60),
        "gemini-2.5-flash": (0.30, 2.50),
        "gemini-2.5-flash-lite": (0.10, 0.40),
    }

    # Modèle de référence servant de Baseline pour mesurer les économies d'entreprise
    BASELINE_MODEL = "gpt-4o"

    @classmethod
    def calculate_cost(
        cls, model_name: str, input_tokens: int, output_tokens: int = 0
    ) -> float:
        """Calcule le coût exact en USD pour un volume de tokens donné."""
        input_price_m, output_price_m = cls.PRICING_PER_MILLION.get(
            model_name, cls.PRICING_PER_MILLION[cls.BASELINE_MODEL]
        )
        input_cost = (input_tokens / 1_000_000.0) * input_price_m
        output_cost = (output_tokens / 1_000_000.0) * output_price_m
        return round(input_cost + output_cost, 7)

    @classmethod
    def calculate_savings(
        cls, selected_model: str, input_tokens: int, output_tokens: int = 0
    ) -> tuple[float, float, float]:
        """Retourne (coût_modèle_sélectionné, coût_baseline_gpt4o, économie_réalisée)."""
        actual_cost = cls.calculate_cost(selected_model, input_tokens, output_tokens)
        baseline_cost = cls.calculate_cost(
            cls.BASELINE_MODEL, input_tokens, output_tokens
        )
        savings = max(0.0, baseline_cost - actual_cost)
        return actual_cost, baseline_cost, round(savings, 7)

    @classmethod
    def get_default_model_for_provider(
        cls, provider: LLMProvider, tier: str = "fast"
    ) -> str:
        if provider == LLMProvider.OPENAI:
            return "gpt-4o" if tier == "deep_reasoning" else "gpt-4o-mini"
        elif provider == LLMProvider.GEMINI:
            return "gemini-2.5-flash"
        return "gemini-2.5-flash"