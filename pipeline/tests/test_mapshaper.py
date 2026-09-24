from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from wgj import mapshaper, paths


def test_helpers_work_without_node(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(mapshaper, "REPO", tmp_path)  # no node_modules here
    monkeypatch.setattr(mapshaper.shutil, "which", lambda _name: None)
    monkeypatch.setattr(mapshaper, "_MAPSHAPER", None)
    assert mapshaper.js_lookup({"a": "b", "c": "d"}) == "{'a':'b','c':'d'}"
    assert mapshaper.js_expr({"x": "1", "y": "'two'"}) == "x=1, y='two'"
    with pytest.raises(mapshaper.MapshaperNotFound, match="mapshaper not found"):
        mapshaper.run_mapshaper(["-version"])


@pytest.mark.mapshaper
def test_mapshaper_is_resolvable() -> None:
    if shutil.which("node") is None or not (paths.REPO / "node_modules" / "mapshaper").exists():
        pytest.skip("node + mapshaper not installed (npm ci)")
    mapshaper.run_mapshaper(["-version"])
