import re
from typing import List, Tuple
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import InjectionScanResult, ThreatLevel


class PromptInjectionScanner:
    """
    Scanner heuristique et structurel pour détecter les attaques de type Prompt Injection & Jailbreak.
    """

    # Signatures d'attaques directes et indirectes (OWASP LLM01)
    JAILBREAK_PATTERNS: List[Tuple[str, re.Pattern, float]] = [
        (
            "System Override / Ignore Instructions",
            re.compile(
                r"(ignore|disregard|forget|bypass|override)\s+(all\s+)?(previous|prior|above|system)\s+(instructions|rules|prompts|guidelines)",
                re.IGNORECASE,
            ),
            0.95,
        ),
        (
            "DAN / Jailbreak Persona",
            re.compile(
                r"(do\s+anything\s+now|DAN\s+mode|jailbreak|developer\s+mode\s+enabled|unfiltered\s+mode)",
                re.IGNORECASE,
            ),
            0.90,
        ),
        (
            "System Role Exploitation",
            re.compile(
                r"(you\s+are\s+now\s+a\s+system\s+administrator|switch\s+to\s+root\s+user|act\s+as\s+an\s+unrestricted\s+ai)",
                re.IGNORECASE,
            ),
            0.85,
        ),
        (
            "Prompt Leakage Attempt",
            re.compile(
                r"(reveal|print|output|display|show)\s+(your\s+)?(exact\s+)?(initial|original|system)\s+(prompt|instructions)",
                re.IGNORECASE,
            ),
            0.80,
        ),
        (
            "Special Control Delimiters Abuse",
            re.compile(
                r"(<\|im_start\|>|<\|im_end\|>|\[SYSTEM_PROMPT\]|```system)",
                re.IGNORECASE,
            ),
            0.90,
        ),
    ]

    def scan(self, text: str) -> InjectionScanResult:
        if not text or not text.strip():
            return InjectionScanResult(
                is_threat=False,
                threat_level=ThreatLevel.SAFE,
                detected_patterns=[],
                risk_score=0.0,
            )

        detected: List[str] = []
        max_score = 0.0

        for pattern_name, regex, weight in self.JAILBREAK_PATTERNS:
            if regex.search(text):
                detected.append(pattern_name)
                max_score = max(max_score, weight)

        if max_score >= 0.85:
            threat_level = ThreatLevel.CRITICAL
            is_threat = True
        elif max_score >= 0.50:
            threat_level = ThreatLevel.MEDIUM
            is_threat = True
        elif max_score > 0.0:
            threat_level = ThreatLevel.LOW
            is_threat = False
        else:
            threat_level = ThreatLevel.SAFE
            is_threat = False

        if is_threat:
            logger.warning(
                f"Security Alert: Prompt Injection détecté! Risk: {max_score:.2f} | Patterns: {detected}"
            )

        return InjectionScanResult(
            is_threat=is_threat,
            threat_level=threat_level,
            detected_patterns=detected,
            risk_score=max_score,
        )