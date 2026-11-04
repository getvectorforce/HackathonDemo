"""Meta Developer Muse API client with OpenAI compatibility and fallback simulation.

Connects to Meta Model API (api.meta.ai/v1) for the Muse model family (muse-spark, muse-wonder).
Supports tool calling and fallback simulation for demonstration without live credentials.
"""

import json
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage, AIMessage
from config import META_API_KEY, META_API_BASE, META_MODEL, SIMULATION_MODE


def get_meta_muse_llm(temperature: float = 0.2):
    """Returns a LangChain ChatOpenAI instance configured for Meta Developer Muse API."""
    if not SIMULATION_MODE and META_API_KEY:
        return ChatOpenAI(
            model=META_MODEL,
            base_url=META_API_BASE,
            api_key=META_API_KEY,
            temperature=temperature,
        )
    return None


class SimulatedMuseModel:
    """Smart simulation engine providing banking-aware deliberations when API key is not present.

    Simulates Meta Muse reasoning for each of the 5 banking agents in the swarm topology.
    """

    @staticmethod
    def generate_response(agent_name: str, state: Dict[str, Any], query_tool_func) -> Dict[str, Any]:
        incident = state.get("incident", {})
        customer_name = incident.get("customer_name", "Alex Mercer")
        amount = incident.get("amount", 2450.00)
        tx_id = incident.get("tx_id", "TX-8921-X")
        auto_debit = incident.get("upcoming_auto_debit", 450.00)

        if agent_name == "triage_agent":
            # Triage retrieves dispute policy and hands off to Fraud
            rag_info = query_tool_func("unauthorized transaction customer liability Regulation E", "dispute_policy")
            msg = (
                f"Hello {customer_name}. I have acknowledged your urgent report regarding the unrecognized "
                f"${amount:,.2f} transaction (ID: {tx_id}). Under our Regulation E dispute policy, "
                f"immediate notice limits your liability to $50. Because this involves an unrecognized foreign terminal, "
                f"I am immediately swarming with our Fraud Specialist (Sam) to isolate the card and assess device risk."
            )
            return {
                "message": msg,
                "handoff_to": "fraud_agent",
                "action_taken": "Acknowledged claim, initiated Reg E file, swarmed to Fraud Specialist",
                "rag_consulted": rag_info[:180] + "..."
            }

        elif agent_name == "fraud_agent":
            # Fraud retrieves security SOP, freezes card, sets risk score, hands off to Underwriter
            rag_info = query_tool_func("geo-velocity impossible travel containment hard freeze", "fraud_security_sop")
            msg = (
                f"Fraud Specialist (Sam) stepping in. I've analyzed transaction {tx_id}. "
                f"Triggered Rule: Impossible Travel Geo-Velocity (login from New York, POS swipe in Bucharest within 42 minutes). "
                f"Composite Risk Score: 88/100 (HIGH). "
                f"Actions taken: Executed HARD_FREEZE on Debit Card ending in 4102 and revoked all active OAuth mobile sessions. "
                f"Swarming to Loan & Credit Underwriter (Morgan) to shield customer's standing loans and pending auto-debit."
            )
            return {
                "message": msg,
                "handoff_to": "credit_agent",
                "action_taken": "Applied HARD_FREEZE on card 4102, revoked tokens, flagged Geo-Velocity anomaly",
                "rag_consulted": rag_info[:180] + "..."
            }

        elif agent_name == "credit_agent":
            # Credit underwriter checks loan protection SOP, freezes auto-debit penalty, passes to compliance
            rag_info = query_tool_func("loan auto-debit overdraft forgiveness bridge credit", "credit_underwriting_policy")
            msg = (
                f"Loan & Credit Underwriter (Morgan) here. Reviewing customer profile: {customer_name} has a scheduled "
                f"auto-loan debit of ${auto_debit:,.2f} due in 3 days. Due to the fraudulent debit of ${amount:,.2f}, "
                f"the account is at risk of overdraft and NSF bounce. "
                f"Underwriting Actions: Placed a 14-day hold on the ${auto_debit:,.2f} auto-debit, waived all prospective "
                f"NSF/overdraft charges, and attached FCRA non-derogatory dispute flag. "
                f"Swarming to Compliance & Regulatory Officer (Jordan) for AML/SAR threshold evaluation."
            )
            return {
                "message": msg,
                "handoff_to": "compliance_agent",
                "action_taken": "Applied 14-day loan auto-debit hold, waived NSF fees, added FCRA protection flag",
                "rag_consulted": rag_info[:180] + "..."
            }

        elif agent_name == "compliance_agent":
            # Compliance checks AML/OFAC SOP, evaluates SAR triggers, hands off to settlement operations
            rag_info = query_tool_func("Suspicious Activity Report SAR threshold OFAC sanctions", "compliance_aml_sop")
            msg = (
                f"Compliance Officer (Jordan) here. Investigating regulatory obligations for ${amount:,.2f} cross-border breach. "
                f"1. FinCEN SAR Analysis: Transaction is below the standalone $5,000 threshold for single-actor unauthorized POS, "
                f"but matches syndicated credential-stuffing patterns; filed Internal Incident SAR-Log #2026-B99. "
                f"2. OFAC SDN Sanction Screening: Cleared (merchant terminal destination not listed on sanctions registry). "
                f"3. Regulatory Deadlines: Provisional credit must post within 10 business days per Reg E. "
                f"Swarming to Settlement & Operations Lead (Taylor) for ledger reversal and credential reissue."
            )
            return {
                "message": msg,
                "handoff_to": "settlement_agent",
                "action_taken": "Cleared OFAC screening, logged internal SAR dossier, validated 10-day Reg E deadline",
                "rag_consulted": rag_info[:180] + "..."
            }

        elif agent_name == "settlement_agent":
            # Settlement executes reversal, issues virtual card, synthesizes swarm resolution
            rag_info = query_tool_func("provisional credit ledger reversal chargeback code VDC", "settlement_operations_sop")
            msg = (
                f"Settlement & Operations Lead (Taylor) concluding swarm actions. "
                f"Operations Execution: "
                f"1. Posted immediate provisional credit of ${amount:,.2f} to DDA via GL-7102 Disputed Clearing. "
                f"2. Initiated Visa/Mastercard dispute reason code 10.4 (Card-Absent Fraudulent Dispute). "
                f"3. Provisioned Instant Virtual Debit Card (VDC-8840) to customer's mobile wallet. "
                f"4. Coordinated with Credit Underwriting to safeguard loan debit. Incident resolved across all 5 banking divisions."
            )
            return {
                "message": msg,
                "handoff_to": "resolved",
                "action_taken": "Issued provisional credit $2,450.00, initiated chargeback code 10.4, provisioned new VDC",
                "rag_consulted": rag_info[:180] + "..."
            }

        return {
            "message": "Swarm state updated.",
            "handoff_to": "resolved",
            "action_taken": "None",
            "rag_consulted": "None"
        }

