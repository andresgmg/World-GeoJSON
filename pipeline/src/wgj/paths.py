"""Where things live.

The package sits at <repo>/pipeline/src/wgj, so the repository root is three
levels up. Only the data root can be redirected (`WGJ_DATA`): tests point it
at fixtures/data, and every "repository-relative" path the pipeline writes
into a manifest is computed against the data root's parent, so a fixture
manifest still says `data/earth/ABW/...` and validates against the schema.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SCHEMAS = REPO / "schemas"
CACHE = REPO / ".cache" / "sources"


def data_dir() -> Path:
    """The data tree: <repo>/data, or $WGJ_DATA."""
    override = os.environ.get("WGJ_DATA")
    return Path(override).resolve() if override else REPO / "data"


def data_base() -> Path:
    """What manifest paths are relative to: the parent of the data tree."""
    return data_dir().parent


def earth() -> Path:
    return data_dir() / "earth"


def rel(path: Path) -> str:
    """`data/earth/ABW/ABW_ADM0.geojson`-style path for manifests and messages.

    Falls back to the path as given for anything outside the data tree (a
    temporary copy under test, for instance) rather than raising.
    """
    for base in (data_base(), REPO):
        try:
            return path.resolve().relative_to(base).as_posix()
        except ValueError:
            continue
    return path.as_posix()


def country_dir(iso3: str, body: str = "earth") -> Path:
    return data_dir() / body / iso3


def country_dirs(data: Path | None = None) -> list[Path]:
    """Every data/<body>/<code>/ directory, in a platform-independent order."""
    root = data or data_dir()
    return sorted((p for p in root.glob("*/*") if p.is_dir()), key=lambda p: p.as_posix())
