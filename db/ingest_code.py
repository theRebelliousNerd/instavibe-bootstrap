#!/usr/bin/env python
# coding: utf-8

"""
This script handles the initial data ingestion of code and features into the Spanner knowledge graph.

It scans the codebase, parses the files to extract key structural information
(files, functions, classes), and populates the Spanner database with this data.
It also identifies and ingests feature definitions from a YAML file.

This script is designed to be run both as a one-time bootstrap and as part of a
CI/CD pipeline to keep the knowledge graph up-to-date with the latest code changes.
"""

import os
import yaml
import argparse
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

# --- Data Ingestion Logic ---

def ingest_features(db, features_file):
    """Ingests feature definitions from a YAML file into Spanner."""
    print(f"Ingesting features from {features_file}...")

    # --- Debugging Step: Check table schema ---
    try:
        with db.snapshot() as snapshot:
            results = snapshot.execute_sql(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'Features'"
            )
            print("Columns in Features table:")
            for row in results:
                print(row[0])
    except Exception as e:
        print(f"Error reading schema: {e}")
    # --- End Debugging Step ---

    with open(features_file, 'r') as f:
        features = yaml.safe_load(f)

    with db.batch() as batch:
        for feature in features.get('features', []):
            batch.insert(
                table='Features',
                columns=('feature_id', 'name', 'description'),
                values=[(feature['id'], feature['name'], feature.get('description', ''))]
            )
    print("Features ingested successfully.")

def ingest_code(db, codebase_path):
    """Scans the codebase, parses files, and ingests code structure into Spanner."""
    print(f"Ingesting code from {codebase_path}...")
    # This is a placeholder for the actual code parsing logic.
    # In a real implementation, this would use a library like `tree-sitter`
    # to build an AST and extract detailed information about functions, classes,
    # imports, and calls.

    # For this initial version, we will just ingest file information.
    with db.batch() as batch:
        for root, _, files in os.walk(codebase_path):
            for file in files:
                if file.endswith(('.py', '.js', '.java')):
                    file_path = os.path.join(root, file)
                    # In a real implementation, we would generate a stable UUID for the file.
                    file_id = os.path.abspath(file_path)
                    batch.insert(
                        table='Files',
                        columns=('file_id', 'path'),
                        values=[(file_id, file_path)]
                    )
    print("Code ingested successfully.")

# --- Main Execution ---

def main():
    """Main function to run the data ingestion script."""
    parser = argparse.ArgumentParser(description="Ingest code and features into Spanner.")
    parser.add_argument("--features", type=str, help="Path to the features YAML file.")
    parser.add_argument("--code", type=str, help="Path to the codebase directory.")
    args = parser.parse_args()

    if not INSTANCE_ID or not DATABASE_ID:
        print("Error: SPANNER_INSTANCE_ID and SPANNER_DATABASE_ID environment variables must be set.")
        return

    client = get_spanner_client()
    db = get_database(client)

    if args.features:
        ingest_features(db, args.features)

    if args.code:
        ingest_code(db, args.code)

if __name__ == "__main__":
    main()
