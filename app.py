"""Interactive Web Browser UI for 5-Agent Banking Swarm with Human-in-the-Loop (HITL).

Run with:
    streamlit run app.py
"""

import streamlit as st
from datetime import datetime
from langgraph.types import Command
from config import META_MODEL, META_API_BASE, SIMULATION_MODE, META_API_KEY
from swarm.graph import build_banking_swarm_graph
from agents.state import SwarmState, IncidentData
from rag.vector_store import retrieve_banking_knowledge

st.set_page_config(
    page_title="Apex Global Bank - Swarm Incident Response",
    page_icon="🏦",
    layout="wide"
)

# Custom Styling
st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 800; color: #1E3A8A; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1.1rem; color: #4B5563; margin-bottom: 1.5rem; }
    .agent-box { border-radius: 10px; padding: 15px; margin-bottom: 15px; border-left: 6px solid #3B82F6; background-color: #F8FAFC; }
    .hitl-alert { border-radius: 10px; padding: 20px; background-color: #FEF2F2; border: 2px solid #EF4444; margin: 20px 0; }
    .rag-chip { background-color: #FEF3C7; color: #92400E; font-size: 0.85rem; padding: 4px 8px; border-radius: 6px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏦 Apex Global Bank — Autonomous Swarm Response</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Decentralized 5-Agent Swarm with Real-Time Human-in-the-Loop (HITL) Verification Gate</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Topology & Model Settings")
    st.info(f"**Model:** {META_MODEL}\n\n**Provider:** Meta Developer Platform (`api.meta.ai/v1`)\n\n**Topology:** LangGraph Decentralized Swarm\n\n**Memory:** LangGraph Checkpointer (`MemorySaver`)")
    
    st.divider()
    st.subheader("🔍 ChromaDB RAG Explorer")
    rag_query = st.text_input("Test Knowledge Search:", value="Regulation E provisional credit timeline")
    if st.button("Search Knowledge Base"):
        res = retrieve_banking_knowledge(rag_query, n_results=1)
        st.caption(res)

    st.divider()
    if st.button("🔄 Reset Incident Simulation"):
        st.session_state.clear()
        st.rerun()

# Session State Initialization
if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"web-{datetime.now().strftime('%Y%m%d%H%M%S')}"
if "app" not in st.session_state:
    st.session_state.app = build_banking_swarm_graph()
if "history" not in st.session_state:
    st.session_state.history = []
if "hitl_interrupt" not in st.session_state:
    st.session_state.hitl_interrupt = None
if "final_summary" not in st.session_state:
    st.session_state.final_summary = None
if "is_resolved" not in st.session_state:
    st.session_state.is_resolved = False

# Incident Configuration Card
with st.expander("📋 View Incident Details (Alex Mercer - $2,450 Bucharest POS Swipe)", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Customer:** Alex Mercer (`CUST-4401`)")
        st.markdown("**Account:** `ACCT-99214-DDA`")
        st.markdown("**Card:** `****-****-****-4102`")
    with col2:
        st.markdown("**Disputed Tx:** `TX-8921-X` ($2,450.00)")
        st.markdown("**Merchant:** Luxury European Watches Ltd")
        st.markdown("**Location:** Bucharest, Romania")
    with col3:
        st.markdown("**Anomaly:** Impossible Travel Geo-Velocity")
        st.markdown("**Collateral Risk:** Upcoming Auto-Loan Debit $450.00")
        st.markdown("**Loan ID:** `LN-AUTO-9102`")

st.divider()

AGENT_THEMES = {
    "triage_agent": ("Alex", "Customer Triage Specialist", "#0284C7", "💬"),
    "fraud_agent": ("Sam", "Fraud & Security Specialist", "#DC2626", "🛡️"),
    "credit_agent": ("Morgan", "Loan & Credit Underwriter", "#D97706", "📈"),
    "compliance_agent": ("Jordan", "AML & Compliance Officer", "#4F46E5", "⚖️"),
    "settlement_agent": ("Taylor", "Settlement & Operations Lead", "#059669", "💳"),
}


def process_stream(stream_generator):
    for event in stream_generator:
        for node_name, state_update in event.items():
            if node_name == "__interrupt__":
                if isinstance(state_update, (list, tuple)) and len(state_update) > 0:
                    st.session_state.hitl_interrupt = state_update[0].value
                elif isinstance(state_update, dict):
                    st.session_state.hitl_interrupt = state_update
                return
            
            if isinstance(state_update, dict):
                history = state_update.get("swarm_history", [])
                if history:
                    st.session_state.history = history
                if state_update.get("resolution_summary"):
                    st.session_state.final_summary = state_update.get("resolution_summary")
                if state_update.get("is_resolved"):
                    st.session_state.is_resolved = True


# Run Simulation Trigger
if not st.session_state.history and not st.session_state.hitl_interrupt:
    if st.button("🚀 Start Autonomous Swarm Deliberation", type="primary"):
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
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        process_stream(st.session_state.app.stream(initial_state, config=config))
        st.rerun()

# Display Swarm Deliberations
if st.session_state.history:
    st.subheader("🗣️ Live Swarm Peer-to-Peer Deliberation")
    for idx, step in enumerate(st.session_state.history, start=1):
        agent_id = step.get("agent")
        name, role, color, icon = AGENT_THEMES.get(agent_id, (step.get("display_name"), "Agent", "#64748B", "🤖"))
        
        with st.container():
            st.markdown(f"""
            <div style="border-left: 5px solid {color}; padding: 12px 18px; margin-bottom: 12px; background: #FFFFFF; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: {color}; font-size: 1.05rem;">{icon} Step {idx}: {name} ({role})</span>
                    <span style="background: #F1F5F9; color: #475569; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600;">Handoff ➡️ {step.get('handoff_to')}</span>
                </div>
                <div style="font-size: 0.95rem; color: #1E293B; margin-bottom: 8px; line-height: 1.45;">{step.get('message')}</div>
                <div style="margin-top: 6px; font-size: 0.85rem;">
                    <span class="rag-chip">🔍 RAG Consulted</span> <span style="color: #64748B;">{step.get('rag_doc_consulted')}</span>
                </div>
                <div style="margin-top: 4px; font-size: 0.85rem; color: #059669; font-weight: 600;">
                    🛠️ Action Executed: {step.get('action_taken')}
                </div>
            </div>
            """, unsafe_allow_html=True)

# Human-in-the-Loop Interaction Card
if st.session_state.hitl_interrupt and not st.session_state.is_resolved:
    intr = st.session_state.hitl_interrupt
    st.markdown('<div class="hitl-alert">', unsafe_allow_html=True)
    st.markdown(f"### 🚨 {intr.get('title', 'SECURITY VERIFICATION REQUIRED')}")
    st.markdown(f"**Transaction:** `${intr.get('amount', 2450.0):,.2f}` at **{intr.get('merchant')}** ({intr.get('location')})")
    st.markdown(f"**Question:** `{intr.get('question')}`")
    st.markdown("Please choose your verification action to resume the swarm:")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚨 NO! This is Fraud (Lock Card & Claim Dispute)", type="primary", use_container_width=True):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            st.session_state.hitl_interrupt = None
            process_stream(st.session_state.app.stream(Command(resume="CONFIRM_FRAUD"), config=config))
            st.rerun()

    with btn_col2:
        if st.button("✅ YES! I Authorized this (Legitimate Travel)", type="secondary", use_container_width=True):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            st.session_state.hitl_interrupt = None
            process_stream(st.session_state.app.stream(Command(resume="LEGITIMATE"), config=config))
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# Final Consensus Summary Card
if st.session_state.final_summary:
    st.success("✔ Swarm Consensus Finalized")
    st.markdown("### 📑 Final Incident Resolution Summary")
    st.code(st.session_state.final_summary, language="text")

