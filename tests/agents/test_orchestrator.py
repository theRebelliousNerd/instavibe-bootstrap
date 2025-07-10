#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the orchestrator agent."""

import unittest
from agents.orchestrator.agent import OrchestratorAgent


class TestOrchestratorAgent(unittest.TestCase):
    """Tests for the orchestrator agent."""

    def test_handle_request(self):
        """Tests the handle_request method."""
        agent = OrchestratorAgent()
        response = agent.handle_request("test request")
        self.assertEqual(response, "Response from orchestrator agent.")

    # TODO: Add more tests for the orchestrator agent


if __name__ == "__main__":
    unittest.main()