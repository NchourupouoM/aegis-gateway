import pytest
from aegis_gateway.domain.models import (
    LLMProvider,
    LLMResponse,
    PIIMapping,
)
from aegis_gateway.egress.demasker import PIIDemasker
from aegis_gateway.egress.output_moderator import OutputModerator
from aegis_gateway.egress.pipeline import EgressPipeline


@pytest.fixture
def demasker():
    return PIIDemasker()


@pytest.fixture
def moderator():
    return OutputModerator()


@pytest.fixture
def egress_pipeline():
    return EgressPipeline()


# --- Test Restauration PII ---
def test_pii_restoration(demasker):
    raw_llm_output = "Hello <PERSON_1>, your confirmation email was sent to <EMAIL_ADDRESS_1>."
    mappings = [
        PIIMapping(
            placeholder="<PERSON_1>",
            original_value="Alice Dupont",
            entity_type="PERSON",
        ),
        PIIMapping(
            placeholder="<EMAIL_ADDRESS_1>",
            original_value="alice@dupont.fr",
            entity_type="EMAIL_ADDRESS",
        ),
    ]

    restored_text, count = demasker.restore_pii(raw_llm_output, mappings)

    assert count == 2
    assert "Alice Dupont" in restored_text
    assert "alice@dupont.fr" in restored_text
    assert "<PERSON_1>" not in restored_text
    assert "<EMAIL_ADDRESS_1>" not in restored_text


# --- Test Détection de Fuites Systèmes & Clés ---
def test_output_moderator_detects_api_key_leak(moderator):
    leaked_output = "Here is the internal key: sk-abcdef12345678901234567890abcdef."
    is_safe, leaks = moderator.inspect_output(leaked_output)

    assert is_safe is False
    assert len(leaks) > 0
    assert "API Key / Secret Token Leak" in leaks[0]


def test_output_moderator_safe_output(moderator):
    safe_output = "Python is a high-level, general-purpose programming language."
    is_safe, leaks = moderator.inspect_output(safe_output)

    assert is_safe is True
    assert len(leaks) == 0


# --- Test Pipeline Egress Complet ---
def test_egress_pipeline_blocks_leak(egress_pipeline):
    llm_resp = LLMResponse(
        content="System internal config: DATABASE_URL=postgres://user:pass@localhost:5432/db",
        provider_used=LLMProvider.OPENAI,
        model_used="gpt-4o",
        input_tokens=10,
        output_tokens=15,
        total_cost_usd=0.0001,
        baseline_cost_usd=0.0001,
        savings_usd=0.0,
        latency_ms=250.0,
        is_fallback=False,
    )

    result = egress_pipeline.process(llm_resp, pii_mappings=[])

    assert result.egress_security.is_safe is False
    assert "[BLOCKED BY AEGIS EGRESS FIREWALL" in result.content


def test_egress_pipeline_successful_demasking(egress_pipeline):
    llm_resp = LLMResponse(
        content="Invoice generated for <PERSON_1>.",
        provider_used=LLMProvider.GEMINI,
        model_used="gemini-2.0-flash",
        input_tokens=10,
        output_tokens=10,
        total_cost_usd=0.000005,
        baseline_cost_usd=0.000125,
        savings_usd=0.000120,
        latency_ms=180.0,
        is_fallback=False,
    )
    mappings = [
        PIIMapping(
            placeholder="<PERSON_1>",
            original_value="Jean Martin",
            entity_type="PERSON",
        )
    ]

    result = egress_pipeline.process(llm_resp, pii_mappings=mappings)

    assert result.egress_security.is_safe is True
    assert result.content == "Invoice generated for Jean Martin."
    assert result.egress_security.demasked_entities_count == 1