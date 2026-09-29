from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from wgj import paths, previews


def test_level_inputs_prefer_the_combined_file_and_sort_parts(dom: Path, brb: Path) -> None:
    assert list(previews.level_inputs(brb)) == ["ADM0", "ADM1"]
    inputs = previews.level_inputs(dom)
    assert [p.name for p in inputs["ADM2"]] == ["DO-01.geojson", "DO-02.geojson"]
    assert inputs["ADM1"] == [dom / "DOM_ADM1.geojson"]


@pytest.mark.mapshaper
def test_previews_reproduce_byte_for_byte(data_copy: Path) -> None:
    if shutil.which("node") is None or not (paths.REPO / "node_modules" / "mapshaper").exists():
        pytest.skip("node + mapshaper not installed (npm ci)")
    for code in ("ABW", "BRB"):
        d = data_copy / "earth" / code
        before = {p.name: p.read_bytes() for p in (d / "preview").glob("*.geojson")}
        lines = previews.preview_country(d)
        assert len(lines) == len(before)
        after = {p.name: p.read_bytes() for p in (d / "preview").glob("*.geojson")}
        assert after == before, code


def test_a_level_too_big_for_any_preview_ships_without_one(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """At the coarsest percentage and still over the hard limit: no file, no abort."""
    dest = tmp_path / "XXX_ADM5.preview.geojson"
    tries: list[float] = []

    def fake_write(inputs: list[Path], out: Path, pct: float) -> int:
        tries.append(pct)
        out.write_text('{"type":"FeatureCollection","features":[]}')
        return previews.HARD_LIMIT + 1

    monkeypatch.setattr(previews, "_write", fake_write)
    monkeypatch.setattr(previews, "load", lambda path: [])
    assert previews.build_preview([tmp_path / "in.geojson"], dest, 0) is None
    assert not dest.exists()
    assert tries[-1] == previews.MIN_PERCENTAGE
