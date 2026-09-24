from __future__ import annotations

from pathlib import Path

import pytest

from geoworld import GeoWorld

REPO = Path(__file__).resolve().parents[4]
FIXTURES = REPO / "fixtures"


@pytest.fixture(scope="session")
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def world(tmp_path: Path) -> GeoWorld:
    """A client over the committed fixtures, caching into a fresh temp dir."""
    return GeoWorld(base_url=FIXTURES.as_uri(), cache_dir=tmp_path / "cache")


@pytest.fixture
def world_nocache() -> GeoWorld:
    return GeoWorld(base_url=FIXTURES.as_uri(), cache=False)
