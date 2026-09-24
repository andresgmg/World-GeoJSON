from __future__ import annotations

from pathlib import Path

import pytest

from wgj import index, schema


def test_index_is_deterministic_and_consistent() -> None:
    first, second = index.build_index(), index.build_index()
    assert index.render(first) == index.render(second)
    countries = first["countries"]
    assert [c["iso_a3"] for c in countries] == ["ABW", "BRB", "DOM"]
    datasets = [d for c in countries for d in c["datasets"]]
    assert first["totals"] == {
        "countries": 3,
        "datasets": len(datasets),
        "features": sum(d["features"] for d in datasets),
        "bytes": sum(d.get("bytes", 0) for d in datasets),
    }
    dom = countries[2]
    assert dom["levels"] == ["ADM0", "ADM1", "ADM2"]
    assert dom["municipal_level"] == "ADM2"
    assert dom["manifest"] == "data/earth/DOM/manifest.json"
    assert dom["terms"]["adm1"]["en"]


def test_index_validates_against_its_schema() -> None:
    errors = list(schema.validator("index.schema.json").iter_errors(index.build_index()))
    assert errors == [], [schema.describe_error(e) for e in errors[:5]]


def test_fixture_index_is_fresh(fixtures: Path) -> None:
    assert (fixtures / "index.json").read_text("utf-8") == index.render(index.build_index())
    assert index.main(["--check"]) == 0


def test_real_index_is_fresh(real_data: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WGJ_DATA", str(real_data))
    assert index.main(["--check"]) == 0
