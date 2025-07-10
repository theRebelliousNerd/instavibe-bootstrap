#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Document Parser: Parses documents (e.g., Markdown, text files)."""

import logging

# --- Configuration ---
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --- Main Parsing Logic ---
def parse_document(file_path: str):
    """Parses the document in the given file and returns the content."""
    with open(file_path, "r") as f:
        content = f.read()

    # TODO: Implement more sophisticated parsing for different document types
    # (e.g., chunking for vector search, extracting metadata)

    return content


# --- Main Execution ---
if __name__ == "__main__":
    # This is for testing purposes
    # You will need to have a file named `test.md` in the same directory as this script.
    # with open("test.md", "w") as f:
    #     f.write("# This is a test document.")

    # content = parse_document("test.md")
    # logger.info(f"Content: {content}")
    pass