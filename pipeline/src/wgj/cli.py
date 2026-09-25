"""`wgj` — the World GeoJSON pipeline, one subcommand per step.

    wgj fetch --continent americas      download sources into .cache/sources/
    wgj build CHL                       normalise + simplify + finalize one country
    wgj finalize data/earth/*/          ids, hierarchy, corrections, bbox, canonical layout
    wgj previews data/earth/CHL         catalog map previews
    wgj manifest data/earth/*/          manifest.json datasets[]
    wgj index                           data/index.json
    wgj validate --checksums            every check CI runs
    wgj all CHL                         build → previews → manifest → index → validate

Each subcommand has its own --help.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Callable

from wgj import __version__

Command = Callable[[list[str]], int]


def _fetch(argv: list[str]) -> int:
    from wgj.fetch import main

    return main(argv)


def _build(argv: list[str]) -> int:
    from wgj.build import main

    return main(argv)


def _finalize(argv: list[str]) -> int:
    from wgj.finalize import main

    return main(argv)


def _previews(argv: list[str]) -> int:
    from wgj.previews import main

    return main(argv)


def _manifest(argv: list[str]) -> int:
    from wgj.manifest import main

    return main(argv)


def _index(argv: list[str]) -> int:
    from wgj.index import main

    return main(argv)


def _validate(argv: list[str]) -> int:
    from wgj.validate import main

    return main(argv)


def _all(argv: list[str]) -> int:
    """build, previews, manifest and index for the given countries, then validate."""
    from wgj.paths import country_dir

    ap = argparse.ArgumentParser(prog="wgj all")
    ap.add_argument("iso3", nargs="+")
    args = ap.parse_args(argv)
    dirs = [str(country_dir(c.upper())) for c in args.iso3]
    for step, cmd_argv in (
        (_build, list(args.iso3)),
        (_previews, dirs),
        (_manifest, dirs),
        (_index, []),
        (_validate, dirs),
    ):
        rc = step(cmd_argv)
        if rc:
            return rc
    return 0


COMMANDS: dict[str, tuple[Command, str]] = {
    "fetch": (_fetch, "download source data into .cache/sources/"),
    "build": (_build, "normalise source data into data/ (runs finalize)"),
    "finalize": (_finalize, "apply the data contract to committed files"),
    "previews": (_previews, "write the catalog map previews"),
    "manifest": (_manifest, "write manifest.json datasets[]"),
    "index": (_index, "write data/index.json"),
    "validate": (_validate, "validate everything against the conventions and schemas"),
    "all": (_all, "build → previews → manifest → index → validate"),
}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] in ("-h", "--help"):
        width = max(len(k) for k in COMMANDS)
        print(__doc__.strip())
        print("\ncommands:")
        for name, (_, help_text) in COMMANDS.items():
            print(f"  {name:<{width}}  {help_text}")
        return 0
    if args[0] in ("-V", "--version"):
        print(f"wgj {__version__}")
        return 0
    cmd = COMMANDS.get(args[0])
    if cmd is None:
        print(f"wgj: unknown command '{args[0]}' (try: {', '.join(COMMANDS)})", file=sys.stderr)
        return 2
    return cmd[0](args[1:])
