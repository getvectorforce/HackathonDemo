"""Unit and integration tests for the LangGraph Banking Swarm."""

import unittest
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

    def test_swarm_execution_flow(self):
        """Verify all 5 banking agents participate and achieve resolution."""
        initial_state: SwarmState = {
            "messages": [],
            "active_agent": "triage_agent",
            "incident": self.incident,
            "swarm_history": [],
            "resolution_summary": None,
            "is_resolved": False,
        }

        app = build_banking_swarm_graph()
        final_state = app.invoke(initial_state)

        self.assertTrue(final_state.get("is_resolved"))
        self.assertEqual(final_state.get("active_agent"), "resolved")
        self.assertIsNotNone(final_state.get("resolution_summary"))

        history = final_state.get("swarm_history", [])
        self.assertEqual(len(history), 5)

        agents_in_order = [h["agent"] for h in history]
        expected_order = [
            "triage_agent",
            "fraud_agent",
            "credit_agent",
            "compliance_agent",
            "settlement_agent"
        ]
        self.assertEqual(agents_in_order, expected_order)


if __name__ == "__main__":
    unittest.main()

