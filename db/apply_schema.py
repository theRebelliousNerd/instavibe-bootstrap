import os
from google.cloud import spanner


def apply_schema():
    """Applies the schema from schema.sql to the Spanner database."""

    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    instance_id = os.environ.get("SPANNER_INSTANCE_ID")
    database_id = os.environ.get("SPANNER_DATABASE_ID")

    if not all([project_id, instance_id, database_id]):
        print("Error: GOOGLE_CLOUD_PROJECT, SPANNER_INSTANCE_ID, and SPANNER_DATABASE_ID must be set.")
        return

    spanner_client = spanner.Client(project=project_id)
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    # Use an absolute path to the schema file
    schema_file_path = os.path.join(os.path.dirname(__file__), "schema.sql")

    with open(schema_file_path, "r") as f:
        schema_statements = f.read().split(";")

    # Filter out empty statements
    schema_statements = [s.strip() for s in schema_statements if s.strip()]

    print("Applying schema to the database...")
    for statement in schema_statements:
        try:
            print(f"Executing DDL statement: {statement}")
            operation = database.update_ddl([statement])
            operation.result()  # Wait for the operation to complete
            print("Statement executed successfully.")
        except Exception as e:
            print(f"Error executing DDL statement: {e}")
            # Decide if you want to stop on the first error or continue
            # return

    print("Schema applied successfully.")


if __name__ == "__main__":
    apply_schema()