from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from aegis_gateway.domain.models import ChatRequest, GatewayResponse
from aegis_gateway.egress.pipeline import EgressPipeline
from aegis_gateway.firewall.ingress_pipeline import IngressFirewall
from aegis_gateway.observability.database import get_db_session
from aegis_gateway.observability.service import FinOpsAnalyticsService
from aegis_gateway.providers.dispatcher import ResilientDispatcher
from aegis_gateway.router.smart_router import SmartRouter

router = APIRouter(prefix="/v1", tags=["LLM Gateway"])

# Singletons de traitement
ingress_firewall = IngressFirewall()
smart_router = SmartRouter()
resilient_dispatcher = ResilientDispatcher()
egress_pipeline = EgressPipeline()


@router.post(
    "/chat/completions",
    response_model=GatewayResponse,
    status_code=status.HTTP_200_OK,
)
async def chat_completions(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db_session),
) -> GatewayResponse:
    """Endpoint central de la passerelle : Sécurité Ingress ➔ Routage ➔ LLM ➔ Egress ➔ Audit FinOps."""

    # 1. Ingress Security & PII Masking
    ingress_report = ingress_firewall.process(request)

    if ingress_report.is_blocked:
        # Enregistrer l'incident de sécurité en DB
        await FinOpsAnalyticsService.record_transaction(
            session=db,
            ingress_report=ingress_report,
            decision=None,
            gateway_response=None,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ingress_report.block_reason,
        )

    # 2. Smart Cost & Complexity Routing
    decision = smart_router.route(
        messages=ingress_report.processed_messages,
        original_request=request,
    )

    # 3. Exécution Résiliente avec Auto-Fallback
    llm_response = await resilient_dispatcher.dispatch(
        messages=ingress_report.processed_messages,
        request=request,
        decision=decision,
    )

    # 4. Egress Guardrails & Restauration PII
    gateway_response = egress_pipeline.process(
        llm_response=llm_response,
        pii_mappings=ingress_report.pii_result.anonymized_entities,
    )

    # 5. Persistance Audit & FinOps non-bloquante
    await FinOpsAnalyticsService.record_transaction(
        session=db,
        ingress_report=ingress_report,
        decision=decision,
        gateway_response=gateway_response,
    )

    return gateway_response