"""State schema for the 5-Agent Banking Swarm topology."""

from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage


class IncidentData(TypedDict, total=False):
    customer_id: str
    customer_name: str
    account_id: str
    card_last_four: str
    tx_id: str
    amount: float
    merchant: str
    location: str
    device: str
    upcoming_auto_debit: float
    auto_debit_loan_id: str


class SwarmDeliberationRecord(TypedDict, total=False):
    agent: str
    display_name: str
    role: str
    message: str
    rag_doc_consulted: str
    action_taken: str
    handoff_to: str


class SwarmState(TypedDict, total=False):
    """LangGraph Swarm State shared across all 5 banking agents."""
    messages: List[Any]
    active_agent: str
    incident: IncidentData
    swarm_history: List[SwarmDeliberationRecord]
    resolution_summary: Optional[str]
    is_resolved: bool

