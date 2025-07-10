#!/usr/bin/env python
# coding: utf-8

"""
This module defines the CodeQueryAgent.

The CodeQueryAgent is responsible for answering questions about the codebase
structure by querying the Spanner knowledge graph.
"""

import os
from google.cloud import spanner

# --- Spanner Configuration ---
INSTANCE_ID = os.environ.get("SPANNER_INSTANCE_ID")
DATABASE_ID = os.environ.get("SPANNER_DATABASE_ID")

def get_spanner_client():
    """Returns a Spanner client."""
    return spanner.Client()

def get_database(client):
    """Gets a Spanner database instance."""
    instance = client.instance(INSTANCE_ID)
    return instance.database(DATABASE_ID)

class CodeQueryAgent:
    """An agent that can query the codebase knowledge graph."""

    def __init__(self):
        """Initializes the CodeQueryAgent."""
        self.client = get_spanner_client()
        self.db = get_database(self.client)

    def run_spanner_graph_query(self, query):
        """Executes a Spanner Graph Query against the knowledge graph."""
        print(f"Executing query: {query}")
        with self.db.snapshot() as snapshot:
            results = snapshot.execute_sql(query)
            return list(results)

    def find_functions_calling(self, function_name):
        """Finds all functions that call a given function."""
        query = f"""
            SELECT f.name
            FROM Functions f
            JOIN Calls c ON f.function_id = c.caller_function_id
            JOIN Functions callee ON c.callee_function_id = callee.function_id
            WHERE callee.name = '{function_name}'
        """
        return self.run_spanner_graph_query(query)

    def find_files_importing(self, file_name):
        """Finds all files that import a given file."""
        query = f"""
            SELECT importer.path
            FROM Files importer
            JOIN Imports i ON importer.file_id = i.importer_file_id
            JOIN Files imported ON i.imported_file_id = imported.file_id
            WHERE imported.path LIKE '%{file_name}'
        """
        return self.run_spanner_graph_query(query)


def main():
    """Main function for testing the CodeQueryAgent."""
    agent = CodeQueryAgent()

    # Example usage:
    calling_functions = agent.find_functions_calling("some_function")
    print(f"Functions calling 'some_function': {calling_functions}")

    importing_files = agent.find_files_importing("some_file.py")
    print(f"Files importing 'some_file.py': {importing_files}")

if __name__ == "__main__":
    main()
