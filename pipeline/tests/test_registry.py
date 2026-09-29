from __future__ import annotations

import pytest

from wgj import registry, schema
from wgj.sources import SOURCE_INFO


def test_registry_validates_against_its_schema() -> None:
    errors = list(schema.validator("countries.schema.json").iter_errors(registry.raw_registry()))
    assert errors == [], [schema.describe_error(e) for e in errors[:5]]


def test_registry_entries_are_usable() -> None:
    reg = registry.countries()
    assert "CHL" in reg and "$comment" not in reg
    for iso3, entry in reg.items():
        assert entry["source"] in SOURCE_INFO, iso3
        assert any(entry["m49_region"] in regions for regions in registry.CONTINENTS.values()), iso3


def test_continents_partition_the_registry() -> None:
    """Every entry belongs to exactly one continent, so --continent covers them all."""
    per_continent = [set(registry.resolve_targets(None, c)) for c in registry.CONTINENTS]
    assert sum(len(s) for s in per_continent) == len(registry.countries())
    assert set().union(*per_continent) == set(registry.countries())


def test_resolve_targets() -> None:
    assert "CHL" in registry.resolve_targets(None, "americas")
    assert registry.resolve_targets(["chl", "USA"], None) == ["CHL", "USA"]
    with pytest.raises(SystemExit, match="not both"):
        registry.resolve_targets(["CHL"], "americas")
    with pytest.raises(SystemExit, match="not both"):
        registry.resolve_targets([], None)
    with pytest.raises(SystemExit, match=r"not in countries\.json"):
        registry.resolve_targets(["XXX"], None)


def test_corrections_are_keyed_by_upstream_id() -> None:
    fixes = registry.shapeiso_fixes()
    assert fixes["USA"]["ADM1"]["66186276B38006515706420"] == "US-SD"
    assert fixes["BLZ"]["ADM2"] == {"*": ""}
    assert registry.id_overrides() == {}
