from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

Category = Literal["BILLING", "ACCOUNT_ACCESS", "BUG_REPORT", "FEATURE_REQUEST", "SECURITY", "OTHER"]
Priority = Literal["P0", "P1", "P2", "P3"]
Sentiment = Literal["NEGATIVE", "NEUTRAL", "POSITIVE"]

Route = Literal["AUTO_REPLY", "NEEDS_INFO", "ESCALATE_BILLING", "ESCALATE_TECH", "ESCALATE_SECURITY"]

class TriageResult(BaseModel):
    category: Category
    priority: Priority
    sentiment: Sentiment
    confidence: float = Field(ge=0.0, le=1.0)
    missing_info: List[str] = Field(default_factory=list)
    reason: str

class RetrievedChunk(BaseModel):
    source: str
    chunk_id: str
    text: str

class AgentResponse(BaseModel):
    triage: TriageResult
    route: Route
    answer: str
    citations: List[Dict[str, str]] = Field(default_factory=list)
    retrieved: List[RetrievedChunk] = Field(default_factory=list)
    debug: Optional[Dict[str, Any]] = None
