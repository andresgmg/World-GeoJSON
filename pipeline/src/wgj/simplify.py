"""Simplification to a fixed ground tolerance, with a size budget."""

from __future__ import annotations

from pathlib import Path

from wgj.mapshaper import run_mapshaper

# Standard simplification tolerance, in metres on the ground.
#
# This is a *distance*, not a percentage, and that choice matters. A percentage
# keeps a fixed share of each file's vertices, so the resulting ground
# resolution depends entirely on how densely the source happened to be
# digitised — two neighbouring countries end up at different fidelities. A
# distance tolerance gives every dataset in the repository the same real-world
# resolution, which is the property a coherent collection needs.
#
# Calibrated against Chile, which has one of the most complex coastlines on
# Earth: its 16 regions come to 49.7 MB at 10 m, 21.2 MB at 25 m, 10.0 MB at
# 50 m, 4.6 MB at 100 m and 1.6 MB at 250 m. 100 m is far finer than any
# administrative boundary is meaningfully surveyed to for general use, and it
# keeps even the worst case comfortably inside the CDN ceiling.
TOLERANCE_M = 100

# Hard ceiling. jsDelivr refuses files over 20 MB, so nothing may approach it.
# Applied only as a fallback: a dataset that still exceeds this at the standard
# tolerance gets a coarser one, and the value used is recorded in the manifest.
SIZE_BUDGET = 18 * 1024 * 1024


def simplify(
    src: Path,
    dest: Path,
    budget: int | None = SIZE_BUDGET,
    extra: list[str] | None = None,
    pre: list[str] | None = None,
) -> dict:
    """Simplify to the standard ground tolerance, coarsening only if oversized.

    Returns what was actually applied, for the manifest. The standard tolerance
    is used unmodified for essentially every dataset; the doubling loop is a
    safety net for pathological inputs, not the normal path.

    `budget=None` disables size-driven coarsening. Split levels use that: their
    canonical artefacts are the per-parent parts, and judging the level by the
    size of an *optional* whole-country file would needlessly degrade
    resolution — Brazil's 5,570 municipalities blow the ceiling as one file
    while every per-state file fits at the standard tolerance with room to
    spare.
    """
    extra = extra or []
    # `pre` runs before -simplify. Filtering there matters: the Natural Earth
    # source is one global file, and simplifying all 258 countries before
    # discarding 257 of them would be absurd.
    pre = pre or []

    def write(interval: int) -> int:
        run_mapshaper(
            [
                str(src),
                *pre,
                "-simplify",
                f"interval={interval}",
                "keep-shapes",
                *extra,
                "-o",
                "precision=0.000001",
                "bbox",
                "format=geojson",
                str(dest),
            ]
        )
        return dest.stat().st_size

    interval = TOLERANCE_M
    size = write(interval)
    if budget is not None:
        while size > budget and interval < 10_000:
            interval *= 2
            print(f"      over budget at {interval // 2} m, retrying at {interval} m")
            size = write(interval)

        if size > budget:
            raise RuntimeError(
                f"{dest.name}: {size / 1024 / 1024:.1f} MB still exceeds the budget "
                f"at {interval} m tolerance"
            )

    print(f"      {interval} m tolerance  ->  {size / 1024 / 1024:.1f} MB")
    return {"method": "visvalingam", "tolerance_m": interval}
