"""Offline HTTP fakes shared by ingestion tests."""

from __future__ import annotations

import json

from flamesafe.ingestion.psi_client import PSIClient

SETTINGS = {
    "base_url": "https://psi.example/ws/",
    "endpoints": {
        "search": "/repo/search?source=psi&type=investigation&size=200&from=0",
        "investigation": "/repo/investigations/{psi_id}",
        "download": "/studies/{psi_id}/download?file={filename}",
    },
    "request": {"timeout_s": 1, "retries": 3, "backoff_s": 0},
}


class FakeResponse:
    def __init__(self, status=200, body=b"", headers=None):
        self.status_code = status
        self.content = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.headers = headers or {}

    def json(self):
        return json.loads(self.content)

    @property
    def text(self):
        return self.content.decode()

    def iter_content(self, chunk):
        for i in range(0, len(self.content), chunk):
            yield self.content[i : i + chunk]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeSession:
    """Maps URL substrings to a list of responses (consumed in order, last one repeats).

    The longest matching key wins, so "/investigations/PSI-100" beats "/investigations/PSI-10".
    """

    def __init__(self, routes):
        self.routes = routes
        self.headers = {}
        self.calls: list[str] = []

    def get(self, url, **_):
        self.calls.append(url)
        matches = [k for k in self.routes if k in url]
        if not matches:
            return FakeResponse(404)
        responses = self.routes[max(matches, key=len)]
        return responses.pop(0) if len(responses) > 1 else responses[0]


def make_client(routes):
    session = FakeSession(routes)
    return PSIClient(session=session, settings=SETTINGS), session
