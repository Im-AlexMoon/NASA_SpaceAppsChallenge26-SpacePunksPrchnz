"""Thin, retrying client for the public PSI API (no key needed).

Endpoints (verify + log in docs/02_data_engineering/DATA_SOURCES.md):
  search        GET {base}/repo/search?source=psi&type=investigation&size=200&from=0
  investigation GET {base}/repo/investigations/{psi_id}
  download      GET {base}/studies/{psi_id}/download?file={url-encoded filename}

Task DE-02. Rules: never invent counts; store raw JSON responses verbatim in bronze.
"""
