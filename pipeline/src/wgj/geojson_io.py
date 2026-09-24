"""Reading and writing the repository's GeoJSON.

Two readers: `scan` and `feature_count` stream with ijson so a 15 MB file
costs a few tens of MB of RSS rather than a gigabyte of Python objects;
`load` reads a whole file for the steps that rewrite it. One writer:
`serialise`, the canonical layout every committed file uses (one feature per
line, `id` before `properties`, coordinates with at most six decimals) so a
second run of any step is a no-op.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from collections.abc import Iterable
from pathlib import Path


def feature_count(path: Path) -> int:
    """Count features without holding the parsed file in memory."""
    import ijson

    n = 0
    with path.open("rb") as fh:
        for prefix, event, _ in ijson.parse(fh, use_float=True):
            if event == "start_map" and prefix == "features.item":
                n += 1
    return n


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def scan(path: Path) -> dict:
    """One streaming pass: feature count, bbox, geometry types, property keys.

    Never retains more than a single coordinate position, so memory is flat
    regardless of file size.
    """
    n_features = 0
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    prop_keys: set[str] = set()
    geom_types: Counter[str] = Counter()
    pos: list[float] = []

    import ijson

    with path.open("rb") as fh:
        for prefix, event, value in ijson.parse(fh, use_float=True):
            if event == "start_map" and prefix == "features.item":
                n_features += 1
            elif event == "map_key" and prefix == "features.item.properties":
                prop_keys.add(value)
            elif event == "string" and prefix.endswith("geometry.type"):
                geom_types[value] += 1
            elif ".coordinates" in prefix:
                # ijson emits one `.item` per nesting level, so every coordinate
                # number's prefix contains ".coordinates". The innermost
                # start_array/end_array pair brackets one position.
                if event == "start_array":
                    pos = []
                elif event == "number":
                    pos.append(float(value))
                elif event == "end_array":
                    if len(pos) >= 2:
                        x, y = pos[0], pos[1]
                        minx, maxx = min(minx, x), max(maxx, x)
                        miny, maxy = min(miny, y), max(maxy, y)
                    pos = []

    bbox = (
        [round(v, 6) for v in (minx, miny, maxx, maxy)]
        if n_features and minx != float("inf")
        else []
    )
    return {
        "features": n_features,
        "bbox": bbox,
        "geometry_types": dict(sorted(geom_types.items())),
        "properties": sorted(prop_keys),
    }


def fmt_number(v: float | int) -> str:
    """Coordinates: at most six decimals, no exponent, no trailing zeros."""
    if isinstance(v, bool):  # pragma: no cover - never a coordinate
        raise TypeError("bool is not a coordinate")
    if isinstance(v, int):
        return str(v)
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fmt_coords(c: object) -> str:
    if isinstance(c, list):
        return "[" + ",".join(fmt_coords(x) for x in c) + "]"
    if isinstance(c, (int, float)):
        return fmt_number(c)
    raise TypeError(f"unexpected value in coordinates: {c!r}")


def fmt_geometry(g: dict) -> str:
    return (
        "{" + f'"type":{json.dumps(g["type"])},"coordinates":{fmt_coords(g["coordinates"])}' + "}"
    )


def fmt_feature(f: dict) -> str:
    props = json.dumps(f["properties"], ensure_ascii=False, separators=(",", ":"))
    fid = json.dumps(f["id"], ensure_ascii=False)
    return (
        '{"type":"Feature","id":'
        + fid
        + ',"properties":'
        + props
        + ',"geometry":'
        + fmt_geometry(f["geometry"])
        + "}"
    )


def bbox_of(features: Iterable[dict]) -> list[float]:
    minx = miny = float("inf")
    maxx = maxy = float("-inf")

    def walk(c: object) -> None:
        nonlocal minx, miny, maxx, maxy
        if isinstance(c, list) and c and isinstance(c[0], (int, float)):
            x, y = float(c[0]), float(c[1])
            minx, maxx = min(minx, x), max(maxx, x)
            miny, maxy = min(miny, y), max(maxy, y)
        elif isinstance(c, list):
            for item in c:
                walk(item)

    for f in features:
        walk(f["geometry"]["coordinates"])
    return [round(v, 6) for v in (minx, miny, maxx, maxy)]


def serialise(features: list[dict]) -> bytes:
    bbox = "[" + ",".join(fmt_number(v) for v in bbox_of(features)) + "]"
    body = ",\n".join(fmt_feature(f) for f in features)
    return (
        '{"type":"FeatureCollection","bbox":' + bbox + ',"features":[\n' + body + "\n]}"
    ).encode("utf-8")


def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text("utf-8"))
    if data.get("type") != "FeatureCollection":
        raise SystemExit(f"{path}: not a FeatureCollection")
    return list(data.get("features") or [])
