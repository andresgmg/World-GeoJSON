"""Small text helpers shared across the pipeline."""

from __future__ import annotations

import unicodedata


def slug(text: str) -> str:
    """ASCII, lower-case, hyphen-separated: `Región de Ñuble` -> `region-de-nuble`."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    out = "".join(c if c.isalnum() else "-" for c in ascii_text.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def group_slug(text: str) -> str:
    """The catalog's folder name for an M49 region: `South America` -> `south-america`."""
    return text.lower().replace(" ", "-").replace("/", "-")


def human_bytes(n: int | None) -> str:
    if n is None:
        return "—"
    size = float(n)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


def mb(n: int | float) -> str:
    return f"{n / 1024 / 1024:.1f} MB"
