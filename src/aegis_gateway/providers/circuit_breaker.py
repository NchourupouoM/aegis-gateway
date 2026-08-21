import time
from aegis_gateway.core.logger import logger
from aegis_gateway.domain.models import CircuitState, LLMProvider


class CircuitBreaker:
    """Gestionnaire d'état Circuit Breaker par fournisseur pour éviter la cascade de pannes."""

    def __init__(
        self,
        provider: LLMProvider,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 30.0,
    ):
        self.provider = provider
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec

        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = time.time()

    def allow_request(self) -> bool:
        """Vérifie si le circuit permet l'envoi d'une requête vers ce provider."""
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            # Vérifier si le délai de récupération est écoulé -> passage en HALF_OPEN
            if current_time - self.last_state_change >= self.recovery_timeout_sec:
                logger.info(
                    f"Circuit Breaker [{self.provider.value}] transition OPEN ➔ HALF_OPEN (Test de sonde)"
                )
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = current_time
                return True
            return False

        return True

    def record_success(self):
        """Réinitialise le compteur d'échecs après un appel réussi."""
        if self.state != CircuitState.CLOSED:
            logger.info(
                f"Circuit Breaker [{self.provider.value}] rétabli : passage à CLOSED"
            )
        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_state_change = time.time()

    def record_failure(self):
        """Incrémente les échecs et ouvre le circuit si le seuil est dépassé."""
        self.consecutive_failures += 1
        current_time = time.time()

        if (
            self.consecutive_failures >= self.failure_threshold
            and self.state != CircuitState.OPEN
        ):
            self.state = CircuitState.OPEN
            self.last_state_change = current_time
            logger.error(
                f"🔴 Circuit Breaker [{self.provider.value}] OUVERT ! ({self.consecutive_failures} échecs consécutifs). "
                f"Toutes les requêtes basculeront automatiquement sur le Fallback pendant {self.recovery_timeout_sec}s."
            )