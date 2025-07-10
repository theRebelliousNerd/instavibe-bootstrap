import os
from google.cloud import spanner
from apply_schema import apply_schema

def get_db():
    """Gets the Spanner database instance."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    instance_id = os.environ.get("SPANNER_INSTANCE_ID")
    database_id = os.environ.get("SPANNER_DATABASE_ID")

    if not all([project_id, instance_id, database_id]):
        raise ValueError("GOOGLE_CLOUD_PROJECT, SPANNER_INSTANCE_ID, and SPANNER_DATABASE_ID must be set.")

    spanner_client = spanner.Client(project=project_id)
    instance = spanner_client.instance(instance_id)
    return instance.database(database_id)

def get_schema_items(db, query):
    """Fetches schema item names from the information schema."""
    items = []
    try:
        with db.snapshot() as snapshot:
            results = snapshot.execute_sql(query)
            for row in results:
                items.append(row[0])
    except Exception as e:
        print(f"Warning: Could not fetch schema items with query '{query}': {e}")
    return items

def reset_schema():
    """Drops all foreign keys, indexes, and tables, then reapplies the schema."""
    db = get_db()
    ddl_statements = []

    # 1. Get all Foreign Keys and create DROP statements
    print("Fetching foreign key constraints...")
    fk_query = "SELECT 'ALTER TABLE ' || t.TABLE_NAME || ' DROP CONSTRAINT ' || kcu.CONSTRAINT_NAME FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS AS t JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE AS kcu ON t.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME WHERE t.CONSTRAINT_TYPE = 'FOREIGN KEY' AND t.TABLE_CATALOG = ''"
    drop_fk_statements = get_schema_items(db, fk_query)
    ddl_statements.extend(drop_fk_statements)

    # 2. Get all Indexes and create DROP statements
    print("Fetching indexes...")
    indexes_query = "SELECT 'DROP INDEX ' || INDEX_NAME FROM INFORMATION_SCHEMA.INDEXES WHERE INDEX_TYPE != 'PRIMARY_KEY' AND TABLE_CATALOG = ''"
    drop_index_statements = get_schema_items(db, indexes_query)
    ddl_statements.extend(drop_index_statements)

    # 3. Get all Tables and create DROP statements
    print("Fetching tables...")
    tables_query = "SELECT 'DROP TABLE ' || TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_CATALOG = ''"
    drop_table_statements = get_schema_items(db, tables_query)
    ddl_statements.extend(drop_table_statements)

    if ddl_statements:
        print("\nExecuting DROP statements...")
        try:
            operation = db.update_ddl(ddl_statements)
            operation.result(timeout=300)  # Wait for completion
            print("All existing indexes and tables dropped successfully.")
        except Exception as e:
            print(f"An error occurred while dropping items: {e}")
            print("Attempting to proceed with schema creation anyway...")

    # 4. Re-apply the schema
    print("\nApplying fresh schema...")
    apply_schema()

if __name__ == "__main__":
    reset_schema()
