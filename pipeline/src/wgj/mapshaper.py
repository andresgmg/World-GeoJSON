"""Running mapshaper.

Geometry work is delegated to mapshaper. That is deliberate: it does
topology-preserving simplification, shapefile reading, spatial joins and
splitting correctly and in one process, and it avoids a heavyweight GDAL
dependency in a repository whose contributors are mostly not Python
developers. It is pinned in package.json (`npm ci`).
"""

from __future__ import annotations

import shutil
import subprocess

from wgj.paths import REPO


class MapshaperNotFound(SystemExit):
    """Raised at call time, never at import: the pure helpers must work without Node."""


def _mapshaper_cmd() -> list[str]:
    """Prefer the pinned local install over `npx -y`.

    `npx -y mapshaper` re-resolves the package on every invocation, and a full
    continent means hundreds of them; concurrent runs then collide on the npm
    cache and fail intermittently. `npm install` pins the version in
    package.json, which also makes the pipeline reproducible.
    """
    local = REPO / "node_modules" / ".bin"
    for name in ("mapshaper.cmd", "mapshaper"):
        candidate = local / name
        if candidate.exists():
            return [str(candidate)]
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise MapshaperNotFound("mapshaper not found — run `npm install`")
    return [npx, "-y", "mapshaper"]


_MAPSHAPER: list[str] | None = None


def mapshaper_cmd() -> list[str]:
    """Resolve mapshaper on first use, not at import.

    Resolving at import made the module unimportable on a machine without
    Node — including the test runner — even for the pure helpers below.
    """
    global _MAPSHAPER
    if _MAPSHAPER is None:
        _MAPSHAPER = _mapshaper_cmd()
    return _MAPSHAPER


def run_mapshaper(args: list[str]) -> None:
    """Invoke mapshaper with shell=False.

    shell=True would hand the argument list to cmd.exe, which re-parses it and
    mangles the quoting inside the -each expressions. shell=False lets Python
    quote each argument correctly, which is why the JS object literals below
    can use single quotes and survive intact.
    """
    proc = subprocess.run(
        [*mapshaper_cmd(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()
        tail = detail[-1] if detail else "no output"
        # RuntimeError, not SystemExit: main() catches it per country so one
        # bad dataset does not abandon the other fifty-six.
        raise RuntimeError(f"mapshaper: {tail}")


def js_lookup(mapping: dict[str, str]) -> str:
    """A single-quoted JS object literal, safe to pass as one argv element."""
    body = ",".join(f"'{k}':'{v}'" for k, v in mapping.items())
    return "{" + body + "}"


def js_expr(pairs: dict[str, str]) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs.items())
