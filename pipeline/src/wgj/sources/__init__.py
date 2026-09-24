"""Upstream sources: one module per provider, plus what the manifest says about them."""

from __future__ import annotations

STANDARD_FIELDS = ["shapeName", "shapeISO", "shapeGroup", "shapeType", "parentISO"]

SOURCE_INFO = {
    "geoboundaries": {
        "name": "geoBoundaries (gbOpen)",
        "url": "https://www.geoboundaries.org/",
    },
    "natural-earth": {
        "name": "Natural Earth 10m Admin 0",
        "url": "https://www.naturalearthdata.com/",
        "license": "public-domain",
    },
    "ide-chile": {
        "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
        "url": "https://www.geoportal.cl/",
        "license": "CC-BY-4.0",
    },
}
