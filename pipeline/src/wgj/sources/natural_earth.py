"""Natural Earth 10m Admin 0 — every country outline (public domain)."""

from __future__ import annotations

import json
from pathlib import Path

from wgj.geojson_io import feature_count
from wgj.mapshaper import js_expr
from wgj.paths import CACHE, earth
from wgj.simplify import simplify

NE_ADM0_URL = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_10m_admin_0_countries.geojson"
)
NE_ADM0_FILE = CACHE / "natural-earth" / "ne_10m_admin_0_countries.geojson"

_NE_CODES: set[str] | None = None


def natural_earth_codes(src: Path) -> set[str]:
    """Every ADM0_A3 / ISO_A3 present in the global file, parsed once."""
    global _NE_CODES
    if _NE_CODES is None:
        data = json.loads(src.read_text("utf-8"))
        _NE_CODES = set()
        for f in data.get("features", []):
            p = f.get("properties") or {}
            for key in ("ADM0_A3", "ISO_A3"):
                v = p.get(key)
                if v and v != "-99":
                    _NE_CODES.add(v)
    return _NE_CODES


def build_adm0(iso3: str, entry: dict) -> dict | None:
    """Carve one country's outline out of the global Natural Earth file.

    Natural Earth rather than geoBoundaries for ADM0: it is public domain, a
    single coherent generalisation instead of 51 per-country files of wildly
    varying quality, and it covers the six Americas territories geoBoundaries
    has no ADM0 for at all.
    """
    src = CACHE / "natural-earth" / "ne_10m_admin_0_countries.geojson"
    if not src.exists():
        print("  ADM0 skipped — Natural Earth not cached")
        return None

    # Check membership up front. mapshaper aborts with a confusing
    # "Table is missing one or more fields" when a filter matches nothing,
    # because an empty table has no columns for -filter-fields to keep.
    if iso3 not in natural_earth_codes(src):
        print(f"  ADM0 — {iso3} is not in Natural Earth")
        return None

    out_dir = earth() / iso3
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{iso3}_ADM0.geojson"

    print("  ADM0")
    simp = simplify(
        src,
        dest,
        # ADM0_A3 rather than ISO_A3: Natural Earth sets ISO_A3 to "-99" for
        # territories whose status is contested, and those are exactly the ones
        # we still want to ship. Filtering happens before simplification.
        pre=["-filter", f"ADM0_A3 === '{iso3}' || ISO_A3 === '{iso3}'"],
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "NAME_LONG || NAME",
                    "shapeISO": f"'{iso3}'",
                    "shapeGroup": f"'{iso3}'",
                    "shapeType": "'ADM0'",
                }
            ),
            "-filter-fields",
            "shapeName,shapeISO,shapeGroup,shapeType",
        ],
    )

    if feature_count(dest) == 0:
        dest.unlink()
        print("  ADM0 — not present in Natural Earth")
        return None
    return {"level": "ADM0", "simplification": simp}
