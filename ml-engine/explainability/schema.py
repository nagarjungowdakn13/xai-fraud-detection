"""Explanation Payload Schema (Dataclass)"""
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ExplanationPayload:
    transaction_id: str
    timestamp: int
    risk_score: float
    shap_values: Any
    graph_context: Dict[str, Any]
    temporal_context: Dict[str, Any]
    rules_triggered: List[str]
    version: str
    hash: str
