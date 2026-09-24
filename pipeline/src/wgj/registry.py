"""The curated tables the pipeline runs on.

countries.json is the single source of truth for which ADM level is the
MUNICIPAL tier in each country; it cannot be inferred from the data because
geoBoundaries' level numbers are not semantically consistent across
countries. The other files hold documented upstream corrections.
"""

from __future__ import annotations

import json
from functools import cache
from importlib import resources
from typing import Any

CONTINENTS: dict[str, set[str]] = {
    "americas": {"Northern America", "Central America", "Caribbean", "South America"},
}


def _load(name: str) -> dict[str, Any]:
    text = resources.files("wgj.tables").joinpath(name).read_text("utf-8")
    data: dict[str, Any] = json.loads(text)
    return {k: v for k, v in data.items() if not k.startswith("$")}


def raw_registry(name: str = "countries.json") -> dict[str, Any]:
    """The file as stored, `$comment` included (for schema validation)."""
    text = resources.files("wgj.tables").joinpath(name).read_text("utf-8")
    data: dict[str, Any] = json.loads(text)
    return data


@cache
def countries() -> dict[str, dict[str, Any]]:
    """ISO3 -> registry entry (iso_a2, m49_region, name, source, municipal_level, ...)."""
    return _load("countries.json")


@cache
def iso3166_2() -> dict[str, Any]:
    return _load("iso3166_2.json")


@cache
def shapeiso_fixes() -> dict[str, dict[str, dict[str, str]]]:
    """ISO3 -> level -> src_shape_id (or "*") -> corrected shapeISO."""
    return _load("shapeiso_fixes.json")


@cache
def id_overrides() -> dict[str, dict[str, dict[str, str]]]:
    """ISO3 -> level -> ident -> feature-id key."""
    return _load("id_overrides.json")


def resolve_targets(iso3s: list[str] | None, continent: str | None) -> list[str]:
    """The ISO3 codes a command should act on.

    Exactly one of the two selectors must be given; the old scripts accepted
    both and disagreed on which won.
    """
    if bool(iso3s) == bool(continent):
        raise SystemExit("pass ISO 3166-1 alpha-3 codes or --continent, not both and not neither")
    reg = countries()
    if continent:
        regions = CONTINENTS[continent]
        return sorted(k for k, v in reg.items() if v.get("m49_region") in regions)
    targets = [c.upper() for c in iso3s or []]
    unknown = sorted(set(targets) - set(reg))
    if unknown:
        raise SystemExit(f"not in countries.json: {', '.join(unknown)}")
    return targets
