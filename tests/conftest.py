"""Shared fixtures.

Tests run against the real, small countries in data/earth/ (Aruba is 846
bytes; Barbados and the Dominican Republic add an ADM1 and a split level).
Anything not checked out — CI uses a sparse checkout — is skipped, never
failed, so the suite is usable from a partial clone.
"""

from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data" / "earth"


def country(code: str) -> Path:
    d = DATA / code
    if not (d / "manifest.json").exists():
        pytest.skip(f"data/earth/{code} is not checked out")
    return d


@pytest.fixture
def repo() -> Path:
    return REPO


@pytest.fixture
def abw() -> Path:
    """One ADM0 file, one preview, one manifest — the smallest country."""
    return country("ABW")


@pytest.fixture
def brb() -> Path:
    """ADM0 plus a whole-file ADM1."""
    return country("BRB")


@pytest.fixture
def dom() -> Path:
    """Has a split municipal level: ADM2/DO-XX.geojson parts."""
    return country("DOM")
