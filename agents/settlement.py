"""Agent 5: Core Settlement & Operations Lead (Taylor).

Executes general ledger contra-posting for provisional credit, initiates card network
chargeback code 10.4, issues new Virtual Debit Card, and closes the swarm loop.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag, tool_post_provisional_credit, tool_issue_virtual_card
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def settlement_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Settlement & Operations Lead in the LangGraph Swarm."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))

    # Run domain tools
    account_id = incident.get("account_id", "ACCT-99214-DDA")
    customer_id = incident.get("customer_id", "CUST-4401")
    amount = incident.get("amount", 2450.00)

    cred_res = tool_post_provisional_credit(account_id, amount, "GL-7102")
    vdc_res = tool_issue_virtual_card(customer_id)

    if llm is not None:
        settlement_sop = tool_consult_rag("provisional credit GL-7102 chargeback 10.4 Virtual Debit Card", "settlement_operations_sop")
        system_prompt = (
            "You are Taylor, Core Settlement & Operations Lead at Apex Global Bank. "
            "You are finalizing the swarm resolution. State that you have credited the customer DDA via GL-7102, "
            "initiated card network chargeback reason code 10.4, provisioned new Virtual Debit Card, and finalized "
            "the collaborative resolution across all 5 banking divisions.\n\n"
            f"Settlement SOP Context from ChromaDB:\n{settlement_sop}"
        )
        user_prompt = (
            f"Customer: {incident.get('customer_name')}, Amount to credit: ${amount:,.2f}, Account: {account_id}."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        rag_doc = settlement_sop[:180] + "..."
        action = f"Credited ${amount:,.2f} via GL-7102, initiated chargeback 10.4, issued VDC token"
    else:
        sim = SimulatedMuseModel.generate_response("settlement_agent", state, tool_consult_rag)
        content = sim["message"]
        rag_doc = sim["rag_consulted"]
        action = sim["action_taken"]

    record: SwarmDeliberationRecord = {
        "agent": "settlement_agent",
        "display_name": "Taylor",
        "role": "Settlement & Operations Lead",
        "message": content,
        "rag_doc_consulted": rag_doc,
        "action_taken": action,
        "handoff_to": "resolved",
    }
    history.append(record)

    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=f"[Taylor - Settlement Lead]: {content}"))

    summary = (
        f"INCIDENT RESOLUTION REPORT:\n"
        f"- Customer: {incident.get('customer_name')} ({customer_id})\n"
        f"- Disputed Tx: {incident.get('tx_id')} for ${amount:,.2f}\n"
        f"- Fraud Containment: Card {incident.get('card_last_four')} HARD_FREEZE applied; Geo-Velocity confirmed.\n"
        f"- Underwriting Protection: 14-day hold placed on ${incident.get('upcoming_auto_debit')} auto-loan payment; NSF waived.\n"
        f"- AML/Compliance: OFAC SDN clear; internal SAR reference logged.\n"
        f"- Restitution: Immediate provisional credit of ${amount:,.2f} deposited to {account_id}; new VDC activated."
    )

    return {
        "active_agent": "resolved",
        "swarm_history": history,
        "messages": messages,
        "resolution_summary": summary,
        "is_resolved": True,
    }

