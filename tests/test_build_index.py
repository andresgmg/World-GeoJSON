from __future__ import annotations

from pathlib import Path

import build_index
import validate_data


def test_index_is_deterministic_and_consistent(abw: Path) -> None:
    first = build_index.build_index()
    second = build_index.build_index()
    assert build_index.render(first) == build_index.render(second)

    countries = first["countries"]
    assert [c["iso_a3"] for c in countries] == sorted(c["iso_a3"] for c in countries)
    datasets = [d for c in countries for d in c["datasets"]]
    assert first["totals"] == {
        "countries": len(countries),
        "datasets": len(datasets),
        "features": sum(d["features"] for d in datasets),
        "bytes": sum(d.get("bytes", 0) for d in datasets),
    }
    aruba = next(c for c in countries if c["iso_a3"] == "ABW")
    assert aruba["levels"] == ["ADM0"]
    assert aruba["licenses"] == ["public-domain"]
    assert aruba["manifest"] == "data/earth/ABW/manifest.json"


def test_index_validates_against_its_schema(abw: Path) -> None:
    v = validate_data.validator("index.schema.json")
    errors = list(v.iter_errors(build_index.build_index()))
    assert errors == [], [validate_data._describe(e) for e in errors[:5]]


def test_committed_index_is_fresh(repo: Path) -> None:
    index = repo / "data" / "index.json"
    if not index.exists():
        import pytest

        pytest.skip("data/index.json not checked out")
    assert index.read_text("utf-8") == build_index.render(build_index.build_index())
