#!/usr/bin/env python
# coding: utf-8

"""
This module provides a simple command-line interface (CLI) to interact with the AI developer assistant agents.
"""

import argparse
import sys

# Add the parent directory to the Python path to allow importing agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.code_query.agent import CodeQueryAgent
from agents.doc_search.agent import DocSearchAgent

def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="AI Developer Assistant CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Code Query Agent Commands ---
    code_query_parser = subparsers.add_parser("code-query", help="Query the codebase.")
    code_query_subparsers = code_query_parser.add_subparsers(dest="subcommand", required=True)

    find_callers_parser = code_query_subparsers.add_parser("find-callers", help="Find functions calling a specific function.")
    find_callers_parser.add_argument("function_name", type=str, help="The name of the function.")

    find_importers_parser = code_query_subparsers.add_parser("find-importers", help="Find files importing a specific file.")
    find_importers_parser.add_argument("file_name", type=str, help="The name of the file.")

    # --- Doc Search Agent Commands ---
    doc_search_parser = subparsers.add_parser("doc-search", help="Search the documentation.")
    doc_search_parser.add_argument("query", type=str, help="The search query.")

    args = parser.parse_args()

    if args.command == "code-query":
        agent = CodeQueryAgent()
        if args.subcommand == "find-callers":
            results = agent.find_functions_calling(args.function_name)
            print(results)
        elif args.subcommand == "find-importers":
            results = agent.find_files_importing(args.file_name)
            print(results)

    elif args.command == "doc-search":
        agent = DocSearchAgent()
        results = agent.search(args.query)
        print(results)

if __name__ == "__main__":
    main()
