from __future__ import annotations

from pathlib import Path

import pytest

import gen_catalog


@pytest.mark.parametrize(
    ("n", "expected"),
    [(None, "—"), (0, "0 B"), (846, "846 B"), (4_814_221, "4.6 MB"), (14_854_660, "14.2 MB")],
)
def test_human_bytes(n: int | None, expected: str) -> None:
    assert gen_catalog.human_bytes(n) == expected


def test_slug() -> None:
    assert gen_catalog.slug("South America") == "south-america"
    assert gen_catalog.slug("Latin America / Caribbean") == "latin-america---caribbean"


def test_every_level_in_data_has_a_label(abw: Path) -> None:
    """A level without a label renders as a bare code on its catalog page."""
    import json

    levels: set[str] = set()
    for mpath in gen_catalog.DATA.glob("*/*/manifest.json"):
        for ds in json.loads(mpath.read_text("utf-8")).get("datasets", []):
            levels.add(ds["level"])
    assert levels <= set(gen_catalog.LEVELS), levels - set(gen_catalog.LEVELS)


def test_generate_copies_previews_and_refreshes_changed_ones(abw: Path, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()

    gen_catalog.generate(docs, "https://cdn.example", "https://raw.example")

    pages = sorted(p.relative_to(docs).as_posix() for p in docs.rglob("*.md"))
    assert "catalog/index.md" in pages
    assert "catalog/SUMMARY.md" in pages
    assert "catalog/earth/caribbean/abw.md" in pages

    asset = docs / "catalog" / "earth" / "caribbean" / "abw" / "ADM0.preview.geojson"
    src = abw / "preview" / "ABW_ADM0.preview.geojson"
    assert asset.read_bytes() == src.read_bytes()

    # Same length, different bytes: must be re-copied (it used to compare sizes).
    stale = bytearray(src.read_bytes())
    stale[0:1] = b"X" if stale[:1] != b"X" else b"Y"
    asset.write_bytes(bytes(stale))
    assert asset.stat().st_size == src.stat().st_size

    gen_catalog.generate(docs, "https://cdn.example", "https://raw.example")
    assert asset.read_bytes() == src.read_bytes()


def test_generate_is_idempotent(abw: Path, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    gen_catalog.generate(docs, "", "")
    assert gen_catalog.generate(docs, "", "") == 0
