from __future__ import annotations

import pytest

from wgj import licensing, schema


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
    assert licensing.spdx(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "Open Data Commons Open Database License (ODbL)",
        "ODbL-1.0",
        "Creative Commons Attribution-ShareAlike 4.0",
        "CC BY-SA 3.0",
        "Creative Commons Attribution 4.0 Share-Alike",  # share-alike wins
        "",
        "Some licence nobody has heard of",
    ],
)
def test_spdx_rejects_copyleft_and_unknown(text: str) -> None:
    assert licensing.spdx(text) is None


def test_rollup() -> None:
    assert licensing.rollup(["CC-BY-4.0", "CC-BY-4.0"]) == ("CC-BY-4.0", None)
    assert licensing.rollup(["public-domain", "CC-BY-2.5", "public-domain"]) == (
        "mixed",
        ["CC-BY-2.5", "public-domain"],
    )


def test_allow_list_matches_the_schema() -> None:
    """One list, two homes: the fetch-time mapping and the manifest schema's enum."""
    assert schema.allowed_licenses() == licensing.ALLOWED
    assert "ODbL-1.0" not in licensing.ALLOWED
