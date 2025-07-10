-- Spanner Schema for AI Developer Assistant Knowledge Graph

-- Node Tables

CREATE TABLE Files (
    file_id STRING(36) NOT NULL,
    path STRING(MAX) NOT NULL,
    content STRING(MAX),
    language STRING(255),
) PRIMARY KEY (file_id);

CREATE UNIQUE INDEX Files_ByPath ON Files(path);

CREATE TABLE Functions (
    function_id STRING(36) NOT NULL,
    file_id STRING(36) NOT NULL,
    name STRING(MAX) NOT NULL,
    signature STRING(MAX),
    start_line INT64,
    end_line INT64,
    CONSTRAINT FK_FunctionFile FOREIGN KEY (file_id) REFERENCES Files (file_id)
) PRIMARY KEY (function_id);

CREATE TABLE Classes (
    class_id STRING(36) NOT NULL,
    file_id STRING(36) NOT NULL,
    name STRING(MAX) NOT NULL,
    start_line INT64,
    end_line INT64,
    CONSTRAINT FK_ClassFile FOREIGN KEY (file_id) REFERENCES Files (file_id)
) PRIMARY KEY (class_id);

CREATE TABLE Features (
    feature_id STRING(36) NOT NULL,
    name STRING(MAX) NOT NULL,
    description STRING(MAX),
) PRIMARY KEY (feature_id);

CREATE UNIQUE INDEX Features_ByName ON Features(name);

CREATE TABLE APIDocuments (
    doc_id STRING(36) NOT NULL,
    path STRING(MAX) NOT NULL,
    title STRING(MAX),
) PRIMARY KEY (doc_id);

CREATE UNIQUE INDEX APIDocuments_ByPath ON APIDocuments(path);

CREATE TABLE Tutorials (
    tutorial_id STRING(36) NOT NULL,
    path STRING(MAX) NOT NULL,
    title STRING(MAX),
) PRIMARY KEY (tutorial_id);

CREATE UNIQUE INDEX Tutorials_ByPath ON Tutorials(path);

CREATE TABLE ToDoItems (
    todo_id STRING(36) NOT NULL,
    description STRING(MAX) NOT NULL,
    status STRING(50),
) PRIMARY KEY (todo_id);

CREATE TABLE DocChunks (
    chunk_id STRING(36) NOT NULL,
    document_id STRING(36) NOT NULL, -- Can be from APIDocuments or Tutorials
    content STRING(MAX),
    embedding ARRAY<FLOAT64>,
) PRIMARY KEY (chunk_id);

CREATE TABLE CodeIssues (
    issue_id STRING(36) NOT NULL,
    type STRING(255) NOT NULL,
    description STRING(MAX),
    priority_score FLOAT64,
) PRIMARY KEY (issue_id);

CREATE TABLE WebArticles (
    article_id STRING(36) NOT NULL,
    url STRING(MAX) NOT NULL,
    title STRING(MAX),
) PRIMARY KEY (article_id);

CREATE UNIQUE INDEX WebArticles_ByUrl ON WebArticles(url);

CREATE TABLE Tables (
    table_id STRING(36) NOT NULL,
    name STRING(MAX) NOT NULL,
    schema_name STRING(MAX),
) PRIMARY KEY (table_id);

CREATE UNIQUE INDEX Tables_ByName ON Tables(name);

CREATE TABLE Columns (
    column_id STRING(36) NOT NULL,
    table_id STRING(36) NOT NULL,
    name STRING(MAX) NOT NULL,
    data_type STRING(MAX),
    CONSTRAINT FK_ColumnTable FOREIGN KEY (table_id) REFERENCES Tables (table_id)
) PRIMARY KEY (column_id);


-- Edge Tables (Bitemporal)

CREATE TABLE Imports (
    import_id STRING(36) NOT NULL,
    importer_file_id STRING(36) NOT NULL,
    imported_file_id STRING(36) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    CONSTRAINT FK_ImporterFile FOREIGN KEY (importer_file_id) REFERENCES Files (file_id),
    CONSTRAINT FK_ImportedFile FOREIGN KEY (imported_file_id) REFERENCES Files (file_id)
) PRIMARY KEY (import_id);

CREATE TABLE Calls (
    call_id STRING(36) NOT NULL,
    caller_function_id STRING(36) NOT NULL,
    callee_function_id STRING(36) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    CONSTRAINT FK_CallerFunction FOREIGN KEY (caller_function_id) REFERENCES Functions (function_id),
    CONSTRAINT FK_CalleeFunction FOREIGN KEY (callee_function_id) REFERENCES Functions (function_id)
) PRIMARY KEY (call_id);

CREATE TABLE Implements (
    implement_id STRING(36) NOT NULL,
    class_id STRING(36) NOT NULL,
    interface_id STRING(36) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    CONSTRAINT FK_ImplClass FOREIGN KEY (class_id) REFERENCES Classes (class_id),
    CONSTRAINT FK_ImplInterface FOREIGN KEY (interface_id) REFERENCES Classes (class_id)
) PRIMARY KEY (implement_id);

CREATE TABLE References (
    reference_id STRING(36) NOT NULL,
    source_node_id STRING(36) NOT NULL,
    source_node_type STRING(50) NOT NULL,
    target_node_id STRING(36) NOT NULL,
    target_node_type STRING(50) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
) PRIMARY KEY (reference_id);

CREATE TABLE HasIssue (
    has_issue_id STRING(36) NOT NULL,
    node_id STRING(36) NOT NULL,
    node_type STRING(50) NOT NULL,
    issue_id STRING(36) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    CONSTRAINT FK_Issue FOREIGN KEY (issue_id) REFERENCES CodeIssues (issue_id)
) PRIMARY KEY (has_issue_id);

CREATE TABLE ImplementsFeature (
    implements_feature_id STRING(36) NOT NULL,
    node_id STRING(36) NOT NULL,
    node_type STRING(50) NOT NULL,
    feature_id STRING(36) NOT NULL,
    valid_from_commit STRING(40),
    valid_to_commit STRING(40),
    branch_name STRING(255),
    CONSTRAINT FK_Feature FOREIGN KEY (feature_id) REFERENCES Features (feature_id)
) PRIMARY KEY (implements_feature_id);


-- Non-Bitemporal Edge Tables

CREATE TABLE HasChunk (
    has_chunk_id STRING(36) NOT NULL,
    document_id STRING(36) NOT NULL,
    chunk_id STRING(36) NOT NULL,
    CONSTRAINT FK_Chunk FOREIGN KEY (chunk_id) REFERENCES DocChunks (chunk_id)
) PRIMARY KEY (has_chunk_id);

CREATE TABLE DocumentsFeature (
    documents_feature_id STRING(36) NOT NULL,
    doc_id STRING(36) NOT NULL,
    doc_type STRING(50) NOT NULL, -- 'APIDocument' or 'Tutorial'
    feature_id STRING(36) NOT NULL,
    CONSTRAINT FK_DocFeature FOREIGN KEY (feature_id) REFERENCES Features (feature_id)
) PRIMARY KEY (documents_feature_id);

CREATE TABLE HasColumn (
    has_column_id STRING(36) NOT NULL,
    table_id STRING(36) NOT NULL,
    column_id STRING(36) NOT NULL,
    CONSTRAINT FK_Table FOREIGN KEY (table_id) REFERENCES Tables (table_id),
    CONSTRAINT FK_Column FOREIGN KEY (column_id) REFERENCES Columns (column_id)
) PRIMARY KEY (has_column_id);