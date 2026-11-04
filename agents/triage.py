"""Agent 1: Customer Account & Triage Specialist (Alex).

Acts as the front-line point of contact. Validates dispute under Regulation E,
consults ChromaDB for customer liability tiers, and swarms to Fraud Specialist.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def triage_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Triage Agent in the LangGraph Swarm."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))

    if llm is not None:
        # Live Meta Muse API execution
        policy_context = tool_consult_rag("Regulation E customer liability timeline", "dispute_policy")
        system_prompt = (
            "You are Alex, a Senior Customer Triage Specialist at Apex Global Bank. "
            "A customer reported an unauthorized transaction. Consult the provided Regulation E policy. "
            "Explain customer liability, acknowledge claim, and specify handoff to Fraud Specialist (Sam).\n\n"
            f"Policy Context from ChromaDB:\n{policy_context}"
        )
        user_prompt = (
            f"Customer: {incident.get('customer_name')}, Amount: ${incident.get('amount')}, "
            f"TxID: {incident.get('tx_id')}, Merchant: {incident.get('merchant')}."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        handoff = "fraud_agent"
        rag_doc = policy_context[:180] + "..."
        action = f"Initiated Reg E dispute file for {incident.get('tx_id')}"
    else:
        # Simulated Muse Model
        sim = SimulatedMuseModel.generate_response("triage_agent", state, tool_consult_rag)
        content = sim["message"]
        handoff = sim["handoff_to"]
        rag_doc = sim["rag_consulted"]
        action = sim["action_taken"]

    record: SwarmDeliberationRecord = {
        "agent": "triage_agent",
        "display_name": "Alex",
        "role": "Customer Triage Specialist",
        "message": content,
        "rag_doc_consulted": rag_doc,
        "action_taken": action,
        "handoff_to": handoff,
    }
    history.append(record)

    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=f"[Alex - Triage]: {content}"))

    return {
        "active_agent": handoff,
        "swarm_history": history,
        "messages": messages,
    }

