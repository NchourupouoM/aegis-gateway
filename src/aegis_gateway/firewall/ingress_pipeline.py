from typing import List
from aegis_gateway.core.config import get_settings
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import (
    ChatMessage,
    ChatRequest,
    IngressSecurityReport,
    InjectionScanResult,
    PIIMaskingResult,
    PIIMapping,
    ThreatLevel,
)
from aegis_gateway.firewall.pii_anonymizer import PIIAnonymizer
from aegis_gateway.firewall.prompt_injection_scanner import PromptInjectionScanner


class IngressFirewall:
    """Orchestrateur de sécurité pour l'inspection des flux entrants."""

    def __init__(self):
        self.settings = get_settings()
        self.pii_anonymizer = PIIAnonymizer()
        self.injection_scanner = PromptInjectionScanner()

    def process(self, request: ChatRequest) -> IngressSecurityReport:
        """Exécute l'inspection de sécurité et l'anonymisation sur tous les messages de la requête."""
        processed_messages: List[ChatMessage] = []
        all_pii_mappings: List[PIIMapping] = []
        highest_threat = InjectionScanResult(
            is_threat=False,
            threat_level=ThreatLevel.SAFE,
            detected_patterns=[],
            risk_score=0.0,
        )

        for message in request.messages:
            content = message.content

            # 1. Vérification des injections de prompt si activée
            if self.settings.ENABLE_JAILBREAK_DETECTION:
                scan_res = self.injection_scanner.scan(content)
                if scan_res.risk_score > highest_threat.risk_score:
                    highest_threat = scan_res

                # Blocage immédiat si menace critique
                if scan_res.threat_level == ThreatLevel.CRITICAL:
                    logger.error(f"Requête bloquée pour Jailbreak: {scan_res.detected_patterns}")
                    return IngressSecurityReport(
                        is_blocked=True,
                        block_reason=f"Security Violation: Critical Prompt Injection detected ({', '.join(scan_res.detected_patterns)})",
                        injection_result=scan_res,
                        pii_result=PIIMaskingResult(sanitized_text="", anonymized_entities=[], has_pii=False),
                        processed_messages=[],
                    )

            # 2. Masquage PII si activé
            if self.settings.ENABLE_PII_MASKING:
                pii_res = self.pii_anonymizer.mask_text(content)
                sanitized_content = pii_res.sanitized_text
                all_pii_mappings.extend(pii_res.anonymized_entities)
            else:
                sanitized_content = content

            processed_messages.append(ChatMessage(role=message.role, content=sanitized_content))

        combined_pii_result = PIIMaskingResult(
            sanitized_text="\n".join([m.content for m in processed_messages]),
            anonymized_entities=all_pii_mappings,
            has_pii=len(all_pii_mappings) > 0,
        )

        return IngressSecurityReport(
            is_blocked=False,
            block_reason=None,
            injection_result=highest_threat,
            pii_result=combined_pii_result,
            processed_messages=processed_messages,
        )