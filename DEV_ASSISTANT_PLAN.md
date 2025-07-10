# Project Plan: InstaVibe to AI Developer Assistant

## 1. Project Vision

This document outlines the plan to transition the "InstaVibe" codebase from its current state (a completed tutorial project) into a sophisticated, personalized, codebase-aware AI developer assistant. The assistant will be accessed via a command-line interface (CLI) and will leverage a bitemporal knowledge graph and a suite of specialized AI agents to understand, query, and modify a large application's codebase and associated documentation.

## 2. Core Architectural Components

The project will be built on the foundation of the `instavibe-bootstrap` architecture, evolving its components for the new developer-focused purpose.

*   **CLI (The Frontend):** A new Gemini CLI will replace the InstaVibe web app as the user interface.
*   **Orchestrator Agent (The Brain):** The existing Orchestrator agent will be adapted to handle developer-centric commands.
*   **Specialized Agents (The Hands):** A new suite of agents will be created, each with a specific developer-focused toolset.
*   **Knowledge Graph (The Memory):** The Spanner database will be evolved into a comprehensive, bitemporal knowledge graph and vector database.
*   **Cloud Platform (The Engine):** The entire system will run on Google Cloud, using Vertex AI Agent Engine and Cloud Run.

---

## 3. Phase 1: The Knowledge Graph (Spanner)

The foundation of the assistant is its ability to understand the codebase. This phase focuses on building the data ingestion pipeline to populate the Spanner database.

### 3.1. Spanner Schema Design

*   **Nodes:**
    *   `File`: Represents a file in the codebase.
    *   `Function`: Represents a function or method.
    *   `Class`: Represents a class.
    *   `Feature`: A conceptual node representing a specific product feature (e.g., "User Authentication", "Payment Processing"). Acts as a hub for all related artifacts.
    *   `APIDocument`: Represents a document for an API.
    *   `Tutorial`: Represents a tutorial document.
    *   `ToDoItem`: Represents a task from a to-do list.
    *   `DocChunk`: Represents a chunk of a document for vector search.
    *   `CodeIssue`: Represents a specific problem or status associated with a code node (e.g., "Broken", "NeedsDependencies", "NeedsGroundingData").
*   **Edges:**
    *   `IMPORTS`: Represents a file importing another file.
    *   `CALLS`: Represents a function calling another function.
    *   `IMPLEMENTS`: Represents a class implementing an interface.
    *   `REFERENCES`: Represents a file referencing another file or a document.
    *   `HAS_CHUNK`: Represents a document having a document chunk.
    *   `HAS_ISSUE`: Connects a code node to a `CodeIssue` node.
    *   `IMPLEMENTS_FEATURE`: Connects a code node (File, Function, Class) to a `Feature` node.
    *   `DOCUMENTS_FEATURE`: Connects a documentation node (APIDocument, Tutorial) to a `Feature` node.

### 3.2. The Graph as a RAG Index (Not a Code Mirror)

A critical principle of this architecture is that the Spanner knowledge graph serves as a metadata index and a system for Retrieval-Augmented Generation (RAG), not as a complete, versioned mirror of the codebase. The agent's primary source of truth for file content is always the live file system in the user's workspace.

*   **Workspace is Primary:** The `CodeModificationAgent` and other agents will always read file contents directly from the workspace using tools like `read_file` before taking action.
*   **Graph Provides Paths and Context:** The graph's role is to store the paths to files and the rich web of relationships (calls, implementations, issues, documentation) between them. An agent queries the graph to understand *what* to read and *how it connects* to everything else.
*   **`File.content` Field Usage:** The `content` field in the `Files` table is intended as a limited cache or for very small, critical configuration files. It should not be treated as the canonical source for file content.

### 3.3. Graph-Powered RAG and Code Health Analysis

To enable a high-confidence RAG model for code generation, the assistant must not only understand the code but also its health and its relationship to available documentation. The `Feature` node is central to this strategy.

*   **Code Health Analysis:**
    *   A dedicated process (or a new `CodeHealthAgent`) will periodically scan the codebase.
    *   Using static analysis tools, it will identify issues like syntax errors, unresolved imports ("Needs Dependencies"), or failed tests ("Broken").
    *   For each issue found, it will create a `CodeIssue` node and link it to the relevant `File`, `Function`, or `Class` node with a `HAS_ISSUE` edge.
    *   **Integration with CI/CD:** The `CodeHealthAgent` will be linked to GitHub Actions or Cloud Build to provide real-time analysis on pull requests, creating `CodeIssue` nodes preemptively.
    *   **AI-Driven Issue Prioritization:** Vertex AI will be used to score `CodeIssue` severity based on factors like affected features or historical fixes, adding a `priority_score` field to the `CodeIssue` node.

*   **RAG Grounding via Features:**
    *   The system evaluates its readiness to perform tasks by checking if a feature is well-documented.
    *   For a given `Feature` node, the system will check for outgoing `DOCUMENTS_FEATURE` edges. If there are few or no connections to `APIDocument` or `Tutorial` nodes, a `CodeIssue` with the type "NeedsGroundingData" can be attached to the `Feature` node itself. This signals that the assistant needs more information before it can confidently work on this feature.

*   **RAG in Action:**
    *   When the `CodeModificationAgent` is tasked with a change related to a feature (e.g., "add a field to the user profile"), it will first identify the relevant `Feature` node ("User Profile").
    *   The query will then gather all context by traversing the graph from that central `Feature` node:
        1.  Get all code: Follow all `IMPLEMENTS_FEATURE` edges to retrieve the relevant `File`, `Function`, and `Class` nodes.
        2.  Get all documentation: Follow all `DOCUMENTS_FEATURE` edges to retrieve `APIDocument` and `Tutorial` nodes.
        3.  Get all known issues: Check for any `CodeIssue` nodes attached to the feature or its constituent code nodes.
    *   This provides a rich, holistic context, allowing the agent to make more informed and accurate code modifications.

### 3.4. Data Ingestion Pipeline: Code

*   **Trigger:** Git hooks (`post-commit`) or a scheduled Cloud Function.
*   **Process:**
    1.  Scan the codebase for changes.
    2.  For each changed file, parse it into an Abstract Syntax Tree (AST).
    3.  Extract nodes (files, functions, classes) and edges (imports, calls, etc.) from the AST.
    4.  Upsert the nodes and edges into the Spanner graph, using commit timestamps for bitemporality.

### 3.5. Data Ingestion Pipeline: Documents & Features

*   **Trigger:** Manual or a scheduled Cloud Function.
*   **Process:**
    1.  **Feature Identification:** Identify `Feature` nodes. This can be done manually, by convention (e.g., a `features.yaml` file in the repo), or by parsing issue tracker tickets or conventional commit messages.
    2.  **Document Ingestion:** Read documents from a specified directory.
    3.  **Chunking & Embeddings:** Chunk the documents and generate vector embeddings for each chunk.
    4.  **Storage:** Store chunks and embeddings in Spanner.
    5.  **Link to Features:** Establish `DOCUMENTS_FEATURE` edges connecting the new `APIDocument` or `Tutorial` nodes to the appropriate `Feature` nodes.

### 3.6. Data Ingestion Pipeline: Web Content

*   **Trigger:** Manual or scheduled Cloud Function.
*   **Process:**
    1.  Crawl specified URLs using the `WebScrapingAgent`.
    2.  The agent will use `crawl4ai` to extract clean, LLM-ready content.
    3.  Chunk the scraped content.
    4.  Generate vector embeddings for each chunk.
    5.  Store the chunks and embeddings in Spanner, linking them to a new `WebArticle` node.

### 3.7. Data Ingestion Pipeline: Database Schema

*   **Trigger:** Manual or scheduled Cloud Function.
*   **Process:**
    1.  Connect to the application's database.
    2.  Introspect the database schema to get table and column information.
    3.  Create `Table` and `Column` nodes in the Spanner graph.
    4.  Create `HAS_COLUMN` edges to link tables and columns.

### 3.8. Bitemporal Graph Implementation

To truly understand the evolution of the codebase, the knowledge graph must be bitemporal, tracking not only the current state but also all previous states of the code's structure. This allows us to ask questions about the code "as it was" at any given point in time. We achieve this by versioning the relationships (edges) in our graph, tying them to the commit history.

*   **Error Handling:** Ingestion pipelines will be designed with robust error handling, including:
    *   **Retry and Idempotency:** Use exponential backoff for failed parsing or Spanner upserts, with idempotent keys (e.g., commit hash + node ID) to prevent duplicate data.
    *   **Validation Step:** After ingestion, run consistency checks (e.g., ensure no dangling edges) and log any discrepancies as new `CodeIssue` nodes.

#### 3.8.1. Bitemporal Schema: Versioning Edges

The core idea is that nodes (files, functions, classes) are relatively stable entities, but the relationships between them change with every commit. We will model this by adding two fields to our edge tables (`IMPORTS`, `CALLS`, `IMPLEMENTS`, etc.).

*   `valid_from_commit`: (String) The commit hash from which this relationship becomes active.
*   `valid_to_commit`: (String) The commit hash when this relationship ceases to be valid. A `NULL` or special value (e.g., 'HEAD') indicates the relationship is currently active.
*   `branch_name`: (String) The name of the branch where the change occurred, to support non-linear histories.

**Example: `CALLS` Edge Table Schema**
'''sql
CREATE TABLE Calls (
    caller_id STRING(36),
    callee_id STRING(36),
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    -- Foreign keys to the 'Nodes' table
);
'''

#### 3.8.2. Bitemporal Ingestion Logic

The data ingestion pipeline, triggered by a `post-commit` hook, becomes more sophisticated. For each commit, it performs a "diff" on the graph state.

*   **Trigger:** Git `post-commit` hook. The hook script will pass the new commit hash and the parent commit hash to the ingestion service.

*   **Process:**
    1.  **Identify Changes:** The service first identifies all files changed in the new commit.
    2.  **Parse New State:** It parses the changed files to determine the *new* set of relationships (e.g., function `A` now calls function `C` but no longer calls `B`).
    3.  **"Close" Old Relationships:** For every relationship that existed in the parent commit but does *not* exist in the new commit, the pipeline finds the corresponding edge in Spanner. It then updates that edge's `valid_to_commit` from `NULL` to the new commit hash. This effectively "archives" the old relationship, marking it as inactive from this point forward.
    4.  **Create New Relationships:** For every new relationship found in the current commit that did *not* exist in the parent, a new edge is inserted into the appropriate table. The `valid_from_commit` is set to the new commit hash, and `valid_to_commit` is set to `NULL`.

This process ensures that for any given commit hash, we can reconstruct the exact state of the codebase's structure.

#### 3.8.3. Time-Aware Querying

The `CodeQueryAgent` will be designed to leverage this bitemporal data.

*   **Default Queries:** By default, queries will inspect the *current* state of the codebase. The agent's tool (`run_spanner_graph_query`) will automatically add a `WHERE valid_to_commit IS NULL` clause to its queries.
    *   *Example:* "Find all functions that call `UserService.update`" will only return functions that call it in the latest version of the code.

*   **Historical Queries:** The agent will also support point-in-time analysis.
    *   *Example:* "Show me what functions called `UserService.update` in commit `a1b2c3d`". The agent would find all `CALLS` edges where `valid_from_commit <= a1b2c3d` and `valid_to_commit > a1b2c3d` (or is `NULL`).
    *   *Branch-Aware Queries:* "What changed in this feature on the `dev` branch?"

### 3.9. Scalability and Optimization

For large codebases, Spanner queries can become bottlenecks. The following strategies will be employed:

*   **Indexing Strategies:** Beyond default indexes, composite indexes will be created on high-traffic fields like `valid_from_commit` and `valid_to_commit`. Interleaved tables will be used for parent-child relationships.
*   **Partitioning:** Edge tables will be partitioned by commit ranges or feature IDs to improve query performance.
*   **Caching Layer:** A Redis or Memorystore cache will be introduced for frequent graph traversals.
*   **Monitoring:** Cloud Monitoring will be used to track query latencies and ingestion throughput.

### 3.10. Multi-Language Support

The ingestion pipeline will be extended to support multiple languages (e.g., JavaScript, Java) using language-specific parsers like Tree-sitter. A `Language` property will be added to `File` nodes.

---

## 4. Phase 2: The Specialized Agents

With the knowledge graph in place, we can build the agents that will use it.

### 4.1. `CodeQueryAgent`

*   **Purpose:** Answers questions about the codebase structure.
*   **Tools:**
    *   `run_spanner_graph_query`: Executes a Spanner Graph Query against the knowledge graph.
*   **Example:** "Find all functions that call the `UserService.update` method."

### 4.2. `DocSearchAgent`

*   **Purpose:** Answers questions based on API docs, tutorials, and architecture notes using a hybrid search approach.
*   **Tools:**
    *   `vertex_vector_search`: Performs a vector similarity search against the Vertex AI index to find relevant document chunks.
    *   `run_spanner_query`: Retrieves the full text and metadata of the chunks from Spanner using the IDs returned by the vector search.
    *   `run_spanner_graph_query`: Traverses the graph from the retrieved documents to find related features, code, or issues.
*   **Example:** "How do I authenticate with the Stripe API according to our docs?" The agent would first find relevant doc chunks in Vertex AI, retrieve their content from Spanner, and then use the graph to see which features or code examples are linked to those docs.

### 4.3. `WebScrapingAgent`

*   **Purpose:** Fetches and processes content from the web.
*   **Tools:**
    *   `crawl_url`: Uses `crawl4ai` to scrape a URL and return clean, LLM-ready content.
*   **Example:** "Scrape the latest documentation for the `requests` library."

### 4.4. `AppDatabaseAgent`
*   **Purpose:** Interacts with the application's database.
*   **Tools:** Leverages MCP Toolbox for secure execution; generates SQL via LLM, then invokes predefined tools.
*   **Example Workflow:** For "How many users signed up?", generate SQL with LLM, execute via `execute_app_sql` tool.

### 4.5. `CodeModificationAgent`
*   **Purpose:** Writes and modifies code.
*   **Tools:**
    *   `read_file`
    *   `write_file`
    *   `replace`
    *   `generate_diff`
    *   `simulate_change`: To dry-run modifications.
*   **Workflow:** Mandates human-in-the-loop for changes: Generate diffs and require CLI approval before applying.
*   **Example:** "Add a new field `last_login` to the `User` model in `models.py`."

### 4.6. `BuildAgent`
*   **Purpose:** Interacts with the build system to compile or package the application.
*   **Tools:**
    *   `run_shell_command`
*   **Example:** "Run the build process for the `api` module."

### 4.7. `BugAssistantAgent`
*   **Purpose:** Manages the testing and debugging process.
*   **Tools:**
    *   `run_shell_command`: To execute test suites (e.g., `pytest`, `npm test`) and debugging aids (e.g., `gdb`, `pdb`).
    *   `run_spanner_graph_query`: To find related code, documentation, and recent changes when a test fails.
    *   Integration with external tools like Sentry for error tracking.
*   **Workflow:**
    1.  Executes a specified test suite.
    2.  Parses the output for failures.
    3.  If a test fails, it queries the knowledge graph to find the code that was changed in the most recent commits that is related to the failed test.
    4.  It presents the failed test, the error message, and the relevant code changes to the user or another agent for debugging.
*   **Example:** "Run the tests for the `payments` feature. If they fail, show me the recent changes to the `StripeClient` class."

### 4.8. `RequirementsInterrogatorAgent`
*   **Purpose:** Acts as a thought partner to refine raw feature ideas into well-defined, actionable plans. It challenges assumptions, suggests alternatives, and considers technical constraints.
*   **Tools:**
    *   `read_file`: To analyze user-provided build plans or feature documents.
    *   `google_web_search`: To research existing solutions and best practices.
    *   `run_spanner_graph_query`: To understand the existing application context and identify potential integration points or conflicts.
    *   `x_search`: To gauge community sentiment on similar features.
*   **Workflow:**
    1.  **Analyze Input:** Receives a high-level feature idea or a detailed build plan document from the user via the `read_file` tool.
    2.  **Summarize and Verify:** Presents a concise summary of its understanding of the core goals and asks for confirmation.
    3.  **Interrogate and Refine:** Engages in a targeted dialogue based on the provided document. It identifies potential ambiguities, challenges assumptions, and explores alternatives for performance, cost, and reliability.
    4.  **Co-Create the Feature Plan:** Collaboratively builds out the final, detailed feature specification.

### 4.9. `DeploymentAgent`
*   **Purpose:** Automates deployment and rollback, integrating with the build process.
*   **Tools:** `run_shell_command` (for `kubectl` or `gcloud deploy`), `run_spanner_graph_query` (to check post-deployment issues).
*   **Workflow:** After `BuildAgent` succeeds, it deploys via Cloud Run or Kubernetes, then queries the graph for new `CodeIssue` nodes from logs.

### 4.10. Agent Enhancements and Testing
*   **Orchestrator Enhancements:** Add routing logic for hybrid queries (e.g., if `CodeQueryAgent` needs docs, delegate to `DocSearchAgent`). Include a global error handler that retries with alternative agents or prompts user for clarification.
*   **Agent Testing Framework:** Develop unit tests for each agent's tools using Pytest, mocking Spanner and Vertex AI. Include end-to-end scenarios in Milestone 3.

### 4.9. `DeploymentAgent`

*   **Purpose:** Automates deployment and rollback, integrating with the build process.
*   **Tools:**
    *   `run_shell_command`: For `kubectl` or `gcloud deploy`.
    *   `run_spanner_graph_query`: To check post-deployment issues.
*   **Workflow:** After `BuildAgent` succeeds, it deploys via Cloud Run or Kubernetes, then queries the graph for new `CodeIssue` nodes from logs.

### 4.10. Agent Enhancements and Testing

*   **Orchestrator Enhancements:** Add routing logic for hybrid queries (e.g., if `CodeQueryAgent` needs docs, delegate to `DocSearchAgent`). Include a global error handler that retries with alternative agents or prompts user for clarification.
*   **`CodeModificationAgent`:** Mandate human-in-the-loop for changes: Generate diffs and require CLI approval before applying. Add a `simulate_change` tool to dry-run modifications.
*   **`BugAssistantAgent`:** Expand to include debugging aids like attaching `gdb` or `pdb` via `run_shell_command`, and integrate with external tools like Sentry for error tracking.
*   **Agent Testing Framework:** Develop unit tests for each agent's tools using Pytest, mocking Spanner and Vertex AI. Include end-to-end scenarios in Milestone 3.

---

## 5. Phase 2.5: Integrating MCP Toolbox for Databases (genai-toolbox)

This intermediate phase sets up the `genai-toolbox` as an MCP server to define and expose database tools. It acts as a control plane between agents and databases (e.g., the application's DB and Spanner knowledge graph), simplifying tool invocation while adding security and observability. The toolbox is in beta (as of v0.8.0+), so monitor for updates; it supports semantic versioning for backward compatibility.

### 5.1. Setup and Deployment

*   **Installation:** Use Docker for Cloud Run deployment to align with the project's Google Cloud engine.
    '''bash
    export VERSION=0.8.0  # Check releases for latest (e.g., post-2025 updates)
    docker pull us-central1-docker.pkg.dev/database-toolbox/toolbox/toolbox:$VERSION
    '''
*   Deploy as a container on Cloud Run, exposing port 5000. Enable auto-reloading for dynamic tool updates.
*   **Configuration File (`tools.yaml`):** Define sources, tools, and toolsets in a version-controlled YAML file stored in the repo (e.g., `/config/tools.yaml`). Load it via `--tools-file` flag when running the server.
*   **Security Best Practices:**
    *   Use environment variables (e.g., `${DB_PASSWORD}`) for secrets, integrated with Cloud Secret Manager.
    *   Enable auth (e.g., IAM-based) for tool access.
    *   Integrate OpenTelemetry for tracing and metrics, exporting to Cloud Monitoring.
    *   Connection pooling is automatic; set max connections based on expected agent load.
*   **Observability:** Out-of-the-box metrics for tool invocations; add custom traces for query latency in Spanner graph operations.

### 5.2. Defining Sources

Sources configure database connections. For the application's database (assuming PostgreSQL or similar) and Spanner knowledge graph:

*   **Application DB Source (e.g., Cloud SQL for PostgreSQL):**
    '''yaml
    sources:
      app-db-source:
        kind: cloud-sql-postgres
        project: your-project-id
        region: us-central1
        instance: app-instance-name
        database: app_database
        user: ${APP_DB_USER}
        password: ${APP_DB_PASSWORD}
    '''
*   **Spanner Knowledge Graph Source:**
    '''yaml
    sources:
      spanner-graph-source:
        kind: spanner
        project: your-project-id
        instance: knowledge-graph-instance
        database: knowledge_graph_db
        # Additional params like auth can be inferred from IAM
    '''

### 5.3. Defining Tools

Tools define actions like SQL queries. Use `kind: spanner-sql` for Spanner (supports SQL and GQL statements for graph queries). These replace/adapt the `natural_language_to_sql` and `run_sql_query` in `AppDatabaseAgent`, allowing agents to invoke predefined tools securely.

*   **Example for `AppDatabaseAgent` (Natural Language to SQL Flow):**
    Define a generic SQL execution tool; the agent can use LLM to generate SQL from NL, then invoke this tool.
    '''yaml
    tools:
      execute_app_sql:
        kind: cloud-sql-postgres-sql  # Or spanner-sql if app DB is Spanner
        source: app-db-source
        description: Execute a safe, read-only SQL query against the application database.
        parameters:
          - name: sql_query
            type: string
            description: The SQL query to execute (generated from natural language).
        statement: $1  # Placeholder for dynamic SQL; ensure sanitization
    '''
*   For NL conversion: Retain `natural_language_to_sql` but chain it: Agent generates SQL via LLM, then calls `execute_app_sql`.
*   **Example for `CodeQueryAgent` (Spanner Graph Queries):**
    Define tools for graph traversals using Spanner's GQL or SQL.
    '''yaml
    tools:
      query_code_graph:
        kind: spanner-sql
        source: spanner-graph-source
        description: Run a graph query on the knowledge graph (e.g., find calling functions).
        parameters:
          - name: feature_name
            type: string
            description: The feature to query (e.g., 'User Authentication').
          - name: commit_hash
            type: string
            description: Optional commit for bitemporal query.
        statement: |
          SELECT f.id, f.name
          FROM Features AS feat
          JOIN ImplementsFeature AS impl ON feat.id = impl.feature_id
          JOIN Functions AS f ON impl.function_id = f.id
          WHERE feat.name = $1
          AND (impl.valid_to_commit IS NULL OR impl.valid_to_commit > $2)
    '''

### 5.4. Defining Toolsets

Group tools for agents:

'''yaml
toolsets:
  database_agents:
    - execute_app_sql
    - query_code_graph
  # Add more for specific agents
'''

### 5.5. SDK Integration (Python Focus, for Vertex AI Agents)

Use the Core or LangChain SDK to load tools into agents. Install: `pip install toolbox-core` or `pip install toolbox-langchain`.

*   **Loading Tools in Agents (e.g., `AppDatabaseAgent`):**
    '''python
    from toolbox_core import ToolboxClient  # Or toolbox_langchain for LangChain integration

    async with ToolboxClient("https://your-toolbox-service-url") as client:
        tools = await client.load_toolset("database_agents")
        # Pass 'tools' to the agent's configuration in Vertex AI
    '''
*   In the agent's logic: Use loaded tools for invocation, e.g., call `execute_app_sql` with generated SQL.
*   **Enhancing `natural_language_to_sql`:**
    Structure as a workflow: Agent prompts LLM for SQL generation (e.g., via Vertex AI), then invokes toolbox tool for execution. This adds security (e.g., toolbox can enforce read-only).
*   **Google Cloud Integration:**
    *   Deploy on Cloud Run for scalability.
    *   Use with Vertex AI: Load tools in orchestrator agent, distribute to specialized agents.
    *   For graph RAG: Toolbox tools can fetch context from Spanner for RAG grounding.

### 5.6. Testing and Iteration

*   Test tool invocations via CLI or unit tests.
*   Monitor for beta changes; update to stable v1.0+ when available.

---

## 6. Phase 3: The Gemini CLI

The final phase is to build the user-facing CLI.

### 6.1. CLI Design

*   **Framework:** Python's `click` or `argparse` library.
*   **Commands:**
    *   `ideate`: Initiates a session with the `RequirementsInterrogatorAgent`.
    *   `ask`: For general questions that will be routed to the Orchestrator.
    *   `refactor`: For specific code modification tasks, likely using a feature plan.
    *   `test`: For running tests with the `BugAssistantAgent`.
    *   `build`: For running builds with the `BuildAgent`.

### 6.2. A2A Integration & MCP Configuration

*   The CLI will act as an A2A client, sending user commands to the Orchestrator agent.
*   The connection will be established by configuring a local **Model Context Protocol (MCP) Server** in the `gemini-cli`'s project-specific settings.
*   A `.gemini/settings.json` file will be created in the project's root directory.
*   This file will instruct the `gemini-cli` to launch a local proxy process (the MCP server) which will in turn connect to the deployed Orchestrator agent on Vertex AI Agent Engine. This avoids the need to modify the `gemini-cli`'s source code.
*   Environment variable overrides will be supported for testing local vs. cloud modes.

**`.gemini/settings.json` Example:**
'''json
{
  "mcpServers": {
    "dev-assistant-orchestrator": {
      "command": "adk",
      "args": ["web", "-a", "orchestrate"]
    }
  }
}
'''

### 6.3. Usability and Extensibility

*   **Interactive Mode:** Add a REPL-like mode for multi-turn conversations (e.g., `gemini repl` for iterative ideation).
*   **Help and Documentation:** Auto-generate command help from agent descriptions, plus a `docs` command to query internal assistant docs.
*   **Plugin System:** Allow users to extend with custom agents via a plugin directory, loading them dynamically.
*   **Error Reporting:** Built-in feedback loop to report agent failures to a central log, potentially triggering self-healing (e.g., re-ingest graph).

---

## 7. Dependencies

*   **`crawl4ai`:** [https://github.com/crawl4ai/crawl4ai](https://github.com/crawl4ai/crawl4ai)
*   **`genai-toolbox`:** [https://github.com/googleapis/genai-toolbox](https://github.com/googleapis/genai-toolbox) - Core library for the MCP Toolbox for Databases. See full docs at [https://googleapis.github.io/genai-toolbox/](https://googleapis.github.io/genai-toolbox/).
    *   `toolbox-core`: Core SDK for programmatic tool loading.
    *   `toolbox-langchain`: LangChain integration for the toolbox.
*   **`context7`:** [https://github.com/upstash/context7](https://github.com/upstash/context7) - Potential for real-time context management.
*   **`claude-task-master`:** [https://github.com/eyaltoledano/claude-task-master](https://github.com/eyaltoledano/claude-task-master) - Reference for task management and agent orchestration.

### 7.1. Spanner Graph Resources

*   **Official Documentation**
    *   [Spanner Graph Overview](https://cloud.google.com/spanner/docs/graph/overview)
    *   [Spanner Graph Product Page](https://cloud.google.com/products/spanner/graph)
    *   [Schemas Overview](https://cloud.google.com/spanner/docs/schema-and-data-model)
    *   [Schema Design Best Practices](https://cloud.google.com/spanner/docs/schema-design)
    *   [Set Up and Query Spanner Graph](https://cloud.google.com/spanner/docs/graph/set-up)
*   **Tutorials and Guides**
    *   [Getting Started with Spanner Graph (Google Codelab)](https://codelabs.developers.google.com/codelabs/spanner-graph-getting-started)
    *   [Using Spanner Graph with LangChain for GraphRAG](https://cloud.google.com/blog/products/databases/using-spanner-graph-with-langchain-for-graphrag)
    *   [Unraveling Cinematic Connections: Analyzing Relationships with Spanner Graph](https://medium.com/google-cloud/unraveling-cinematic-connections-analyzing-movie-people-relationships-with-spanner-graph-47ccc50b07ec)
    *   [Clinical Trial Search with Google Spanner: Graph, SQL, Vector, and LLM](https://dgg32.medium.com/clinical-trial-search-with-google-spanner-graph-sql-vector-and-llm-all-in-one-query-5ada29f840cd)
    *   [Google Cloud Spanner Graph and ReGraph Tutorial](https://cambridge-intelligence.com/google-cloud-spanner-and-regraph/)
    *   [How to Build Social Graphs and Intelligent Recommendations (Video)](https://www.youtube.com/watch?v=SepF_1T133k)

---

## 8. Roadmap & Milestones

*   **Milestone 1 (End of Week 1):**
    *   Complete the Spanner schema design, including the `Feature` node.
    *   Implement the initial data ingestion pipeline for code and features.
*   **Milestone 2 (End of Week 2):**
    *   Implement the data ingestion pipeline for documents.
    *   Develop and test the `CodeQueryAgent` and `DocSearchAgent`.
    *   Initial multi-language ingestion tests (e.g., JavaScript with Tree-sitter).
    *   Set up MCP Toolbox server, define initial sources/tools for app DB and Spanner.
*   **Milestone 3 (End of Week 3):**
    *   Develop and test the `CodeModificationAgent` and `BuildAgent`.
    *   Develop the initial `BugAssistantAgent` for running tests.
    *   Integrate `CodeHealthAgent` with CI/CD pipeline.
    *   Integrate toolbox SDK into `AppDatabaseAgent` and `CodeQueryAgent`; test NL-to-SQL chaining.
    *   Develop agent testing framework and initial end-to-end tests.
*   **Milestone 4 (End of Week 4):**
    *   Develop the `RequirementsInterrogatorAgent` and `DeploymentAgent`.
    *   Develop the Gemini CLI with the new `ideate` command and other usability features.
    *   Integrate all agents with the Orchestrator.
    *   End-to-end testing.

---

## 9. Monitoring, Maintenance, and Iteration

Post-launch sustainability is key.

*   **Telemetry:** Use Cloud Operations Suite for agent usage metrics (e.g., query volume, success rates) and cost breakdowns.
*   **Update Mechanism:** Scheduled Cloud Function to check for dependency updates (e.g., via PyPI APIs) and propose upgrades as `ToDoItem` nodes.
*   **User Feedback Loop:** CLI command (`feedback`) to collect ratings on agent responses, storing them in Spanner for fine-tuning.
*   **Disaster Recovery:** Backup Spanner daily and test restores; define rollback procedures for faulty ingestions.
