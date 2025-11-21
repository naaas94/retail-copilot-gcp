from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class Intent(BaseModel):
    id: str
    description: str
    measures: List[str]
    dimensions: List[str]

class Plan(BaseModel):
    intent_id: str
    tables: List[str]
    measures: List[Dict[str, str]]
    dimensions: List[Dict[str, str]]
    filters: List[Dict[str, str]]
    limits: Dict[str, int]
    viz_hint: Optional[Dict[str, Any]] = None
    needs_disambiguation: bool = False
    clarification_question: Optional[str] = None

class RouterOutput(BaseModel):
    route: Literal["qa", "sql", "unsafe", "handoff", "clarify"]
    reason: str
    clarify_question: Optional[str] = None

class Trace(BaseModel):
    user_query: str
    route: str
    plan: Optional[Plan] = None
    sql: Optional[str] = None
    latency_ms: float
    cost_estimate_usd: float
    error: Optional[str] = None
