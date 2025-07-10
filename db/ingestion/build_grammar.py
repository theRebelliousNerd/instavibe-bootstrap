from tree_sitter import Language

Language.build_library(
  # Store the library in the `build` directory
  'db/ingestion/my-languages.so',

  # Include one or more languages
  [
    'db/ingestion/tree-sitter-python'
  ]
)