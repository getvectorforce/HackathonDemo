"""Unit and integration tests for the LangGraph Banking Swarm with HITL."""

import unittest
from langgraph.types import Command
from swarm.graph import build_banking_swarm_graph
from agents.state import SwarmState, IncidentData
from rag.vector_store import get_banking_vector_store, retrieve_banking_knowledge


class TestBankingSwarm(unittest.TestCase):

    def setUp(self):
        self.store = get_banking_vector_store()
        self.incident: IncidentData = {
            "customer_id": "TEST-CUST-101",
            "customer_name": "Jordan Lee",
            "account_id": "ACCT-TEST-999",
            "card_last_four": "5555",
            "tx_id": "TX-TEST-777",
            "amount": 1200.00,
            "merchant": "Foreign Electronics Hub",
            "location": "Berlin, Germany",
            "device": "Unknown POS",
            "upcoming_auto_debit": 200.00,
            "auto_debit_loan_id": "LN-TEST-01",
        }

    def test_chromadb_rag_retrieval(self):
        """Verify ChromaDB stores and retrieves banking policies."""
        result = retrieve_banking_knowledge("Regulation E dispute provisional credit")
        self.assertIsNotNone(result)
        self.assertIn("Regulation E", result)

    def test_swarm_hitl_branch_confirm_fraud(self):
        """Verify HITL flow when customer confirms unauthorized fraud."""
        initial_state: SwarmState = {
            "messages": [],
            "active_agent": "triage_agent",
            "incident": self.incident,
            "swarm_history": [],
            "resolution_summary": None,
            "is_resolved": False,
            "customer_verification_status": None,
            "is_false_alarm": False,
        }

        app = build_banking_swarm_graph()
        config = {"configurable": {"thread_id": "test-hitl-fraud"}}

        # 1. Run until HITL interrupt
        res1 = app.invoke(initial_state, config=config)
        snap1 = app.get_state(config)
        self.assertTrue(len(snap1.tasks) > 0)
        self.assertTrue(len(snap1.tasks[0].interrupts) > 0)

        # 2. Resume with CONFIRM_FRAUD
        res2 = app.invoke(Command(resume="CONFIRM_FRAUD"), config=config)
        self.assertTrue(res2.get("is_resolved"))
        self.assertEqual(res2.get("customer_verification_status"), "CONFIRMED_FRAUD")
        self.assertFalse(res2.get("is_false_alarm"))
        self.assertEqual(len(res2.get("swarm_history")), 5)

    def test_swarm_hitl_branch_legitimate_travel(self):
        """Verify HITL flow when customer verifies legitimate travel (false alarm)."""
        initial_state: SwarmState = {
            "messages": [],
            "active_agent": "triage_agent",
            "incident": self.incident,
            "swarm_history": [],
            "resolution_summary": None,
            "is_resolved": False,
            "customer_verification_status": None,
            "is_false_alarm": False,
        }

        app = build_banking_swarm_graph()
        config = {"configurable": {"thread_id": "test-hitl-legit"}}

        # 1. Run until HITL interrupt
        res1 = app.invoke(initial_state, config=config)
        snap1 = app.get_state(config)
        self.assertTrue(len(snap1.tasks) > 0)

        # 2. Resume with LEGITIMATE
        res2 = app.invoke(Command(resume="LEGITIMATE"), config=config)
        self.assertTrue(res2.get("is_resolved"))
        self.assertEqual(res2.get("customer_verification_status"), "LEGITIMATE_PURCHASE")
        self.assertTrue(res2.get("is_false_alarm"))
        # Only Triage -> Fraud (HITL) -> Triage (Closure) = 3 steps
        self.assertEqual(len(res2.get("swarm_history")), 3)


if __name__ == "__main__":
    unittest.main()
