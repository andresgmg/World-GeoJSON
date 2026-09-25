"""Build the cross-language goldens in fixtures/expected/ from the Python client.

Run ``python packages/python/geoworld/tests/goldens.py`` to rewrite them; the
Python and the JavaScript test suites both assert their output is identical,
so the two clients cannot drift apart on what they compute from the index and
the files (summaries, hierarchy, search, ids).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]
FIXTURES = REPO / "fixtures"
EXPECTED = FIXTURES / "expected"

SEARCHES: list[tuple[str, str | None]] = [
    ("santo", None),
    ("las", "ADM2"),
    ("san", "ADM2"),
    ("DO-01", "ADM1"),
    ("PERAVIA", None),
    ("compostéla", "ADM2"),
    ("", None),
]


def canonical(obj: Any) -> str:
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def build(world: Any) -> dict[str, Any]:
    """Everything both clients must agree on, computed for the fixtures."""
    dom = world.country("DOM")
    tree: dict[str, dict[str, list[str]]] = {}
    root = "DOM:ADM0:DOM"
    tree[root] = {}
    for adm1 in world.children(root):
        tree[root][adm1["id"]] = [child["id"] for child in world.children(adm1["id"])]
    parents = {
        "DOM:ADM0:DOM": None,
        "DOM:ADM1:DO-02": world.parent("DOM:ADM1:DO-02")["id"],
        "DOM:ADM2:DO-02.estebania": world.parent("DOM:ADM2:DO-02.estebania")["id"],
    }
    leaf = world.find("DOM:ADM2:DO-02.guayabal")
    return {
        "countries": world.countries(),
        "totals": world.index()["totals"],
        "dom": {
            "levels": world.levels("DOM"),
            "municipal_level": dom["municipal_level"],
            "terms": dom.get("terms"),
            "parts": world.parts("DOM", "ADM2"),
            "paths": {
                "ADM0": world.dataset("DOM", "ADM0")["path"],
                "ADM1_preview": world.dataset("DOM", "ADM1")["preview"],
                "ADM2_parts": [p["path"] for p in world.dataset("DOM", "ADM2")["parts"]],
            },
            "bbox": {level: world.bbox("DOM", level) for level in world.levels("DOM")},
            "feature_counts": {
                level: sum(1 for _ in world.features("DOM", level)) for level in world.levels("DOM")
            },
            "preview_ids": [f["id"] for f in world.preview("DOM", "ADM1")["features"]][:5],
            "tree": tree,
            "parents": parents,
            "leaf": {
                "id": leaf["id"],
                "properties": leaf["properties"],
                "bbox": leaf.get("bbox"),
                "geometry_type": leaf["geometry"]["type"],
            },
            "search": {
                f"{text}|{level or '*'}": [f["id"] for f in world.search(text, "DOM", level)]
                for text, level in SEARCHES
            },
        },
    }


def main() -> int:
    from geoworld import GeoWorld

    world = GeoWorld(base_url=FIXTURES.as_uri(), cache=False)
    EXPECTED.mkdir(exist_ok=True)
    (EXPECTED / "fixtures.json").write_text(canonical(build(world)), encoding="utf-8")
    print(f"wrote {EXPECTED / 'fixtures.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
