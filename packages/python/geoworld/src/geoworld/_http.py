"""Fetching bytes with the standard library only (``http(s)://`` and ``file://``)."""

from __future__ import annotations

import gzip
import urllib.error
import urllib.request

from .errors import DownloadError


def fetch_bytes(url: str, *, timeout: float, user_agent: str) -> bytes:
    """Return the body at ``url``; gzip is negotiated and decoded transparently."""
    request = urllib.request.Request(
        url, headers={"User-Agent": user_agent, "Accept-Encoding": "gzip"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body: bytes = response.read()
            if response.headers.get("Content-Encoding", "").lower() == "gzip":
                body = gzip.decompress(body)
            return body
    except urllib.error.HTTPError as exc:
        reason = exc.reason if isinstance(exc.reason, str) else str(exc)
        raise DownloadError(url, reason, exc.code) from exc
    except urllib.error.URLError as exc:
        raise DownloadError(url, str(exc.reason)) from exc
    except (OSError, ValueError) as exc:
        raise DownloadError(url, str(exc)) from exc
