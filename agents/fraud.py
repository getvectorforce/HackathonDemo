"""Agent 2: Fraud & Security Specialist (Sam).

Analyzes geo-velocity anomaly, queries ChromaDB for fraud containment SOPs,
executes HARD_FREEZE on compromised card, and hands off to Underwriting.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag, tool_freeze_card
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def fraud_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Fraud Specialist in the LangGraph Swarm."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))

    # Run domain tool
    card_last_four = incident.get("card_last_four", "4102")
    freeze_res = tool_freeze_card(card_last_four, "Geo-velocity breach & unconfirmed foreign POS swipe")

    if llm is not None:
        sop_context = tool_consult_rag("geo-velocity anomaly containment composite risk score", "fraud_security_sop")
        system_prompt = (
            "You are Sam, Lead Fraud & Security Specialist at Apex Global Bank. "
            "You must review the geo-velocity anomaly, report your risk assessment (Composite Risk Score: 88/100), "
            "confirm you have executed HARD_FREEZE on the card, and hand off to Loan & Credit Underwriter (Morgan).\n\n"
            f"Fraud SOP Context from ChromaDB:\n{sop_context}"
        )
        user_prompt = (
            f"Anomaly: Impossible travel detected for card {card_last_four}. "
            f"Tx Amount: ${incident.get('amount')}, Location: {incident.get('location')}."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        handoff = "credit_agent"
        rag_doc = sop_context[:180] + "..."
        action = f"Applied HARD_FREEZE on card ending {card_last_four}, revoked mobile OAuth tokens"
    else:
        sim = SimulatedMuseModel.generate_response("fraud_agent", state, tool_consult_rag)
        content = sim["message"]
        handoff = sim["handoff_to"]
        rag_doc = sim["rag_consulted"]
        action = sim["action_taken"]

    record: SwarmDeliberationRecord = {
        "agent": "fraud_agent",
        "display_name": "Sam",
        "role": "Fraud & Security Specialist",
        "message": content,
        "rag_doc_consulted": rag_doc,
        "action_taken": action,
        "handoff_to": handoff,
    }
    history.append(record)

    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=f"[Sam - Fraud Specialist]: {content}"))

    return {
        "active_agent": handoff,
        "swarm_history": history,
        "messages": messages,
    }

