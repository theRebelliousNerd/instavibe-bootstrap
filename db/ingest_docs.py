#!/usr/bin/env python
# coding: utf-8

"""
This script handles the ingestion of documents into the Spanner knowledge graph.

It reads a document, chunks it into smaller pieces, generates vector embeddings
for each chunk, and stores the document, chunks, and embeddings in Spanner.
It also links the document to a specified feature.
"""

import os
import argparse
import uuid
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

# --- Document Processing ---

def chunk_document(content, chunk_size=1000):
    """Chunks a document into smaller pieces."""
    return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]

def generate_embedding(text):
    """Generates a vector embedding for a given text. Placeholder function."""
    # In a real implementation, this would use a service like Vertex AI
    # to generate high-quality embeddings.
    print(f"Generating embedding for: {text[:50]}...")
    # Returning a dummy embedding for now.
    return [0.1] * 768

# --- Data Ingestion Logic ---

def ingest_document(db, doc_path, feature_name, doc_type="APIDocument"):
    """Ingests a single document into Spanner."""
    print(f"Ingesting document {doc_path} for feature {feature_name}...")

    with open(doc_path, 'r') as f:
        content = f.read()

    doc_id = str(uuid.uuid4())
    doc_title = os.path.basename(doc_path)

    # 1. Ingest the document metadata
    with db.batch() as batch:
        if doc_type == "APIDocument":
            batch.insert(
                table='APIDocuments',
                columns=('doc_id', 'path', 'title'),
                values=[(doc_id, doc_path, doc_title)]
            )
        elif doc_type == "Tutorial":
            batch.insert(
                table='Tutorials',
                columns=('tutorial_id', 'path', 'title'),
                values=[(doc_id, doc_path, doc_title)]
            )

    # 2. Chunk the document and ingest chunks with embeddings
    chunks = chunk_document(content)
    with db.batch() as batch:
        for chunk_content in chunks:
            chunk_id = str(uuid.uuid4())
            embedding = generate_embedding(chunk_content)
            batch.insert(
                table='DocChunks',
                columns=('chunk_id', 'document_id', 'content', 'embedding'),
                values=[(chunk_id, doc_id, chunk_content, embedding)]
            )
            batch.insert(
                table='HasChunk',
                columns=('has_chunk_id', 'document_id', 'chunk_id'),
                values=[(str(uuid.uuid4()), doc_id, chunk_id)]
            )

    # 3. Link the document to the feature
    with db.batch() as batch:
        # First, get the feature_id from the feature_name
        with db.snapshot() as snapshot:
            results = snapshot.execute_sql(
                f"SELECT feature_id FROM Features WHERE name = '{feature_name}'"
            )
            feature_id = [row[0] for row in results][0]

        if feature_id:
            batch.insert(
                table='DocumentsFeature',
                columns=('documents_feature_id', 'doc_id', 'doc_type', 'feature_id'),
                values=[(str(uuid.uuid4()), doc_id, doc_type, feature_id)]
            )

    print("Document ingested successfully.")

# --- Main Execution ---

def main():
    """Main function to run the document ingestion script."""
    parser = argparse.ArgumentParser(description="Ingest a document into Spanner.")
    parser.add_argument("--doc-path", required=True, type=str, help="Path to the document file.")
    parser.add_argument("--feature-name", required=True, type=str, help="Name of the feature to link the document to.")
    parser.add_argument("--doc-type", default="APIDocument", choices=["APIDocument", "Tutorial"], help="Type of the document.")
    args = parser.parse_args()

    if not INSTANCE_ID or not DATABASE_ID:
        print("Error: SPANNER_INSTANCE_ID and SPANNER_DATABASE_ID environment variables must be set.")
        return

    client = get_spanner_client()
    db = get_database(client)

    ingest_document(db, args.doc_path, args.feature_name, args.doc_type)

if __name__ == "__main__":
    main()
