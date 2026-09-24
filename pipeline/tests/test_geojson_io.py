from __future__ import annotations

import json
from pathlib import Path

import pytest

from wgj import geojson_io


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-70, "-70"),
        (12.4, "12.4"),
        (12.577582, "12.577582"),
        (0.000001, "0.000001"),
        (0.00001, "0.00001"),  # json.dumps would write 1e-05
        (-0.0000001, "0"),
        (0.0, "0"),
    ],
)
def test_fmt_number(value: float, expected: str) -> None:
    assert geojson_io.fmt_number(value) == expected


def test_scan_and_sha256_match_the_manifest(abw: Path) -> None:
    manifest = json.loads((abw / "manifest.json").read_text("utf-8"))
    (ds,) = manifest["datasets"]
    path = abw / "ABW_ADM0.geojson"
    got = geojson_io.scan(path)
    assert got["features"] == ds["features"]
    assert got["bbox"] == ds["bbox"]
    assert got["geometry_types"] == ds["geometry_types"]
    assert got["properties"] == ds["properties"]
    assert geojson_io.sha256(path) == ds["sha256"]
    assert geojson_io.feature_count(path) == ds["features"]


def test_committed_files_are_canonical(brb: Path) -> None:
    for p in brb.glob("*.geojson"):
        features = geojson_io.load(p)
        assert p.read_bytes() == geojson_io.serialise(features), p.name
        assert json.loads(p.read_text("utf-8"))["bbox"] == geojson_io.bbox_of(features)
