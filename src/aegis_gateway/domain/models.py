from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage] = Field(..., min_length=1)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=1024, gt=0)
    stream: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ThreatLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    CRITICAL = "critical"


class InjectionScanResult(BaseModel):
    is_threat: bool
    threat_level: ThreatLevel
    detected_patterns: List[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class PIIMapping(BaseModel):
    placeholder: str  # ex: <EMAIL_1>
    original_value: str  # ex: jean.dupont@email.com
    entity_type: str  # ex: EMAIL_ADDRESS


class PIIMaskingResult(BaseModel):
    sanitized_text: str
    anonymized_entities: List[PIIMapping] = Field(default_factory=list)
    has_pii: bool = False


class IngressSecurityReport(BaseModel):
    is_blocked: bool
    block_reason: Optional[str] = None
    injection_result: InjectionScanResult
    pii_result: PIIMaskingResult
    processed_messages: List[ChatMessage]

# Modèles FinOps & Smart Routing
class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"


class ModelTier(str, Enum):
    FAST = "fast"  # Ex: Gemini 2.0 Flash / GPT-4o-mini
    DEEP_REASONING = "deep_reasoning"  # Ex: GPT-4o
    AUTO = "auto"  # Décision par le Smart Router


class RoutingDecision(BaseModel):
    selected_provider: LLMProvider
    selected_model: str
    fallback_provider: LLMProvider
    fallback_model: str
    estimated_input_tokens: int
    complexity_score: float = Field(..., ge=0.0, le=1.0)
    routing_reason: str
    tier: ModelTier
    estimated_input_cost_usd: float
    baseline_cost_usd: float  # Coût si la requête avait été traitée par GPT-4o
    estimated_savings_usd: float  # baseline_cost_usd - estimated_input_cost_usd