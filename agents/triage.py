"""Agent 1: Customer Account & Triage Specialist (Alex).

Acts as the front-line point of contact. Validates dispute under Regulation E,
consults ChromaDB for customer liability tiers, and swarms to Fraud Specialist.
Also handles final customer confirmation for verified legitimate travel false-alarms.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def triage_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Triage Agent in the LangGraph Swarm."""
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))
    customer_name = incident.get("customer_name", "Alex Mercer")
    amount = incident.get("amount", 2450.00)
    tx_id = incident.get("tx_id", "TX-8921-X")
    merchant = incident.get("merchant", "Luxury European Watches Ltd")
    auto_debit = incident.get("upcoming_auto_debit", 450.00)

    # Check if this is a return loop for a verified false-alarm
    if state.get("is_false_alarm"):
        content = (
            f"Customer Triage (Alex): Thank you for verifying your travel authorization, {customer_name}! "
            f"Your ${amount:,.2f} purchase at {merchant} has been cleared. "
            f"Your card remains fully active, and our security switch has logged a 7-day travel exception note. "
            f"Your scheduled auto-loan debit of ${auto_debit:,.2f} will process normally with zero fee impact. "
            f"Case successfully closed as customer-verified legitimate travel."
        )
        handoff = "resolved"
        rag_doc = "SOP: Customer account status active; travel whitelist applied."
        action = "Closed false-alarm case; notified customer of approved status"

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

        summary = (
            f"FALSE-ALARM RESOLUTION REPORT:\n"
            f"- Customer: {customer_name} ({incident.get('customer_id')})\n"
            f"- Transaction: {tx_id} for ${amount:,.2f} at {merchant}\n"
            f"- HITL Verification: Customer confirmed legitimate authorized travel.\n"
            f"- Action: Card kept active; 7-day travel note registered; no chargeback or ledger credit necessary.\n"
            f"- Loans & Debits: Upcoming ${auto_debit:,.2f} auto-debit unaffected."
        )

        return {
            "active_agent": "resolved",
            "swarm_history": history,
            "messages": messages,
            "resolution_summary": summary,
            "is_resolved": True,
        }

    # Initial frontline intake
    llm = get_meta_muse_llm()
    if llm is not None:
        policy_context = tool_consult_rag("Regulation E customer liability timeline", "dispute_policy")
        system_prompt = (
            "You are Alex, a Senior Customer Triage Specialist at Apex Global Bank. "
            "A customer reported an unauthorized transaction. Consult the provided Regulation E policy. "
            "Explain customer liability, acknowledge claim, and specify handoff to Fraud Specialist (Sam).\n\n"
            f"Policy Context from ChromaDB:\n{policy_context}"
        )
        user_prompt = (
            f"Customer: {customer_name}, Amount: ${amount:,.2f}, "
            f"TxID: {tx_id}, Merchant: {merchant}."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        handoff = "fraud_agent"
        rag_doc = policy_context[:180] + "..."
        action = f"Initiated Reg E dispute file for {tx_id}"
    else:
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
