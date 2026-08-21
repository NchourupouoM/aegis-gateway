from typing import List
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import (
    EgressSecurityReport,
    GatewayResponse,
    LLMResponse,
    PIIMapping,
)
from aegis_gateway.egress.demasker import PIIDemasker
from aegis_gateway.egress.output_moderator import OutputModerator


class EgressPipeline:
    """Orchestrateur des contrôles de sécurité et de la désanonymisation en sortie."""

    def __init__(self):
        self.demasker = PIIDemasker()
        self.moderator = OutputModerator()

    def process(
        self,
        llm_response: LLMResponse,
        pii_mappings: List[PIIMapping],
    ) -> GatewayResponse:
        """Valide et transforme la réponse brute du LLM en réponse client sécurisée."""
        raw_content = llm_response.content

        # 1. Inspection anti-fuites de sécurité
        is_safe, detected_leaks = self.moderator.inspect_output(raw_content)

        if not is_safe:
            violation_msg = f"Output blocked by Egress Firewall: Sensitive data leakage detected ({', '.join(detected_leaks)})"
            logger.error(f"{violation_msg}")

            return GatewayResponse(
                content="[BLOCKED BY AEGIS EGRESS FIREWALL : SENSITIVE LEAK DETECTED]",
                provider=llm_response.provider_used,
                model=llm_response.model_used,
                input_tokens=llm_response.input_tokens,
                output_tokens=llm_response.output_tokens,
                total_tokens=llm_response.input_tokens + llm_response.output_tokens,
                cost_usd=llm_response.total_cost_usd,
                baseline_cost_usd=llm_response.baseline_cost_usd,
                savings_usd=llm_response.savings_usd,
                latency_ms=llm_response.latency_ms,
                is_fallback=llm_response.is_fallback,
                fallback_reason=llm_response.fallback_reason,
                pii_anonymized=len(pii_mappings) > 0,
                egress_security=EgressSecurityReport(
                    is_safe=False,
                    violation_reason=violation_msg,
                    leaks_detected=detected_leaks,
                    demasked_entities_count=0,
                ),
            )

        # 2. Désanonymisation réversible des PII
        final_content, demasked_count = self.demasker.restore_pii(
            text=raw_content,
            mappings=pii_mappings,
        )

        return GatewayResponse(
            content=final_content,
            provider=llm_response.provider_used,
            model=llm_response.model_used,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
            total_tokens=llm_response.input_tokens + llm_response.output_tokens,
            cost_usd=llm_response.total_cost_usd,
            baseline_cost_usd=llm_response.baseline_cost_usd,
            savings_usd=llm_response.savings_usd,
            latency_ms=llm_response.latency_ms,
            is_fallback=llm_response.is_fallback,
            fallback_reason=llm_response.fallback_reason,
            pii_anonymized=len(pii_mappings) > 0,
            egress_security=EgressSecurityReport(
                is_safe=True,
                violation_reason=None,
                leaks_detected=[],
                demasked_entities_count=demasked_count,
            ),
        )