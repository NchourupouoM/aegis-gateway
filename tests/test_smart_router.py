import pytest
from aegis_gateway.domain.models import (
    ChatMessage,
    ChatRequest,
    LLMProvider,
    ModelTier,
    Role,
)
from aegis_gateway.router.pricing import ModelPricingCatalog
from aegis_gateway.router.smart_router import SmartRouter
from aegis_gateway.router.token_counter import TokenCounter


@pytest.fixture
def smart_router():
    return SmartRouter()


@pytest.fixture
def token_counter():
    return TokenCounter()


# --- Test Comptage de Tokens ---
def test_token_counter_precision(token_counter):
    text = "Hello world! This is a test prompt for Aegis Gateway."
    count = token_counter.count_text_tokens(text)
    assert count > 0
    assert isinstance(count, int)

    messages = [
        ChatMessage(role=Role.USER, content="Hello!"),
        ChatMessage(role=Role.ASSISTANT, content="Hi there!"),
    ]
    msg_tokens = token_counter.count_messages_tokens(messages)
    assert msg_tokens > len(messages) * 3


def test_pricing_and_savings_calculation():
    input_tokens = 100_000

    gemini_cost, baseline_cost, savings = ModelPricingCatalog.calculate_savings(
        selected_model="gemini-2.5-flash", input_tokens=input_tokens
    )

    assert baseline_cost == 0.25  # 100k tokens à $2.50/M sur GPT-4o
    assert gemini_cost == 0.03    # 100k tokens à $0.30/M sur Gemini 2.5 Flash
    assert savings == 0.22        # $0.25 - $0.03 = $0.22 d'économie


# --- Test Routage Tâche Simple -> Gemini Flash ---
def test_smart_routing_simple_task(smart_router):
    messages = [
        ChatMessage(
            role=Role.USER,
            content="Please summarize this in 3 bullet points and translate to French.",
        )
    ]
    req = ChatRequest(messages=messages)
    decision = smart_router.route(messages, req)

    assert decision.selected_provider == LLMProvider.GEMINI
    assert decision.selected_model == "gemini-2.5-flash"
    assert decision.tier == ModelTier.FAST
    assert decision.estimated_savings_usd > 0


# --- Test Routage Tâche Complexe -> GPT-4o ---
def test_smart_routing_complex_task(smart_router):
    messages = [
        ChatMessage(
            role=Role.USER,
            content="Provide a formal mathematical proof for the convergence of gradient descent with step-by-step reasoning.",
        )
    ]
    req = ChatRequest(messages=messages)
    decision = smart_router.route(messages, req)

    assert decision.selected_provider == LLMProvider.OPENAI
    assert decision.selected_model == "gpt-4o"
    assert decision.tier == ModelTier.DEEP_REASONING