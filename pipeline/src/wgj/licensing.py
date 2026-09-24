"""Licence policy: which upstream terms may be redistributed here.

Data that cannot be redistributed must never reach the working tree, let
alone git history, so this is applied at fetch time (fetch.plan) and again at
validation (the schema's `license` enum, which ALLOWED mirrors).
"""

from __future__ import annotations

import re

# Matched case-insensitively against geoBoundaries' free-text `boundaryLicense`.
# Anything not matching here is refused — including every ODbL and CC-BY-SA
# variant. Kept deliberately conservative: an unrecognised licence is a reason
# to stop and read it, not to guess.
PERMISSIVE: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"public domain", re.I), "public-domain"),
    (re.compile(r"\bCC0\b", re.I), "CC0-1.0"),
    (re.compile(r"creative commons attribution 4\.0|CC[ -]BY[ -]4\.0", re.I), "CC-BY-4.0"),
    (re.compile(r"attribution 3\.0 intergovernmental|CC[ -]BY[ -]3\.0 IGO", re.I), "CC-BY-3.0-IGO"),
    (re.compile(r"creative commons attribution 3\.0|CC[ -]BY[ -]3\.0", re.I), "CC-BY-3.0"),
    (re.compile(r"creative commons attribution 2\.5|CC[ -]BY[ -]2\.5", re.I), "CC-BY-2.5"),
    (re.compile(r"etalab", re.I), "Etalab-2.0"),
    # geoBoundaries writes this as "Open Government Canada 2.0" — no "licence".
    (re.compile(r"open government.*canada", re.I), "OGL-Canada-2.0"),
]
COPYLEFT = re.compile(r"ODbL|open data commons|share.?alike|CC[ -]BY[ -]SA", re.I)

# SPDX identifiers that permit redistribution and commercial use without a
# share-alike obligation. schemas/manifest.schema.json carries the same list
# as the `license` enum; wgj.schema checks the two agree.
ALLOWED: frozenset[str] = frozenset(ident for _, ident in PERMISSIVE)


def spdx(license_text: str) -> str | None:
    """Map geoBoundaries' free-text licence onto an SPDX id, or None."""
    if not license_text or COPYLEFT.search(license_text):
        return None
    for pattern, ident in PERMISSIVE:
        if pattern.search(license_text):
            return ident
    return None


def rollup(licenses: list[str]) -> tuple[str, list[str] | None]:
    """The country-level licence derived from its datasets.

    A single licence is stated as such; several become ("mixed", [sorted]).
    A territory whose only dataset is a public-domain outline must not read
    as CC BY, and several countries mix licences across levels — Argentina's
    ADM1 is CC BY 2.5 and its ADM2 CC BY 3.0 IGO.
    """
    distinct = sorted(set(licenses))
    if len(distinct) == 1:
        return distinct[0], None
    return "mixed", distinct
