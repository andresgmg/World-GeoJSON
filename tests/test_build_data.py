from __future__ import annotations

from pathlib import Path

import pytest

import build_data


def test_importable_and_helpers_work_without_node(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The pure helpers must be usable on a machine with no mapshaper."""
    monkeypatch.setattr(build_data, "REPO", tmp_path)  # no node_modules here
    monkeypatch.setattr(build_data.shutil, "which", lambda _name: None)
    monkeypatch.setattr(build_data, "_MAPSHAPER", None)

    assert build_data.slug("Región de Ñuble") == "region-de-nuble"
    assert build_data.slug("Libertador General Bernardo O'Higgins") == (
        "libertador-general-bernardo-o-higgins"
    )
    assert build_data.js_lookup({"a": "b", "c": "d"}) == "{'a':'b','c':'d'}"
    assert build_data.js_expr({"x": "1", "y": "'two'"}) == "x=1, y='two'"

    with pytest.raises(SystemExit, match="mapshaper not found"):
        build_data.run_mapshaper(["-version"])


def test_registry_has_every_field_the_pipeline_reads() -> None:
    for iso3, entry in build_data.COUNTRIES.items():
        assert len(iso3) == 3 and iso3.isupper(), iso3
        assert entry["source"] in {*build_data.BUILDERS, "natural-earth"}, iso3
        assert set(entry["name"]) == {"en", "es"}, iso3
        assert entry["m49_region"] in build_data.CONTINENTS["americas"], iso3
        assert entry.get("municipal_level") in {None, "ADM1", "ADM2", "ADM3", "ADM4"}, iso3


def test_source_info_covers_every_registry_source() -> None:
    assert {e["source"] for e in build_data.COUNTRIES.values()} <= set(build_data.SOURCE_INFO)


@pytest.mark.mapshaper
def test_mapshaper_is_resolvable() -> None:
    """Only meaningful after `npm ci`; skipped elsewhere."""
    if build_data.shutil.which("node") is None:
        pytest.skip("node not installed")
    if not (build_data.REPO / "node_modules" / "mapshaper").exists():
        pytest.skip("mapshaper not installed (npm ci)")
    build_data.run_mapshaper(["-version"])
