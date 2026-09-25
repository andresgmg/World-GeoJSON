"""On-disk cache of downloaded files, keyed by data version and repository path."""

from __future__ import annotations

import contextlib
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

# Paths as the index writes them: the index itself, a country manifest or a
# .geojson under data/{body}/{ISO3}/. Anchored and without ".." so a hostile
# index cannot escape the cache root.
SAFE_PATH = re.compile(
    r"^data/(?:index\.json|[a-z]+/[A-Z]{3}/(?:manifest\.json|(?:[A-Za-z0-9_\-]+/)*[A-Za-z0-9_.\-]+\.geojson))$"
)


def default_cache_dir() -> Path:
    """The platform's cache location for ``geoworld``.

    ``$GEOWORLD_CACHE`` wins; then ``%LOCALAPPDATA%`` on Windows,
    ``~/Library/Caches`` on macOS and ``$XDG_CACHE_HOME`` (default ``~/.cache``)
    elsewhere.
    """
    override = os.environ.get("GEOWORLD_CACHE")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
    elif sys.platform == "darwin":
        base = str(Path.home() / "Library" / "Caches")
    else:
        base = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(base) / "geoworld"


def is_safe_path(path: str) -> bool:
    return bool(SAFE_PATH.match(path)) and ".." not in path.split("/")


class DiskCache:
    """Files stored as ``<root>/<version>/<path>``; writes are atomic."""

    def __init__(self, root: Path, version: str) -> None:
        self.root = Path(root)
        self.version = version

    @property
    def dir(self) -> Path:
        return self.root / self.version

    def path_for(self, path: str) -> Path:
        if not is_safe_path(path):
            raise ValueError(f"refusing to cache an unexpected path: {path!r}")
        return self.dir / Path(*path.split("/"))

    def get(self, path: str) -> bytes | None:
        try:
            return self.path_for(path).read_bytes()
        except FileNotFoundError:
            return None

    def put(self, path: str, data: bytes) -> None:
        target = self.path_for(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=target.parent)
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
            os.replace(tmp, target)
        except BaseException:
            with contextlib.suppress(OSError):
                os.unlink(tmp)
            raise

    def delete(self, path: str) -> None:
        with contextlib.suppress(FileNotFoundError):
            self.path_for(path).unlink()

    def clear(self) -> None:
        """Remove everything cached for this data version."""
        shutil.rmtree(self.dir, ignore_errors=True)
