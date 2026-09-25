"""The transport against a real (local) HTTP server: gzip, 404, timeouts."""

from __future__ import annotations

import gzip
import threading
from collections.abc import Iterator
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from geoworld import DownloadError, GeoWorld
from geoworld._http import fetch_bytes

BODY = b'{"schema_version": 1, "bodies": [], "totals": {}, "countries": []}'


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/data/index.json":
            accepts_gzip = "gzip" in self.headers.get("Accept-Encoding", "")
            payload = gzip.compress(BODY) if accepts_gzip else BODY
            self.send_response(200)
            if accepts_gzip:
                self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        else:
            self.send_error(404, "nope")

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="module")
def server() -> Iterator[str]:
    httpd = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{httpd.server_address[1]}"
    finally:
        httpd.shutdown()


def test_gzip_is_negotiated_and_decoded(server: str) -> None:
    assert fetch_bytes(f"{server}/data/index.json", timeout=5, user_agent="t") == BODY
    world = GeoWorld(base_url=server, cache=False)
    assert world.index()["countries"] == []


def test_http_error_carries_status(server: str) -> None:
    with pytest.raises(DownloadError) as info:
        fetch_bytes(f"{server}/missing.json", timeout=5, user_agent="t")
    assert info.value.status == 404
    assert "HTTP 404" in str(info.value)


def test_connection_error() -> None:
    with pytest.raises(DownloadError, match="could not fetch"):
        fetch_bytes("http://127.0.0.1:9/x", timeout=1, user_agent="t")
