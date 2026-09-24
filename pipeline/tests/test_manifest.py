from __future__ import annotations

import json
from pathlib import Path

from wgj import manifest


def _manifest(d: Path) -> dict:
    return json.loads((d / "manifest.json").read_text("utf-8"))


def test_build_datasets_reproduces_the_fixture_manifest(brb: Path) -> None:
    m = _manifest(brb)
    prev = {ds["level"]: ds for ds in m["datasets"]}
    assert manifest.build_datasets(brb, prev) == m["datasets"]


def test_parts_only_level(dom: Path) -> None:
    m = _manifest(dom)
    prev = {ds["level"]: ds for ds in m["datasets"]}
    datasets = {ds["level"]: ds for ds in manifest.build_datasets(dom, prev)}
    adm2 = datasets["ADM2"]
    assert adm2["split_by"] == "ADM1"
    assert [p["code"] for p in adm2["parts"]] == ["DO-01", "DO-02"]
    assert "path" not in adm2, "no combined file in the fixture"
    assert adm2["features"] == sum(p["features"] for p in adm2["parts"])
    assert "adm1ISO" in adm2["properties"] and "parentID" in adm2["properties"]
    for key in ("simplification", "license", "src_provider"):
        assert adm2[key] == prev["ADM2"][key]


def test_paths_are_relative_to_the_data_base(abw: Path) -> None:
    entry = manifest.describe(
        abw / "ABW_ADM0.geojson", abw / "preview" / "ABW_ADM0.preview.geojson"
    )
    assert entry["path"] == "data/earth/ABW/ABW_ADM0.geojson"
    assert entry["preview"] == "data/earth/ABW/preview/ABW_ADM0.preview.geojson"


def test_path_key_is_platform_independent() -> None:
    names = ["unassigned.geojson", "US-WY.geojson", "US-AK.geojson"]
    ordered = sorted((Path("ADM2") / n for n in names), key=manifest.path_key)
    assert [p.name for p in ordered] == ["US-AK.geojson", "US-WY.geojson", "unassigned.geojson"]
