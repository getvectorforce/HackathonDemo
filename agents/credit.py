"""Agent 3: Loan & Credit Underwriter (Morgan).

Evaluates credit impact of depleted balance, queries ChromaDB for payment protection SOP,
applies auto-debit grace period, waives NSF fees, and hands off to Compliance.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag, tool_protect_loan_debit
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def credit_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Credit & Dispute Underwriter in the LangGraph Swarm."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))

    # Run domain tool
    customer_id = incident.get("customer_id", "CUST-4401")
    loan_id = incident.get("auto_debit_loan_id", "LN-AUTO-9102")
    auto_debit = incident.get("upcoming_auto_debit", 450.00)
    protect_res = tool_protect_loan_debit(customer_id, loan_id, auto_debit, hold_days=14)

    if llm is not None:
        credit_sop = tool_consult_rag("auto-debit grace period overdraft forgiveness FCRA dispute", "credit_underwriting_policy")
        system_prompt = (
            "You are Morgan, Senior Loan & Credit Underwriter at Apex Global Bank. "
            "The customer's account balance has been drained by fraud, risking a bounce on an upcoming auto loan debit. "
            "Consult the Credit & Underwriting Policy from ChromaDB. "
            "Explain that you have placed a 14-day hold on the auto-debit, waived NSF fees, attached FCRA dispute suppression, "
            "and are swarming to Compliance Officer (Jordan).\n\n"
            f"Underwriting Policy Context from ChromaDB:\n{credit_sop}"
        )
        user_prompt = (
            f"Customer: {incident.get('customer_name')}, Upcoming Auto-Debit: ${auto_debit:,.2f}, Loan ID: {loan_id}."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        handoff = "compliance_agent"
        rag_doc = credit_sop[:180] + "..."
        action = f"Applied 14-day grace hold on auto-loan debit ${auto_debit}, waived NSF fees, set FCRA flag"
    else:
        sim = SimulatedMuseModel.generate_response("credit_agent", state, tool_consult_rag)
        content = sim["message"]
        handoff = sim["handoff_to"]
        rag_doc = sim["rag_consulted"]
        action = sim["action_taken"]

    record: SwarmDeliberationRecord = {
        "agent": "credit_agent",
        "display_name": "Morgan",
        "role": "Loan & Credit Underwriter",
        "message": content,
        "rag_doc_consulted": rag_doc,
        "action_taken": action,
        "handoff_to": handoff,
    }
    history.append(record)

    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=f"[Morgan - Credit Underwriter]: {content}"))

    return {
        "active_agent": handoff,
        "swarm_history": history,
        "messages": messages,
    }

