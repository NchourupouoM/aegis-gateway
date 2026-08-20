from typing import Dict, List, Optional
from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import PIIMapping, PIIMaskingResult


class PIIAnonymizer:
    """Moteur d'anonymisation et de pseudonymisation réversible basé sur Microsoft Presidio."""

    def __init__(
        self,
        entities: Optional[List[str]] = None,
        spacy_model: str = "en_core_web_sm",
    ):
        # Configuration déterministe du moteur NLP pour cibler le modèle spaCy installé
        nlp_configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": spacy_model}],
        }
        provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
        nlp_engine = provider.create_engine()

        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()

        # Entités cibles par défaut
        self.entities = entities or [
            "EMAIL_ADDRESS",
            "CREDIT_CARD",
            "PHONE_NUMBER",
            "IBAN_CODE",
            "PERSON",
            "US_SSN",
            "IP_ADDRESS",
        ]

    def mask_text(self, text: str) -> PIIMaskingResult:
        """Analyse le texte, remplace les PII par des placeholders réversibles et renvoie le mapping."""
        if not text or not text.strip():
            return PIIMaskingResult(
                sanitized_text=text, anonymized_entities=[], has_pii=False
            )

        # 1. Détection des entités
        results = self.analyzer.analyze(
            text=text,
            entities=self.entities,
            language="en",
        )

        if not results:
            return PIIMaskingResult(
                sanitized_text=text, anonymized_entities=[], has_pii=False
            )

        # 2. Construction de la configuration de remplacement avec indexation
        entity_counters: Dict[str, int] = {}
        anonymized_entities: List[PIIMapping] = []

        # Tri des résultats par position de départ
        sorted_results = sorted(results, key=lambda x: x.start)

        operators = {}
        for res in sorted_results:
            entity_type = res.entity_type
            entity_counters[entity_type] = entity_counters.get(entity_type, 0) + 1
            placeholder = f"<{entity_type}_{entity_counters[entity_type]}>"

            original_value = text[res.start : res.end]
            anonymized_entities.append(
                PIIMapping(
                    placeholder=placeholder,
                    original_value=original_value,
                    entity_type=entity_type,
                )
            )

            # Remplacement avec placeholder déterministe
            operators[entity_type] = OperatorConfig(
                "replace", {"new_value": placeholder}
            )

        # 3. Anonymisation
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=results,
            operators=operators,
        )

        logger.debug(
            f"🔒 PII Masking: {len(anonymized_entities)} entité(s) masquée(s) sur le texte."
        )

        return PIIMaskingResult(
            sanitized_text=anonymized_result.text,
            anonymized_entities=anonymized_entities,
            has_pii=True,
        )