"""Shared fixtures.

The suite runs against fixtures/data — three small territories copied from
the real tree (Aruba: one ADM0 file; Barbados: ADM0 + ADM1; the Dominican
Republic reduced to ADM0, ADM1 and two ADM2 parts, no combined ADM2 file and
no ADM2 preview) plus the index built from them. `WGJ_DATA` points the
package at it for the whole session, so nothing depends on the real data
being checked out. Tests that want the real tree ask for `real_data` and are
skipped when it is absent (CI uses a sparse checkout).
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "fixtures" / "data"
REAL = REPO / "data"


@pytest.fixture(autouse=True, scope="session")
def _use_fixtures() -> None:
    os.environ["WGJ_DATA"] = str(FIXTURES)


@pytest.fixture
def repo() -> Path:
    return REPO


@pytest.fixture
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def abw() -> Path:
    return FIXTURES / "earth" / "ABW"


@pytest.fixture
def brb() -> Path:
    return FIXTURES / "earth" / "BRB"


@pytest.fixture
def dom() -> Path:
    return FIXTURES / "earth" / "DOM"


@pytest.fixture
def real_data() -> Path:
    """The full data tree, or skip."""
    # CI's sparse checkout keeps every manifest but only three countries'
    # files, so test for a full-resolution file, not a manifest.
    if not (REAL / "earth" / "CHL" / "CHL_ADM1.geojson").exists():
        pytest.skip("data/ is not fully checked out")
    return REAL


@pytest.fixture
def data_copy(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A writable copy of the fixture tree, with WGJ_DATA pointing at it."""
    dest = tmp_path / "data"
    shutil.copytree(FIXTURES, dest)
    monkeypatch.setenv("WGJ_DATA", str(dest))
    return dest
