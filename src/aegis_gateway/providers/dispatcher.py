import time
from typing import Dict, List
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import (
    ChatMessage,
    ChatRequest,
    LLMProvider,
    LLMResponse,
    RoutingDecision,
)
from aegis_gateway.providers.base import BaseLLMProvider
from aegis_gateway.providers.circuit_breaker import CircuitBreaker
from aegis_gateway.providers.gemini_provider import GeminiProvider
from aegis_gateway.providers.openai_provider import OpenAIProvider
from aegis_gateway.router.pricing import ModelPricingCatalog


class ResilientDispatcher:
    """Gestionnaire d'exécution avec Circuit Breaker et Failover transparent."""

    def __init__(self):
        self.providers: Dict[LLMProvider, BaseLLMProvider] = {
            LLMProvider.OPENAI: OpenAIProvider(),
            LLMProvider.GEMINI: GeminiProvider(),
        }
        self.circuit_breakers: Dict[LLMProvider, CircuitBreaker] = {
            LLMProvider.OPENAI: CircuitBreaker(provider=LLMProvider.OPENAI),
            LLMProvider.GEMINI: CircuitBreaker(provider=LLMProvider.GEMINI),
        }

    async def dispatch(
        self,
        messages: List[ChatMessage],
        request: ChatRequest,
        decision: RoutingDecision,
    ) -> LLMResponse:
        """Exécute la requête avec protection de panne et basculement automatique."""
        primary_provider = decision.selected_provider
        primary_model = decision.selected_model
        fallback_provider = decision.fallback_provider
        fallback_model = decision.fallback_model

        start_time = time.perf_counter()

        # 1. Vérifier si le Circuit Breaker du primaire est ouvert
        primary_cb = self.circuit_breakers[primary_provider]
        if primary_cb.allow_request():
            try:
                # Tentative d'exécution sur le provider primaire
                provider_client = self.providers[primary_provider]
                content, in_tokens, out_tokens = (
                    await provider_client.generate_completion(
                        messages=messages,
                        request=request,
                        model_name=primary_model,
                    )
                )

                latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
                primary_cb.record_success()

                actual_cost, baseline_cost, savings = (
                    ModelPricingCatalog.calculate_savings(
                        selected_model=primary_model,
                        input_tokens=in_tokens,
                        output_tokens=out_tokens,
                    )
                )

                return LLMResponse(
                    content=content,
                    provider_used=primary_provider,
                    model_used=primary_model,
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_cost_usd=actual_cost,
                    baseline_cost_usd=baseline_cost,
                    savings_usd=savings,
                    latency_ms=latency_ms,
                    is_fallback=False,
                )

            except Exception as primary_error:
                primary_cb.record_failure()
                logger.warning(
                    f"Échec du provider primaire [{primary_provider.value} - {primary_model}]: {primary_error}. "
                    f"Basculement immédiat vers le Fallback [{fallback_provider.value} - {fallback_model}]..."
                )
        else:
            logger.warning(
                f"⚡ Circuit Breaker OUVERT pour [{primary_provider.value}]. Bypass direct vers le Fallback [{fallback_provider.value}]"
            )

        # 2. Exécution du Fallback (Plan de secours)
        fallback_start_time = time.perf_counter()
        fallback_client = self.providers[fallback_provider]
        fallback_cb = self.circuit_breakers[fallback_provider]

        try:
            content, in_tokens, out_tokens = (
                await fallback_client.generate_completion(
                    messages=messages,
                    request=request,
                    model_name=fallback_model,
                )
            )

            fallback_cb.record_success()
            total_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

            actual_cost, baseline_cost, savings = ModelPricingCatalog.calculate_savings(
                selected_model=fallback_model,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
            )

            logger.info(
                f"Failover réussi avec succès via [{fallback_provider.value} - {fallback_model}] en {total_latency_ms}ms"
            )

            return LLMResponse(
                content=content,
                provider_used=fallback_provider,
                model_used=fallback_model,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                total_cost_usd=actual_cost,
                baseline_cost_usd=baseline_cost,
                savings_usd=savings,
                latency_ms=total_latency_ms,
                is_fallback=True,
                fallback_reason=f"Primary provider {primary_provider.value} failed or circuit open",
            )

        except Exception as fallback_error:
            fallback_cb.record_failure()
            logger.critical(
                f"PANNES MULTIPLES : Le primaire ET le fallback ont échoué ! Error: {fallback_error}"
            )
            raise RuntimeError(
                f"Gateway Failover Exhausted: Both primary and fallback providers failed. ({fallback_error})"
            )