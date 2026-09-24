"""The JSON Schemas under schemas/, loaded once, with cross-file $refs resolved locally."""

from __future__ import annotations

import json
from functools import cache
from typing import Any

from wgj.licensing import ALLOWED
from wgj.paths import SCHEMAS

BASE = "https://andresgmg.github.io/World-GeoJSON/schemas/"


@cache
def _schemas() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in sorted(SCHEMAS.glob("*.schema.json")):
        s = json.loads(p.read_text("utf-8"))
        out[s["$id"]] = s
    return out


def load(name: str) -> dict[str, Any]:
    """schemas/<name> as a dict."""
    return _schemas()[BASE + name]


@cache
def _registry() -> Any:
    from referencing import Registry, Resource

    return Registry().with_resources(
        (uri, Resource.from_contents(s)) for uri, s in _schemas().items()
    )


def validator(name: str) -> Any:
    """A Draft 2020-12 validator for schemas/<name>."""
    from jsonschema import Draft202012Validator, FormatChecker

    return Draft202012Validator(load(name), registry=_registry(), format_checker=FormatChecker())


def describe_error(error: object) -> str:
    """One line for a jsonschema ValidationError."""
    path = "/".join(str(p) for p in getattr(error, "absolute_path", []))
    msg = str(getattr(error, "message", error))
    if len(msg) > 200:
        msg = msg[:200] + "…"
    return f"{path or '(root)'}: {msg}"


def allowed_licenses() -> frozenset[str]:
    """The manifest schema's licence enum; must equal wgj.licensing.ALLOWED."""
    enum = frozenset(load("manifest.schema.json")["$defs"]["license"]["enum"])
    if enum != ALLOWED:
        raise RuntimeError(
            "schemas/manifest.schema.json licence enum and wgj.licensing.PERMISSIVE disagree: "
            f"{sorted(enum ^ ALLOWED)}"
        )
    return enum
