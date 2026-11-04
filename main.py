"""Main CLI Entrypoint: 5-Agent Banking Swarm Demo.

Powered by:
- LangGraph Swarm Topology
- ChromaDB RAG Vector Store
- Meta Developer Model API (Muse: muse-spark)
"""

import sys
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from config import META_MODEL, META_API_BASE, SIMULATION_MODE, META_API_KEY
from swarm.graph import build_banking_swarm_graph
from agents.state import SwarmState, IncidentData

console = Console()


def print_banner():
    banner = Text()
    banner.append("🏦 Apex Global Bank - Autonomous Swarm Incident Response\n", style="bold cyan")
    banner.append("Decentralized Swarm Topology • LangGraph • ChromaDB RAG • Meta Muse API\n", style="italic white")
    
    mode_str = "Meta Muse Live API (api.meta.ai/v1)" if not SIMULATION_MODE and META_API_KEY else "Simulated Muse Agent Model (Offline Demo)"
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[bold yellow]Model Provider:[/]", f"Meta Developer Platform ({META_MODEL})")
    table.add_row("[bold yellow]API Endpoint:[/]", f"{META_API_BASE}")
    table.add_row("[bold yellow]Execution Mode:[/]", f"[green]{mode_str}[/]")
    table.add_row("[bold yellow]RAG Vector Store:[/]", "ChromaDB (5 Curated Banking Policies & SOPs)")
    table.add_row("[bold yellow]Topology:[/]", "LangGraph Swarm (Peer-to-Peer Agent Handoffs)")
    
    console.print(Panel(table, title="[bold green]Configuration & Topology[/]", expand=False))


def display_incident_card(incident: IncidentData):
    table = Table(title="🚨 High-Priority Banking Alert Received", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Customer", f"{incident.get('customer_name')} ({incident.get('customer_id')})")
    table.add_row("Impacted Account", f"{incident.get('account_id')}")
    table.add_row("Card Number", f"****-****-****-{incident.get('card_last_four')}")
    table.add_row("Disputed Transaction", f"{incident.get('tx_id')} - ${incident.get('amount'):,.2f}")
    table.add_row("Merchant & Geo", f"{incident.get('merchant')} ({incident.get('location')})")
    table.add_row("Collateral Risk", f"Upcoming Auto-Debit ${incident.get('upcoming_auto_debit'):,.2f} for Loan {incident.get('auto_debit_loan_id')}")

    console.print(table)
    console.print("\n[bold yellow]⚡ Initiating Swarm Consultation across Banking Divisions...[/]\n")


AGENT_COLORS = {
    "triage_agent": ("Alex", "Triage & Customer Service", "cyan"),
    "fraud_agent": ("Sam", "Fraud & Security Specialist", "red"),
    "credit_agent": ("Morgan", "Loan & Credit Underwriting", "yellow"),
    "compliance_agent": ("Jordan", "AML & Compliance Officer", "blue"),
    "settlement_agent": ("Taylor", "Settlement & Operations Lead", "green"),
}


def run_demo():
    print_banner()

    # Define sample incident scenario
    incident: IncidentData = {
        "customer_id": "CUST-4401",
        "customer_name": "Alex Mercer",
        "account_id": "ACCT-99214-DDA",
        "card_last_four": "4102",
        "tx_id": "TX-8921-X",
        "amount": 2450.00,
        "merchant": "Luxury European Watches Ltd",
        "location": "Bucharest, Romania",
        "device": "Unknown Android POS terminal",
        "upcoming_auto_debit": 450.00,
        "auto_debit_loan_id": "LN-AUTO-9102",
    }

    display_incident_card(incident)

    initial_state: SwarmState = {
        "messages": [],
        "active_agent": "triage_agent",
        "incident": incident,
        "swarm_history": [],
        "resolution_summary": None,
        "is_resolved": False,
    }

    app = build_banking_swarm_graph()

    # Execute graph stream
    final_state = None
    step_num = 1
    for step_output in app.stream(initial_state):
        for node_name, state_update in step_output.items():
            final_state = state_update
            history = state_update.get("swarm_history", [])
            if not history:
                continue
            
            latest = history[-1]
            agent_id = latest.get("agent")
            name, role, color = AGENT_COLORS.get(agent_id, (latest.get("display_name"), "Agent", "white"))

            content_text = Text()
            content_text.append(f"Deliberation:\n", style="bold")
            content_text.append(f"{latest.get('message')}\n\n", style="italic")
            content_text.append(f"🔍 ChromaDB RAG Policy Consulted:\n", style="bold yellow")
            content_text.append(f"{latest.get('rag_doc_consulted')}\n\n", style="dim")
            content_text.append(f"🛠️ Core Action Executed: ", style="bold green")
            content_text.append(f"{latest.get('action_taken')}\n", style="bold white")
            content_text.append(f"➡️ Swarm Peer Handoff: ", style="bold magenta")
            content_text.append(f"{latest.get('handoff_to')}\n", style="bold magenta")

            panel = Panel(
                content_text,
                title=f"[bold {color}]Step {step_num}: {name} ({role})[/]",
                border_style=color,
                expand=True
            )
            console.print(panel)
            step_num += 1

    # Final Resolution Summary
    if final_state and final_state.get("resolution_summary"):
        console.print(Panel(
            f"[bold green]✔ SWARM CONSENSUS REACHED & DISPUTE RESOLVED[/]\n\n"
            f"{final_state.get('resolution_summary')}",
            title="[bold green]Final Executive Summary[/]",
            border_style="green",
            expand=True
        ))
    
    console.print("\n[bold cyan]✨ Swarm execution completed successfully.[/]")


if __name__ == "__main__":
    run_demo()

