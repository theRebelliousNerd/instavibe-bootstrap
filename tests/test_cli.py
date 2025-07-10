#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the Gemini CLI."""

import unittest
from click.testing import CliRunner
from cli.main import cli


class TestCli(unittest.TestCase):
    """Tests for the Gemini CLI."""

    def test_ideate(self):
        """Tests the ideate command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["ideate"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Ideate command called.", result.output)

    def test_ask(self):
        """Tests the ask command."""
        runner = CliRunner()
        result = runner.invoke(cli, ["ask", "test question"])
        self.assertEqual(result.exit_code, 0)
        self.assertIn("Ask command called with question: test question", result.output)

    # TODO: Add tests for the other CLI commands


if __name__ == "__main__":
    unittest.main()