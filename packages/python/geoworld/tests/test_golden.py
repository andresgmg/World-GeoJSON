"""The Python client must produce fixtures/expected/fixtures.json byte for byte."""

from __future__ import annotations

from goldens import EXPECTED, build, canonical

from geoworld import GeoWorld


def test_matches_golden(world_nocache: GeoWorld) -> None:
    expected = (EXPECTED / "fixtures.json").read_text(encoding="utf-8")
    assert canonical(build(world_nocache)) == expected, (
        "regenerate with: python packages/python/geoworld/tests/goldens.py"
    )
