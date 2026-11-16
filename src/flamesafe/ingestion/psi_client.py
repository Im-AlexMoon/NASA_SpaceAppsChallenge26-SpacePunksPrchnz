"""Thin, retrying client for the public PSI API (no key needed).

Endpoints (verified 2026-11-14, see docs/02_data_engineering/DATA_SOURCES.md):
  search        GET {base}/repo/search?source=psi&type=investigation&size=200&from=0
  investigation GET {base}/repo/investigations/{psi_id}
  download      GET {base}/studies/{psi_id}/download?file={url-encoded filename}
                    (&redirect=false -> returns a presigned S3 URL as plain text)

Observed behaviour worth knowing:
  * search returns Elasticsearch-style JSON: hits.hits[]._source with "Accession", "Research Area"...
  * an unknown investigation id returns HTTP 403 (not 404);
  * an unknown file name returns HTTP 404;
  * presigned URLs embed temporary AWS credentials -> never log or persist them (use `redact_url`).

Rules: never invent counts; callers store raw JSON responses verbatim in bronze.
"""

from __future__ import annotations

import hashlib
import re
import urllib.parse
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from flamesafe import config

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}
_SECRET_QUERY = re.compile(
    r"(AWSAccessKeyId|Signature|x-amz-security-token|X-Amz-[A-Za-z-]+)=[^&]*", re.IGNORECASE
)


class PSIError(RuntimeError):
    """Non-retryable API error carrying the HTTP status."""

    def __init__(self, status: int, url: str, message: str = "") -> None:
        self.status = status
        self.url = redact_url(url)
        super().__init__(f"PSI HTTP {status} for {self.url} {message}".strip())


def redact_url(url: str) -> str:
    """Strip temporary credentials from presigned S3 URLs before logging/persisting."""
    return _SECRET_QUERY.sub(lambda m: f"{m.group(1)}=REDACTED", url)


def _is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, (requests.ConnectionError, requests.Timeout)):
        return True
    return isinstance(exc, PSIError) and exc.status in _RETRYABLE_STATUS


@dataclass
class DownloadResult:
    psi_id: str
    file_name: str
    http_status: int
    bytes: int
    sha256: str
    content_type: str


class PSIClient:
    def __init__(self, session: requests.Session | None = None, settings: dict | None = None):
        cfg = settings or config.load("sources")["psi"]
        self.base_url: str = cfg["base_url"].rstrip("/")
        self.endpoints: dict[str, str] = cfg["endpoints"]
        req = cfg.get("request", {})
        self.timeout: float = req.get("timeout_s", 60)
        self.retries: int = req.get("retries", 4)
        self.backoff: float = req.get("backoff_s", 2)
        self.session = session or requests.Session()
        self.session.headers.setdefault("User-Agent", req.get("user_agent", "flamesafe/0.1"))

    # ------------------------------------------------------------------ urls
    def url(self, endpoint: str, **params: str) -> str:
        quoted = {k: urllib.parse.quote(str(v), safe="") for k, v in params.items()}
        return self.base_url + self.endpoints[endpoint].format(**quoted)

    # ------------------------------------------------------------- transport
    def _get(self, url: str, *, stream: bool = False) -> requests.Response:
        @retry(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self.retries),
            wait=wait_exponential(multiplier=self.backoff, max=30),
            reraise=True,
        )
        def _call() -> requests.Response:
            resp = self.session.get(url, timeout=self.timeout, stream=stream, allow_redirects=True)
            if resp.status_code != 200:
                status = resp.status_code
                resp.close()
                raise PSIError(status, url)
            return resp

        return _call()

    def get_raw(self, url: str) -> bytes:
        """Response body exactly as served (for verbatim bronze storage)."""
        return self._get(url).content

    # ------------------------------------------------------------------- api
    def search(self) -> dict[str, Any]:
        """Raw search response (all investigations, every research area)."""
        return self._get(self.url("search")).json()

    def search_pages(self, first: dict[str, Any], load_page=None) -> Iterator[tuple[int, dict[str, Any]]]:
        """Preserve raw page boundaries while walking the repository's reported total."""
        load_page = load_page or (lambda offset, url: self._get(url).json())
        page = first
        offset = 0
        total = page.get("hits", {}).get("total")
        if isinstance(total, dict):
            total = total.get("value")
        while True:
            yield offset, page
            count = len(page.get("hits", {}).get("hits", []))
            if total is None or offset + count >= total:
                return
            if not count:
                raise ValueError("PSI search ended before its reported total.")
            offset += count
            url = re.sub(r"([?&]from=)\d+", lambda match, offset=offset: match[1] + str(offset), self.url("search"))
            if url == self.url("search"):
                raise ValueError("PSI search endpoint does not expose a page offset.")
            page = load_page(offset, url)

    @staticmethod
    def iter_sources(search_response: dict[str, Any]) -> Iterator[dict[str, Any]]:
        for hit in search_response.get("hits", {}).get("hits", []):
            yield hit.get("_source", {})

    def list_investigations(self, research_area: str | None = None) -> list[dict[str, Any]]:
        """Search hits' `_source` dicts, optionally filtered by exact Research Area."""
        sources = list({row['Accession']: row for _, page in self.search_pages(self.search())
                        for row in self.iter_sources(page) if row.get('Accession')}.values())
        if research_area:
            sources = [s for s in sources if s.get("Research Area") == research_area]
        return sorted(sources, key=lambda s: _accession_key(s.get("Accession", "")))

    def investigation(self, psi_id: str) -> dict[str, Any]:
        """Raw detail record (metadata, `added`, `experimentalTable`, `publications`, ...)."""
        return self._get(self.url("investigation", psi_id=psi_id)).json()

    def presigned_url(self, psi_id: str, file_name: str) -> str:
        """Presigned S3 URL (contains temporary credentials: do not persist unredacted)."""
        url = self.url("download", psi_id=psi_id, filename=file_name) + "&redirect=false"
        return self._get(url).text.strip()

    def download(
        self, psi_id: str, file_name: str, dest: Path, chunk: int = 1 << 20, *,
        expected_bytes: int | None = None, max_bytes: int | None = None,
    ) -> DownloadResult:
        """Stream and verify a file before replacing the destination."""
        url = self.url("download", psi_id=psi_id, filename=file_name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        tmp = dest.with_suffix(dest.suffix + ".part")
        digest, size = hashlib.sha256(), 0
        allowed = min((limit for limit in (expected_bytes, max_bytes) if limit is not None), default=None)
        try:
            with self._get(url, stream=True) as resp, open(tmp, "wb") as fh:
                ctype = resp.headers.get("Content-Type", "")
                for block in resp.iter_content(chunk):
                    size += len(block)
                    if allowed is not None and size > allowed:
                        raise ValueError(f"Download exceeded the allowed {allowed} bytes.")
                    fh.write(block)
                    digest.update(block)
            if expected_bytes is not None and size != expected_bytes:
                raise ValueError(f"Downloaded {size} bytes; expected {expected_bytes}.")
            tmp.replace(dest)
        finally:
            tmp.unlink(missing_ok=True)
        return DownloadResult(psi_id, file_name, 200, size, digest.hexdigest(), ctype)

    def probe(self, psi_id: str, file_name: str) -> int:
        """HTTP status of the download endpoint without fetching the body (0 = network error)."""
        try:
            url = self.url("download", psi_id=psi_id, filename=file_name)
            with self._get(url, stream=True):
                return 200
        except PSIError as exc:
            return exc.status
        except requests.RequestException:
            return 0


def _accession_key(acc: str) -> tuple[int, str]:
    m = re.search(r"(\d+)", acc)
    return (int(m.group(1)) if m else 10**9, acc)
