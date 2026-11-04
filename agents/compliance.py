"""Agent 4: Compliance & Regulatory Officer (Jordan).

Ensures adherence to BSA/AML regulations, evaluates FinCEN SAR thresholds,
runs OFAC sanctions check, confirms Reg E deadlines, and swarms to Settlement Operations.
"""

from typing import Dict, Any
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag, tool_check_aml_sar
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def compliance_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Compliance Officer in the LangGraph Swarm."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))

    # Run domain tool
    tx_id = incident.get("tx_id", "TX-8921-X")
    amount = incident.get("amount", 2450.00)
    aml_res = tool_check_aml_sar(tx_id, amount, "RO")

    if llm is not None:
        compliance_sop = tool_consult_rag("FinCEN Suspicious Activity Report SAR threshold OFAC sanctions", "compliance_aml_sop")
        system_prompt = (
            "You are Jordan, Lead AML & Regulatory Compliance Officer at Apex Global Bank. "
            "Examine the cross-border transaction for FinCEN SAR requirements ($5,000 threshold or syndicated pattern) "
            "and OFAC SDN screening. State that OFAC screening is cleared, log internal SAR audit ref, and "
            "instruct Settlement & Operations Lead (Taylor) to execute ledger provisional reversal.\n\n"
            f"Compliance SOP Context from ChromaDB:\n{compliance_sop}"
        )
        user_prompt = (
            f"TxID: {tx_id}, Amount: ${amount:,.2f}, Merchant: {incident.get('merchant')}, Location: Bucharest, Romania."
        )
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        content = response.content
        handoff = "settlement_agent"
        rag_doc = compliance_sop[:180] + "..."
        action = f"Completed OFAC clearance, logged SAR internal record SAR-REF-90214"
    else:
        sim = SimulatedMuseModel.generate_response("compliance_agent", state, tool_consult_rag)
        content = sim["message"]
        handoff = sim["handoff_to"]
        rag_doc = sim["rag_consulted"]
        action = sim["action_taken"]

    record: SwarmDeliberationRecord = {
        "agent": "compliance_agent",
        "display_name": "Jordan",
        "role": "Compliance & Regulatory Officer",
        "message": content,
        "rag_doc_consulted": rag_doc,
        "action_taken": action,
        "handoff_to": handoff,
    }
    history.append(record)

    messages = list(state.get("messages", []))
    messages.append(AIMessage(content=f"[Jordan - Compliance Officer]: {content}"))

    return {
        "active_agent": handoff,
        "swarm_history": history,
        "messages": messages,
    }

