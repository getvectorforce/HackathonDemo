"""LangGraph Swarm Topology for 5 Banking Agents.

Implements decentralized peer-to-peer handoffs between:
1. Customer Triage (Alex)
2. Fraud & Security (Sam)
3. Loan & Credit Underwriting (Morgan)
4. Compliance & AML (Jordan)
5. Core Settlement & Operations (Taylor)
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END
from agents.state import SwarmState
from agents.triage import triage_agent_node
from agents.fraud import fraud_agent_node
from agents.credit import credit_agent_node
from agents.compliance import compliance_agent_node
from agents.settlement import settlement_agent_node


def route_swarm(state: SwarmState) -> str:
    """Dynamic routing function evaluating the active agent in the swarm."""
    active = state.get("active_agent", "resolved")
    if active in ["resolved", "FINISH", "__end__", None]:
        return END
    return active


def build_banking_swarm_graph():
    """Constructs and compiles the LangGraph Swarm state machine."""
    workflow = StateGraph(SwarmState)

    # 1. Register the 5 Agent Nodes
    workflow.add_node("triage_agent", triage_agent_node)
    workflow.add_node("fraud_agent", fraud_agent_node)
    workflow.add_node("credit_agent", credit_agent_node)
    workflow.add_node("compliance_agent", compliance_agent_node)
    workflow.add_node("settlement_agent", settlement_agent_node)

    # 2. Add Conditional Edges for Swarm Dynamic Peer Handoffs
    routing_map = {
        "triage_agent": "triage_agent",
        "fraud_agent": "fraud_agent",
        "credit_agent": "credit_agent",
        "compliance_agent": "compliance_agent",
        "settlement_agent": "settlement_agent",
        END: END,
    }

    workflow.add_edge(START, "triage_agent")

    for agent_node in ["triage_agent", "fraud_agent", "credit_agent", "compliance_agent", "settlement_agent"]:
        workflow.add_conditional_edges(
            agent_node,
            route_swarm,
            routing_map
        )

    return workflow.compile()

