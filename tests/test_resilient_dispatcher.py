from unittest.mock import AsyncMock, patch
import pytest
from aegis_gateway.domain.models import (
    ChatMessage,
    ChatRequest,
    CircuitState,
    LLMProvider,
    ModelTier,
    Role,
    RoutingDecision,
)
from aegis_gateway.providers.circuit_breaker import CircuitBreaker
from aegis_gateway.providers.dispatcher import ResilientDispatcher


@pytest.fixture
def sample_request():
    return ChatRequest(
        messages=[
            ChatMessage(
                role=Role.USER,
                content="Explain Quantum Computing in simple terms.",
            )
        ]
    )


@pytest.fixture
def sample_decision():
    return RoutingDecision(
        selected_provider=LLMProvider.OPENAI,
        selected_model="gpt-4o",
        fallback_provider=LLMProvider.GEMINI,
        fallback_model="gemini-2.5-flash",
        estimated_input_tokens=50,
        complexity_score=0.8,
        routing_reason="High reasoning",
        tier=ModelTier.DEEP_REASONING,
        estimated_input_cost_usd=0.000125,
        baseline_cost_usd=0.000125,
        estimated_savings_usd=0.0,
    )


# --- Test Succès Primaire ---
@pytest.mark.asyncio
async def test_dispatcher_primary_success(sample_request, sample_decision):
    dispatcher = ResilientDispatcher()

    # Mock de la complétion OpenAI avec succès
    dispatcher.providers[LLMProvider.OPENAI].generate_completion = AsyncMock(
        return_value=("Quantum computing uses qubits.", 50, 20)
    )

    response = await dispatcher.dispatch(
        sample_request.messages, sample_request, sample_decision
    )

    assert response.is_fallback is False
    assert response.provider_used == LLMProvider.OPENAI
    assert response.model_used == "gpt-4o"
    assert "Quantum" in response.content


# --- Test Auto-Fallback Transparent en cas d'erreur 429/500 ---
@pytest.mark.asyncio
async def test_dispatcher_auto_fallback_on_primary_failure(
    sample_request, sample_decision
):
    dispatcher = ResilientDispatcher()

    # Simulation d'une erreur 429 Rate Limit sur OpenAI
    dispatcher.providers[LLMProvider.OPENAI].generate_completion = AsyncMock(
        side_effect=Exception("HTTP 429: Rate Limit Exceeded on OpenAI")
    )

    # Le Fallback Gemini répond avec succès
    dispatcher.providers[LLMProvider.GEMINI].generate_completion = AsyncMock(
        return_value=("Fallback response from Gemini.", 50, 15)
    )

    response = await dispatcher.dispatch(
        sample_request.messages, sample_request, sample_decision
    )

    # Vérifications de la résilience
    assert response.is_fallback is True
    assert response.provider_used == LLMProvider.GEMINI
    assert response.model_used == "gemini-2.5-flash"
    assert response.fallback_reason is not None
    assert "Fallback response from Gemini." in response.content


# --- Test Circuit Breaker ---
def test_circuit_breaker_transitions():
    cb = CircuitBreaker(
        provider=LLMProvider.OPENAI, failure_threshold=2, recovery_timeout_sec=5.0
    )

    assert cb.state == CircuitState.CLOSED
    assert cb.allow_request() is True

    # 1ère panne
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED

    # 2ème panne -> Ouverture du circuit
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    assert cb.allow_request() is False  # Bloque les requêtes pour protéger le système