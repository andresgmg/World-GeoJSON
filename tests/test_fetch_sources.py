from __future__ import annotations

import pytest

import fetch_sources


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Creative Commons Attribution 4.0 International (CC BY 4.0)", "CC-BY-4.0"),
        ("CC-BY 4.0", "CC-BY-4.0"),
        ("Creative Commons Attribution 3.0 Intergovernmental (CC BY 3.0 IGO)", "CC-BY-3.0-IGO"),
        ("Creative Commons Attribution 3.0", "CC-BY-3.0"),
        ("Creative Commons Attribution 2.5", "CC-BY-2.5"),
        ("Open Government Canada 2.0", "OGL-Canada-2.0"),
        ("Licence Ouverte / Open Licence (Etalab)", "Etalab-2.0"),
        ("Public Domain", "public-domain"),
        ("CC0", "CC0-1.0"),
    ],
)
def test_spdx_maps_permissive_licences(text: str, expected: str) -> None:
    assert fetch_sources.spdx(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Open Data Commons Open Database License (ODbL)",
        "ODbL-1.0",
        "Creative Commons Attribution-ShareAlike 4.0",
        "CC BY-SA 3.0",
        # Share-alike wins even when a permissive phrase is also present.
        "Creative Commons Attribution 4.0 Share-Alike",
        "",
        "Some licence nobody has heard of",
    ],
)
def test_spdx_rejects_copyleft_and_unknown(text: str) -> None:
    assert fetch_sources.spdx(text) is None


def test_allow_lists_agree() -> None:
    """The fetch-time mapping and the validate-time allow-list must match.

    They are maintained by hand in two files; drifting apart would let a
    licence through one gate and reject it at the other.
    """
    import validate_data

    fetch_ids = {ident for _, ident in fetch_sources.PERMISSIVE}
    assert fetch_ids == validate_data.ALLOWED_LICENSES


def test_continent_scope_covers_the_registry() -> None:
    regions = fetch_sources.CONTINENTS["americas"]
    in_scope = {k for k, v in fetch_sources.COUNTRIES.items() if v.get("m49_region") in regions}
    assert len(in_scope) == len(fetch_sources.COUNTRIES)
    assert "CHL" in in_scope
