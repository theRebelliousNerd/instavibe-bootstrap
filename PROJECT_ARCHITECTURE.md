# Project Architecture: AI Developer Assistant

This document outlines the file and folder structure for the project. It is a living document and should be updated as the project evolves.

## Current Architecture

```
/instavibe-bootstrap/
├── .gemini/
│   └── settings.json
├── .git/
├── agents/
│   ├── __init__.py
│   ├── code_query/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── doc_search/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── code_modification/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── bug_assistant/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── requirements_interrogator/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── platform_mcp_client/
│   │   ├── __init__.py
│   │   ├── .env
│   │   ├── agent_executor.py
│   │   ├── agent.py
│   │   ├── Dockerfile
│   │   ├── __pycache__/
│   │   ├── requirements.txt
│   │   └── a2a_server.py
│   ├── orchestrate/
│   │   ├── remote_agent_connection.py
│   │   ├── __init__.py
│   │   ├── .env
│   │   ├── agent.py
│   │   ├── __pycache__/
│   │   ├── requirements.txt
│   │   └── .dockerignore
│   ├── .env
│   ├── cloudbuild-build.yaml
│   ├── cloudbuild.yaml
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── social/
│   │   ├── __init__.py
│   │   ├── .env
│   │   ├── agent_executor.py
│   │   ├── social_agent.py
│   │   ├── agent.py
│   │   ├── Dockerfile
│   │   ├── __pycache__/
│   │   ├── instavibe.py
│   │   ├── requirements.txt
│   │   └── a2a_server.py
│   ├── planner/
│   │   ├── planner_client.py
│   │   ├── __init__.py
│   │   ├── .env
│   │   ├── agent_executor.py
│   │   ├── .adk/
│   │   ├── agent.py
│   │   ├── Dockerfile
│   │   ├── __pycache__/
│   │   ├── requirements.txt
│   │   ├── planner_eval.evalset.json
│   │   └── a2a_server.py
├── cli/
│   ├── __init__.py
│   └── main.py
├── db/
│   ├── __init__.py
│   ├── schema.sql
│   ├── ingest_code.py
│   ├── ingest_docs.py
│   ├── features.yaml
│   ├── requirements.txt
│   ├── apply_schema.py
│   └── ingestion/
│       ├── __init__.py
│       ├── code_parser.py
│       ├── tree-sitter-python/
│       ├── build_grammar.py
│       ├── my-languages.so
│       ├── graph_updater.py
│       └── doc_parser.py
├── docs/
│   ├── DEV_ASSISTANT_PLAN.md
│   ├── tutorial_summary.md
│   └── sample_api.md
├── env/
├── instavibe/
│   ├── setup.py
│   ├── templates/
│   │   ├── index.html
│   │   ├── logs.html
│   │   ├── _macros.html
│   │   ├── 404.html
│   │   ├── graph.html
│   │   ├── introvert_ally_review.html
│   │   ├── introvert_ally_post_status.html
│   │   ├── person.html
│   │   ├── introvert_ally.html
│   │   ├── base.html
│   │   ├── plan.html
│   │   └── event_detail.html
│   ├── __init__.py
│   ├── reset.sql
│   ├── temp_endpoint.txt
│   ├── .env
│   ├── app.py
│   ├── ally_routes.py
│   ├── static/
│   │   ├── alice.png
│   │   ├── style.css
│   │   ├── css/
│   │   ├── js/
│   │   ├── logo.png
│   │   └── loading.gif
│   ├── db.py
│   ├── introvertally.py
│   ├── Dockerfile
│   ├── __pycache__/
│   ├── requirements.txt
│   ├── temp-endpoint.py
│   └── .dockerignore
├── prompts/
│   ├── features/
│   │   └── example_feature.md
│   └── requirements_interrogator_prompt.md
├── shortcut/
│   ├── remove.sh
│   └── set_base.sh
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── agents/
│       ├── __init__.py
│       └── test_orchestrator.py
├── tools/
│   ├── __init__.py
│   ├── .env
│   └── instavibe/
│       ├── .DS_Store
│       ├── Dockerfile
│       ├── instavibe.py
│       ├── requirements.txt
│       └── mcp_server.py
├── utils/
│   ├── __init__.py
│   └── remote_delete.py
├── .gitignore
├── DEV_ASSISTANT_PLAN.md
├── init.sh
├── PROJECT_ARCHITECTURE.md
├── README.md
├── requirements.txt
├── set_env.sh
└── tutorial_summary.md
```

## Planned Architecture

```
/instavibe-bootstrap/
├── .gemini/
│   └── settings.json           # MCP server configuration for A2A
├── agents/
│   ├── __init__.py
│   ├── code_query/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── doc_search/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── code_modification/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── bug_assistant/
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── requirements_interrogator/
│   │   ├── __init__.py
│   │   └── agent.py
│   └── ... (other agents: build, web_scraping, etc.)
├── cli/
│   ├── __init__.py
│   └── main.py                 # Main entry point for the Gemini CLI
├── db/
│   ├── __init__.py
│   ├── schema.sql              # Spanner DDL for the knowledge graph
│   ├── ingest_code.py          # Script to ingest code & features
│   ├── ingest_docs.py          # Script to ingest documents
│   ├── features.yaml           # Feature definitions for ingestion
│   └── requirements.txt        # Python dependencies for db scripts
├── docs/
│   ├── DEV_ASSISTANT_PLAN.md   # The main project plan
│   └── tutorial_summary.md     # Summary of the original codelab
├── instavibe/                  # Frontend Dashboard (Flask/React)
│   ├── __init__.py
│   ├── app.py                  # Main Flask application
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   └── templates/
│       ├── base.html
│       ├── index.html              # Main dashboard view
│       ├── graph.html              # Spanner graph visualization
│       ├── plan.html               # View for DEV_ASSISTANT_PLAN.md
│       └── logs.html               # View for .gemini.md logs
├── prompts/
│   └── features/
│       └── example_feature.md    # Example feature plan (Dossier + Blueprint)
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── agents/
│       ├── __init__.py
│       └── test_orchestrator.py
├── tools/
│   └── __init__.py
├── utils/
│   └── __init__.py
├── .gitignore
├── README.md                   # Updated README for the new project
├── requirements.txt
└── PROJECT_ARCHITECTURE.md     # This file
```
