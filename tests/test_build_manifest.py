from __future__ import annotations

import json
from pathlib import Path

import build_manifest


def _manifest(d: Path) -> dict:
    return json.loads((d / "manifest.json").read_text("utf-8"))


def test_scan_matches_committed_manifest(abw: Path) -> None:
    manifest = _manifest(abw)
    (ds,) = manifest["datasets"]
    path = abw.parent.parent.parent / ds["path"]

    got = build_manifest.scan(path)
    assert got["features"] == ds["features"]
    assert got["bbox"] == ds["bbox"]
    assert got["geometry_types"] == ds["geometry_types"]
    assert got["properties"] == ds["properties"]
    assert build_manifest.sha256(path) == ds["sha256"]
    assert path.stat().st_size == ds["bytes"]


def test_describe_records_preview(abw: Path) -> None:
    manifest = _manifest(abw)
    (ds,) = manifest["datasets"]
    path = build_manifest.REPO / ds["path"]
    preview = build_manifest.REPO / ds["preview"]

    entry = build_manifest.describe(path, preview)
    assert entry["preview"] == ds["preview"]
    assert entry["preview_bytes"] == ds["preview_bytes"]


def test_build_datasets_reproduces_committed_manifest(brb: Path) -> None:
    manifest = _manifest(brb)
    prev = {ds["level"]: ds for ds in manifest["datasets"]}
    assert build_manifest.build_datasets(brb, prev) == manifest["datasets"]


def test_build_datasets_split_level(dom: Path) -> None:
    manifest = _manifest(dom)
    prev = {ds["level"]: ds for ds in manifest["datasets"]}
    datasets = {ds["level"]: ds for ds in build_manifest.build_datasets(dom, prev)}

    split = datasets["ADM2"]
    assert split["split_by"] == "ADM1"
    assert split["parts"], "expected per-ADM1 parts"
    assert split["features"] == sum(p["features"] for p in split["parts"])
    assert "adm1ISO" in {k for p in split["parts"] for k in p["properties"]}
    # Provenance written by build_data.py must survive a regeneration.
    for key in ("simplification", "license", "src_provider"):
        assert split[key] == prev["ADM2"][key]


def test_path_key_is_platform_independent() -> None:
    names = ["unassigned.geojson", "US-WY.geojson", "US-AK.geojson"]
    ordered = sorted((Path("ADM2") / n for n in names), key=build_manifest.path_key)
    # Bytewise: uppercase before lowercase, so `unassigned` is always last.
    assert [p.name for p in ordered] == ["US-AK.geojson", "US-WY.geojson", "unassigned.geojson"]


def test_level_patterns() -> None:
    assert build_manifest.LEVEL_FILE.match("CHL_ADM3")
    assert build_manifest.LEVEL_FILE.match("GLP_ADM4")
    assert build_manifest.LEVEL_FILE.match("MOON_QUAD")
    assert not build_manifest.LEVEL_FILE.match("CHL_ADM3.preview")
    assert build_manifest.LEVEL_DIR.match("ADM2")
    assert not build_manifest.LEVEL_DIR.match("preview")
