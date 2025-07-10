# AI Developer Assistant

This project is a personalized, codebase-aware AI assistant that actively participates in the software development lifecycle. The assistant is accessed via a command-line interface (CLI) and leverages a bitemporal knowledge graph and a suite of specialized AI agents to understand, query, and modify a large application's codebase and associated documentation.

## Project Plan

See [DEV_ASSISTANT_PLAN.md](DEV_ASSISTANT_PLAN.md) for the full project plan.

## Architecture

See [PROJECT_ARCHITECTURE.md](PROJECT_ARCHITECTURE.md) for the full project architecture.

## Getting Started

1.  **Set up the environment:**

    ```bash
    source set_env.sh
    ```

2.  **Apply the database schema:**

    ```bash
    python db/apply_schema.py
    ```

3.  **Run the CLI:**

    ```bash
    python cli/main.py --help
    ```