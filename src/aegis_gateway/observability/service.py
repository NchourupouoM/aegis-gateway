from typing import Any, Dict
from sqlalchemy import func, select, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from aegis_gateway.domain.models import GatewayResponse, IngressSecurityReport, RoutingDecision
from aegis_gateway.observability.models import TransactionAuditLog


class FinOpsAnalyticsService:
    """Service de reporting analytique et de persistance des transactions."""

    @staticmethod
    async def record_transaction(
        session: AsyncSession,
        ingress_report: IngressSecurityReport,
        decision: RoutingDecision | None,
        gateway_response: GatewayResponse | None,
    ) -> TransactionAuditLog:
        """Persiste une transaction de manière asynchrone dans la base d'audit."""
        if ingress_report.is_blocked:
            log_entry = TransactionAuditLog(
                provider="BLOCKED",
                model="BLOCKED",
                tier="SECURITY_REJECT",
                input_tokens=0,
                output_tokens=0,
                total_tokens=0,
                cost_usd=0.0,
                baseline_cost_usd=0.0,
                savings_usd=0.0,
                latency_ms=0.0,
                is_fallback=False,
                has_pii=False,
                pii_entities_count=0,
                is_blocked=True,
                block_reason=ingress_report.block_reason,
            )
        else:
            assert gateway_response is not None
            assert decision is not None
            log_entry = TransactionAuditLog(
                provider=gateway_response.provider.value,
                model=gateway_response.model,
                tier=decision.tier.value,
                input_tokens=gateway_response.input_tokens,
                output_tokens=gateway_response.output_tokens,
                total_tokens=gateway_response.total_tokens,
                cost_usd=gateway_response.cost_usd,
                baseline_cost_usd=gateway_response.baseline_cost_usd,
                savings_usd=gateway_response.savings_usd,
                latency_ms=gateway_response.latency_ms,
                is_fallback=gateway_response.is_fallback,
                fallback_reason=gateway_response.fallback_reason,
                has_pii=gateway_response.pii_anonymized,
                pii_entities_count=gateway_response.egress_security.demasked_entities_count,
                is_blocked=not gateway_response.egress_security.is_safe,
                block_reason=gateway_response.egress_security.violation_reason,
            )

        session.add(log_entry)
        await session.commit()
        await session.refresh(log_entry)
        return log_entry

    @staticmethod
    async def get_metrics_summary(session: AsyncSession) -> Dict[str, Any]:
        """Calcule les agrégats de performance, de sécurité et d'économies FinOps."""
        stmt = select(
            func.count(TransactionAuditLog.id).label("total_requests"),
            func.coalesce(func.sum(TransactionAuditLog.cost_usd), 0.0).label("total_cost"),
            func.coalesce(func.sum(TransactionAuditLog.baseline_cost_usd), 0.0).label("baseline_cost"),
            func.coalesce(func.sum(TransactionAuditLog.savings_usd), 0.0).label("total_savings"),
            func.coalesce(func.avg(TransactionAuditLog.latency_ms), 0.0).label("avg_latency"),
            func.coalesce(func.sum(TransactionAuditLog.total_tokens), 0).label("total_tokens"),
            func.coalesce(
                func.sum(func.cast(TransactionAuditLog.is_fallback, Integer)), 0
            ).label("fallback_count"),
            func.coalesce(
                func.sum(func.cast(TransactionAuditLog.is_blocked, Integer)), 0
            ).label("blocked_count"),
            func.coalesce(
                func.sum(func.cast(TransactionAuditLog.has_pii, Integer)), 0
            ).label("pii_sanitized_count"),
        )

        result = await session.execute(stmt)
        row = result.mappings().one()

        savings_pct = 0.0
        if row["baseline_cost"] > 0:
            savings_pct = (row["total_savings"] / row["baseline_cost"]) * 100.0

        return {
            "total_requests": row["total_requests"],
            "total_cost_usd": round(row["total_cost"], 6),
            "baseline_cost_usd": round(row["baseline_cost"], 6),
            "total_savings_usd": round(row["total_savings"], 6),
            "savings_percentage": round(savings_pct, 2),
            "avg_latency_ms": round(row["avg_latency"], 2),
            "total_tokens_processed": row["total_tokens"],
            "fallbacks_triggered": row["fallback_count"],
            "threats_blocked": row["blocked_count"],
            "pii_requests_anonymized": row["pii_sanitized_count"],
        }