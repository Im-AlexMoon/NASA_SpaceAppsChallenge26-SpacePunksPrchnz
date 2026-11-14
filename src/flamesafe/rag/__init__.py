"""F5 · RAG assistant: corpus build, hybrid index, retrieval, grounded answering with citations.

Design: docs/03_data_science/RAG_DESIGN.md. Two retrieval paths:
  1. documents (PSI metadata, abstracts, findings, model cards, physics docs);
  2. structured tools over gold tables (DuckDB) so numbers come from data, not from the LLM.
"""
