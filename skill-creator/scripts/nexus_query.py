"""Nexus API client for skill-creator scripts.

Requires environment variables:
  NEXUS_API_URL   — base URL of the Nexus server (default: http://localhost:8080)
  NEXUS_API_TOKEN — Bearer token for authentication (required for /query calls)

Example:
  export NEXUS_API_URL=http://localhost:8080
  export NEXUS_API_TOKEN=your-token-here
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any

NEXUS_API_URL = os.environ.get("NEXUS_API_URL", "http://localhost:8080").rstrip("/")
NEXUS_API_TOKEN = os.environ.get("NEXUS_API_TOKEN", "")


class NexusAPIError(Exception):
    def __init__(self, status: int, body: str) -> None:
        self.status = status
        self.body = body
        super().__init__(f"Nexus API error {status}: {body[:200]}")


def _headers() -> dict[str, str]:
    h = {"Content-Type": "application/json"}
    if NEXUS_API_TOKEN:
        h["Authorization"] = f"Bearer {NEXUS_API_TOKEN}"
    return h


def query(
    prompt: str,
    session_id: str | None = None,
    execution_origin: str = "interactive",
    timeout: int = 120,
) -> dict[str, Any]:
    """Send a prompt to the Nexus /query endpoint and return the JSON response."""
    if not NEXUS_API_TOKEN:
        raise RuntimeError(
            "NEXUS_API_TOKEN is not set. Export it before running this script:\n"
            "  export NEXUS_API_TOKEN=<your-token>"
        )

    payload: dict[str, Any] = {
        "prompt": prompt,
        "execution_origin": execution_origin,
    }
    if session_id:
        payload["session_id"] = session_id

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{NEXUS_API_URL}/query",
        data=data,
        headers=_headers(),
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise NexusAPIError(e.code, body) from e


def query_text(prompt: str, session_id: str | None = None, timeout: int = 120) -> str:
    """Convenience wrapper: returns only the response text."""
    result = query(prompt, session_id=session_id, timeout=timeout)
    return result.get("response", "")
