"""HTTP fetching with browser-like headers and retry/backoff.

Several university sites return 403/404 to a bare client but serve normally to a
realistic browser User-Agent, so we always send full browser headers.
"""

from __future__ import annotations

import time

import requests

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
}


class FetchError(RuntimeError):
    """Raised when a URL cannot be fetched successfully."""


def fetch(url: str, *, timeout: int = 30, retries: int = 4) -> str:
    """GET ``url`` and return the response text, retrying with backoff.

    Raises :class:`FetchError` on a non-200 response or repeated failure.
    """
    return fetch_bytes(url, timeout=timeout, retries=retries).decode("utf-8", errors="replace")


def fetch_bytes(url: str, *, timeout: int = 30, retries: int = 4) -> bytes:
    """GET ``url`` and return raw response bytes, retrying with backoff."""
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout)
            if resp.status_code == 200:
                return resp.content
            last_exc = FetchError(f"HTTP {resp.status_code} for {url}")
        except requests.RequestException as exc:  # network-level failure
            last_exc = exc
        if attempt < retries - 1:
            time.sleep(2 ** (attempt + 1))  # 2s, 4s, 8s
    raise FetchError(f"Failed to fetch {url}: {last_exc}")
