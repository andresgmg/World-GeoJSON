"""Administrative levels and the file-name conventions built on them."""

from __future__ import annotations

import re

LEVELS = ["ADM0", "ADM1", "ADM2", "ADM3", "ADM4"]
QUAD = "QUAD"

LABELS = {
    "ADM0": "Country / body outline",
    "ADM1": "First-level divisions",
    "ADM2": "Second-level divisions",
    "ADM3": "Third-level divisions",
    # Guadeloupe and Martinique publish their communes as ADM4 upstream.
    "ADM4": "Fourth-level divisions",
    "QUAD": "Quadrangles",
}

LEVEL_RE = re.compile(r"^(ADM[0-4]|QUAD)$")
LEVEL_DIR = LEVEL_RE
LEVEL_FILE = re.compile(r"^[A-Z]{3,4}_(ADM[0-4]|QUAD)$")
PREVIEW_FILE = re.compile(r"^([A-Z]{3,4})_(ADM[0-4]|QUAD)\.preview\.geojson$")


def parse_stem(stem: str) -> tuple[str, str] | None:
    """`CHL_ADM3` -> ("CHL", "ADM3"), or None when it is not a level file."""
    m = LEVEL_FILE.match(stem)
    if not m:
        return None
    code, _, level = stem.rpartition("_")
    return code, level


def preview_name(code: str, level: str) -> str:
    return f"{code}_{level}.preview.geojson"
