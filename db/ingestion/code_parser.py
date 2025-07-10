#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Code Parser: Parses source code into an Abstract Syntax Tree (AST)."""

import logging
from tree_sitter import Language, Parser

# --- Configuration ---
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# TODO: Add support for more languages
# You will need to download the grammar for each language and build the .so file.
# See https://github.com/tree-sitter/tree-sitter for more information.
PY_LANGUAGE = Language('build/my-languages.so', 'python')


# --- Helper Functions ---
def get_parser(language: str) -> Parser:
    """Returns a Tree-sitter parser for the given language."""
    parser = Parser()
    if language == "python":
        parser.set_language(PY_LANGUAGE)
    # TODO: Add cases for other languages
    return parser


# --- Main Parsing Logic ---
def parse_code(file_path: str, language: str):
    """Parses the code in the given file and returns the AST."""
    with open(file_path, "rb") as f:
        code = f.read()

    parser = get_parser(language)
    tree = parser.parse(code)

    # TODO: Traverse the AST and extract relevant information
    # (e.g., functions, classes, imports, calls)

    return tree


# --- Main Execution ---
if __name__ == "__main__":
    # This is for testing purposes
    # You will need to have a file named `test.py` in the same directory as this script.
    # with open("test.py", "w") as f:
    #     f.write("import os\n\ndef my_function():\n    print('Hello, world!')")

    # tree = parse_code("test.py", "python")
    # logger.info(f"AST: {tree.root_node.sexp()}")
    pass
