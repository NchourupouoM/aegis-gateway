from typing import List
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import (
    ChatMessage,
    ChatRequest,
    LLMProvider,
    ModelTier,
    RoutingDecision,
)
from aegis_gateway.router.complexity_analyzer import ComplexityAnalyzer
from aegis_gateway.router.pricing import ModelPricingCatalog
from aegis_gateway.router.token_counter import TokenCounter


class SmartRouter:
    """Routeur intelligent guidé par la complexité, les coûts et la résilience."""

    COMPLEXITY_THRESHOLD = 0.65  # Au-dessus -> Deep Reasoning (GPT-4o)

    def __init__(self):
        self.token_counter = TokenCounter()
        self.complexity_analyzer = ComplexityAnalyzer()

    def route(
        self, messages: List[ChatMessage], original_request: ChatRequest
    ) -> RoutingDecision:
        """Prend la décision de routage optimale pour la requête."""
        # 1. Comptage des tokens
        input_tokens = self.token_counter.count_messages_tokens(messages)

        # 2. Vérification d'une préférence forcée dans les métadonnées de la requête
        requested_tier = original_request.metadata.get("tier", ModelTier.AUTO.value)

        # 3. Analyse de complexité
        complexity_score = self.complexity_analyzer.analyze_complexity(
            messages, input_tokens
        )

        # 4. Décision de Tier
        if requested_tier == ModelTier.DEEP_REASONING.value:
            tier = ModelTier.DEEP_REASONING
            selected_provider = LLMProvider.OPENAI
            selected_model = "gpt-4o"
            fallback_provider = LLMProvider.GEMINI
            fallback_model = "gemini-2.5-flash"
            reason = "Explicitly requested DEEP_REASONING tier via metadata"
        elif requested_tier == ModelTier.FAST.value:
            tier = ModelTier.FAST
            selected_provider = LLMProvider.GEMINI
            selected_model = "gemini-2.5-flash"
            fallback_provider = LLMProvider.OPENAI
            fallback_model = "gpt-4o-mini"
            reason = "Explicitly requested FAST tier via metadata"
        else:
            # Décision intelligente automatique
            if complexity_score >= self.COMPLEXITY_THRESHOLD:
                tier = ModelTier.DEEP_REASONING
                selected_provider = LLMProvider.OPENAI
                selected_model = "gpt-4o"
                fallback_provider = LLMProvider.GEMINI
                fallback_model = "gemini-2.5-flash"
                reason = f"High reasoning complexity detected (score: {complexity_score:.2f} >= {self.COMPLEXITY_THRESHOLD})"
            else:
                tier = ModelTier.FAST
                selected_provider = LLMProvider.GEMINI
                selected_model = "gemini-2.5-flash"
                fallback_provider = LLMProvider.OPENAI
                fallback_model = "gpt-4o-mini"
                reason = f"Standard/Fast task optimal for Gemini Flash (score: {complexity_score:.2f} < {self.COMPLEXITY_THRESHOLD})"

        # 5. Calculs FinOps prédictifs
        actual_cost, baseline_cost, savings = ModelPricingCatalog.calculate_savings(
            selected_model=selected_model,
            input_tokens=input_tokens,
            output_tokens=0,  # Estimation pré-exécution
        )

        logger.info(
            f"Routing Decision: [{selected_provider.value.upper()} - {selected_model}] | Tier: {tier.value} | "
            f"Tokens: {input_tokens} | Cost: ${actual_cost:.6f} (Saved: ${savings:.6f} vs Baseline)"
        )

        return RoutingDecision(
            selected_provider=selected_provider,
            selected_model=selected_model,
            fallback_provider=fallback_provider,
            fallback_model=fallback_model,
            estimated_input_tokens=input_tokens,
            complexity_score=complexity_score,
            routing_reason=reason,
            tier=tier,
            estimated_input_cost_usd=actual_cost,
            baseline_cost_usd=baseline_cost,
            estimated_savings_usd=savings,
        )