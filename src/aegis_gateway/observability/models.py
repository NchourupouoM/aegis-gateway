import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String
from aegis_gateway.observability.database import Base


class TransactionAuditLog(Base):
    """Enregistrement d'audit et de comptabilité FinOps pour chaque requête."""

    __tablename__ = "transaction_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    # Provider & Modèle
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    tier = Column(String(50), nullable=False)

    # Tokens & FinOps ($)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    baseline_cost_usd = Column(Float, default=0.0)
    savings_usd = Column(Float, default=0.0)

    # Performance & Résilience
    latency_ms = Column(Float, default=0.0)
    is_fallback = Column(Boolean, default=False)
    fallback_reason = Column(String(255), nullable=True)

    # Sécurité & Conformité
    has_pii = Column(Boolean, default=False)
    pii_entities_count = Column(Integer, default=0)
    is_blocked = Column(Boolean, default=False)
    block_reason = Column(String(255), nullable=True)