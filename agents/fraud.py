"""Agent 2: Fraud & Security Specialist (Sam) with Human-in-the-Loop (HITL) gate.

Analyzes geo-velocity anomaly, pauses for real-time customer verification via LangGraph interrupt(),
and dynamically branches based on customer confirmation (Confirmed Fraud vs Legitimate Travel).
"""

from typing import Dict, Any
from langgraph.types import interrupt
from agents.state import SwarmState, SwarmDeliberationRecord
from agents.tools import tool_consult_rag, tool_freeze_card, tool_log_travel_exception
from swarm.model_client import get_meta_muse_llm, SimulatedMuseModel
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage


def fraud_agent_node(state: SwarmState) -> Dict[str, Any]:
    """Node function for Fraud Specialist in the LangGraph Swarm with HITL."""
    llm = get_meta_muse_llm()
    incident = state.get("incident", {})
    history = list(state.get("swarm_history", []))
    customer_status = state.get("customer_verification_status")

    card_last_four = incident.get("card_last_four", "4102")
    customer_id = incident.get("customer_id", "CUST-4401")
    tx_id = incident.get("tx_id", "TX-8921-X")
    amount = incident.get("amount", 2450.00)
    merchant = incident.get("merchant", "Luxury European Watches Ltd")
    location = incident.get("location", "Bucharest, Romania")

    # --- HUMAN-IN-THE-LOOP (HITL) GATE ---
    if not customer_status:
        # Pause execution and request human verification
        verification_request = {
            "type": "HUMAN_VERIFICATION_REQUIRED",
            "title": "🚨 URGENT FRAUD SECURITY VERIFICATION",
            "customer_id": customer_id,
            "tx_id": tx_id,
            "amount": amount,
            "merchant": merchant,
            "location": location,
            "question": f"Did you authorize this ${amount:,.2f} purchase at {merchant} in {location}?",
            "choices": {
                "CONFIRM_FRAUD": "1. NO - I did not authorize this! (Lock card & dispute charges)",
                "LEGITIMATE": "2. YES - I authorized this purchase while traveling! (Approve & keep card active)"
            }
        }
        human_answer = interrupt(verification_request)
        customer_status = str(human_answer).strip().upper()

    # Determine if user confirmed fraud or approved as legitimate
    is_legitimate = customer_status in ["LEGITIMATE", "LEGITIMATE_PURCHASE", "2", "YES", "APPROVE", "TRUE"]
    
    if is_legitimate:
        # Branch B: Legitimate Purchase (False Alarm Resolution)
        travel_res = tool_log_travel_exception(customer_id, country="RO", days=7)
        rag_doc = "SOP: Customer-authorized travel exception noted in fraud monitoring registry."
        action = f"Logged 7-day travel note for Romania. Card {card_last_four} kept ACTIVE. Recalibrated risk to LOW."
        handoff = "triage_agent"
        content = (
            f"Fraud Specialist (Sam): Customer confirmed authorization for ${amount:,.2f} at {merchant}. "
            f"This is a verified legitimate transaction. I have logged a 7-day travel exception for Romania, "
            f"cleared the geo-velocity security flag, and ensured card ending {card_last_four} remains active without interruption. "
            f"Handing off to Triage Specialist (Alex) to confirm closure with customer."
        )
        is_false_alarm = True
        verification_label = "LEGITIMATE_PURCHASE"

    else:
        # Branch A: Confirmed Unauthorized Fraud
        freeze_res = tool_freeze_card(card_last_four, "Customer confirmed unauthorized fraud via HITL gate")
        rag_doc = tool_consult_rag("geo-velocity anomaly containment composite risk score", "fraud_security_sop")
        action = f"HARD_FREEZE placed on card {card_last_four}, revoked active OAuth mobile sessions"
        handoff = "credit_agent"
        content = (
            f"Fraud Specialist (Sam): Customer explicitly confirmed via real-time verification that ${amount:,.2f} "
            f"charge at {merchant} is UNAUTHORIZED FRAUD. "
            f"Immediate Containment Executed: Applied HARD_FREEZE on card {card_last_four} and revoked all active OAuth mobile sessions. "
            f"Swarming to Loan & Credit Underwriter (Morgan) to safeguard pending auto-debit and shield credit rating."
        )
        is_false_alarm = False
        verification_label = "CONFIRMED_FRAUD"

    record: SwarmDeliberationRecord = {
        "agent": "fraud_agent",
        "display_name": "Sam",
        "role": "Fraud & Security Specialist",
        "message": content,
        "rag_doc_consulted": rag_doc[:180] + "...",
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
        "customer_verification_status": verification_label,
        "is_false_alarm": is_false_alarm,
    }
