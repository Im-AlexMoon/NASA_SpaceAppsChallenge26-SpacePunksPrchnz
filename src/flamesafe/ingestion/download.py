"""Manifest-driven downloader with budget guardrails (configs/sources.yaml::download_budget).

Task DE-06. Each file -> data/bronze/<PSI-ID>/<filename> + <filename>.meta.json
(source_url, retrieved_at, http_status, bytes, sha256). 404s are recorded, not hidden.
"""
