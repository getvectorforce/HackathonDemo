"""Main CLI Entrypoint: 5-Agent Banking Swarm Demo with Human-in-the-Loop (HITL).

Powered by:
- LangGraph Swarm Topology + MemorySaver Checkpointing
- Human-in-the-Loop (HITL) interrupt() and Command(resume)
- ChromaDB RAG Vector Store
- Meta Developer Model API (Muse: muse-spark)
"""

import sys
import os
import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.prompt import Prompt

from langgraph.types import Command
from config import META_MODEL, META_API_BASE, SIMULATION_MODE, META_API_KEY
from swarm.graph import build_banking_swarm_graph
from agents.state import SwarmState, IncidentData

console = Console()

AGENT_COLORS = {
    "triage_agent": ("Alex", "Triage & Customer Service", "cyan"),
    "fraud_agent": ("Sam", "Fraud & Security Specialist", "red"),
    "credit_agent": ("Morgan", "Loan & Credit Underwriting", "yellow"),
    "compliance_agent": ("Jordan", "AML & Compliance Officer", "blue"),
    "settlement_agent": ("Taylor", "Settlement & Operations Lead", "green"),
}


def print_banner():
    banner = Text()
    banner.append("🏦 Apex Global Bank - Autonomous Swarm with Human-in-the-Loop\n", style="bold cyan")
    banner.append("Decentralized Swarm Topology • HITL Verification Gate • ChromaDB RAG • Meta Muse API\n", style="italic white")
    
    mode_str = "Meta Muse Live API (api.meta.ai/v1)" if not SIMULATION_MODE and META_API_KEY else "Simulated Muse Agent Model (Offline Demo)"
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row("[bold yellow]Model Provider:[/]", f"Meta Developer Platform ({META_MODEL})")
    table.add_row("[bold yellow]API Endpoint:[/]", f"{META_API_BASE}")
    table.add_row("[bold yellow]Execution Mode:[/]", f"[green]{mode_str}[/]")
    table.add_row("[bold yellow]RAG Vector Store:[/]", "ChromaDB (5 Curated Banking Policies & SOPs)")
    table.add_row("[bold yellow]Topology:[/]", "LangGraph Swarm (Peer-to-Peer Agent Handoffs)")
    table.add_row("[bold yellow]HITL Support:[/]", "[bold green]Active (MemorySaver + interrupt)[/]")
    
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


def print_step(latest: dict, step_num: int):
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


def run_demo(auto_choice: str = None):
    print_banner()

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
        "customer_verification_status": None,
        "is_false_alarm": False,
    }

    thread_id = f"incident-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    config = {"configurable": {"thread_id": thread_id}}
    app = build_banking_swarm_graph()

    step_num = 1
    # Run graph until completion or interrupt
    stream_input = initial_state
    
    while True:
        interrupted = False
        interrupt_info = None

        for event in app.stream(stream_input, config=config):
            for node_name, state_update in event.items():
                if node_name == "__interrupt__":
                    interrupted = True
                    if isinstance(state_update, (list, tuple)) and len(state_update) > 0:
                        interrupt_info = state_update[0].value
                    elif isinstance(state_update, dict):
                        interrupt_info = state_update
                    break

                if isinstance(state_update, dict):
                    history = state_update.get("swarm_history", [])
                    if history:
                        print_step(history[-1], step_num)
                        step_num += 1

        if not interrupted:
            break

        # Display the Human-in-the-Loop prompt
        intr_val = interrupt_info or {}
        console.print("\n")
        
        alert_text = Text()
        alert_text.append(f"{intr_val.get('title', 'SECURITY VERIFICATION')}\n\n", style="bold red")
        alert_text.append(f"Transaction ID: {intr_val.get('tx_id')}\n", style="bold white")
        alert_text.append(f"Amount: ${intr_val.get('amount', 0):,.2f} at {intr_val.get('merchant')}\n", style="bold yellow")
        alert_text.append(f"Location: {intr_val.get('location')}\n\n", style="bold yellow")
        alert_text.append(f"Question: {intr_val.get('question')}\n\n", style="bold cyan")
        alert_text.append("Your Options:\n", style="bold white")
        for key, val in intr_val.get('choices', {}).items():
            alert_text.append(f"  • {val}\n", style="green" if "2" in val else "red")

        console.print(Panel(alert_text, title="[bold red]⚠️ HUMAN-IN-THE-LOOP (HITL) GATE TRIGGERED[/]", border_style="red", expand=True))

        if auto_choice:
            user_choice = auto_choice
            console.print(f"[bold cyan]Auto-selecting HITL response:[/] [bold yellow]{user_choice}[/]\n")
        else:
            user_choice = Prompt.ask(
                "\n[bold magenta]Enter your verification response (1 = Confirm Fraud, 2 = Approve Legitimate)[/]",
                choices=["1", "2", "CONFIRM_FRAUD", "LEGITIMATE"],
                default="1"
            )

        norm_choice = "CONFIRM_FRAUD" if user_choice in ["1", "CONFIRM_FRAUD"] else "LEGITIMATE"
        console.print(f"\n[bold green]✔ Human feedback captured:[/] [bold white]{norm_choice}[/]. Resuming Swarm...\n")

        # Set stream input for resumption
        stream_input = Command(resume=norm_choice)

    # Final summary check
    final_snap = app.get_state(config)
    final_state = final_snap.values
    if final_state and final_state.get("resolution_summary"):
        status_title = "[bold green]✔ FALSE ALARM RESOLVED (CARD KEPT ACTIVE)" if final_state.get("is_false_alarm") else "[bold green]✔ SWARM FRAUD CONTAINMENT & RESTITUTION COMPLETE"
        console.print(Panel(
            f"{status_title}[/]\n\n{final_state.get('resolution_summary')}",
            title="[bold green]Final Executive Summary[/]",
            border_style="green",
            expand=True
        ))
    
    console.print("\n[bold cyan]✨ Swarm execution completed successfully.[/]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5-Agent Banking Swarm with HITL")
    parser.add_argument("--auto", choices=["1", "2", "CONFIRM_FRAUD", "LEGITIMATE"], help="Automatically answer HITL interrupt")
    args = parser.parse_args()
    run_demo(auto_choice=args.auto)
