from __future__ import annotations

import json
from pathlib import Path

import pytest

from wgj import catalog
from wgj.levels import LABELS
from wgj.text import group_slug, human_bytes


@pytest.mark.parametrize(
    ("n", "expected"),
    [(None, "—"), (0, "0 B"), (846, "846 B"), (4_814_221, "4.6 MB"), (14_854_660, "14.2 MB")],
)
def test_human_bytes(n: int | None, expected: str) -> None:
    assert human_bytes(n) == expected


def test_group_slug() -> None:
    assert group_slug("South America") == "south-america"
    assert group_slug("Latin America / Caribbean") == "latin-america---caribbean"


def test_every_level_in_the_data_has_a_label(real_data: Path) -> None:
    levels: set[str] = set()
    for mpath in real_data.glob("*/*/manifest.json"):
        for ds in json.loads(mpath.read_text("utf-8")).get("datasets", []):
            levels.add(ds["level"])
    assert levels <= set(LABELS), levels - set(LABELS)


def test_generate_copies_previews_and_refreshes_changed_ones(abw: Path, tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    catalog.generate(docs, "https://cdn.example", "https://raw.example")

    pages = sorted(p.relative_to(docs).as_posix() for p in docs.rglob("*.md"))
    assert pages == [
        "catalog/SUMMARY.md",
        "catalog/earth/caribbean/abw.md",
        "catalog/earth/caribbean/brb.md",
        "catalog/earth/caribbean/dom.md",
        "catalog/index.md",
    ]
    asset = docs / "catalog" / "earth" / "caribbean" / "abw" / "ADM0.preview.geojson"
    src = abw / "preview" / "ABW_ADM0.preview.geojson"
    assert asset.read_bytes() == src.read_bytes()

    # Same length, different bytes: must be re-copied (it used to compare sizes).
    stale = bytearray(src.read_bytes())
    stale[0:1] = b"X" if stale[:1] != b"X" else b"Y"
    asset.write_bytes(bytes(stale))
    catalog.generate(docs, "https://cdn.example", "https://raw.example")
    assert asset.read_bytes() == src.read_bytes()
    assert catalog.generate(docs, "https://cdn.example", "https://raw.example") == 0

    dom_page = (docs / "catalog" / "earth" / "caribbean" / "dom.md").read_text("utf-8")
    assert "No preview available" in dom_page  # the reduced fixture has no ADM2 preview
    assert "wgj previews" in dom_page


def test_publish_schemas_copies_and_prunes(tmp_path: Path) -> None:
    docs = tmp_path / "docs"
    docs.mkdir()
    n = catalog.publish_schemas(docs)
    names = sorted(p.name for p in (docs / "schemas").glob("*.json"))
    assert n == len(names) >= 5 and "manifest.schema.json" in names
    (docs / "schemas" / "old.json").write_text("{}", "utf-8")
    assert catalog.publish_schemas(docs) == 1
    assert catalog.publish_schemas(docs) == 0
