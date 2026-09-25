"""Shapes of what the client returns, mirroring ``schemas/`` in the repository.

Written by hand from ``index.schema.json``, ``manifest.schema.json`` and
``feature.schema.json`` so the package needs no code generator. ``TypedDict``
keeps the objects plain ``dict``s: what ``json.loads`` gives back is what you
get, with names for your editor and type checker.
"""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict

Body = Literal["earth", "moon", "mars"]
Level = str
"""``ADM0`` … ``ADM4`` or ``QUAD``."""
Status = Literal["ok", "review", "deprecated"]
BBox = list[float]
"""``[west, south, east, north]`` in degrees."""


class Localised(TypedDict):
    en: str
    es: NotRequired[str]


class Crs(TypedDict):
    authority: str
    code: str
    epsg: int


class Source(TypedDict):
    name: str
    url: str
    license: str
    licenses: NotRequired[list[str]]
    retrieved: str


class Simplification(TypedDict):
    method: Literal["visvalingam", "douglas-peucker", "none"]
    tolerance_m: int


class GeometryTypes(TypedDict, total=False):
    Polygon: int
    MultiPolygon: int


class Part(TypedDict):
    """One file of a split level: ``data/{body}/{ISO3}/{LEVEL}/{code}.geojson``."""

    code: str
    path: str
    bytes: int
    sha256: str
    features: int
    bbox: BBox
    geometry_types: GeometryTypes
    properties: list[str]


class Dataset(TypedDict):
    level: Level
    path: NotRequired[str]
    """Absent when the level is published as parts only (Brazil ADM2)."""
    bytes: int
    sha256: NotRequired[str]
    features: int
    bbox: BBox
    geometry_types: GeometryTypes
    properties: list[str]
    preview: NotRequired[str]
    preview_bytes: NotRequired[int]
    simplification: NotRequired[Simplification]
    license: str
    src_provider: NotRequired[str]
    src_year: NotRequired[str | int]
    unassigned: NotRequired[int]
    split_by: NotRequired[Literal["ADM1"]]
    parts: NotRequired[list[Part]]


class Terms(TypedDict, total=False):
    adm1: Localised
    adm2: Localised
    municipal: Localised


class Country(TypedDict):
    """One entry of ``index.countries``: the manifest plus derived fields."""

    body: Body
    iso_a3: str
    iso_a2: NotRequired[str]
    m49_region: NotRequired[str]
    name: Localised
    status: Status
    manifest: str
    license: str
    licenses: list[str]
    levels: list[Level]
    municipal_level: Level | None
    terms: NotRequired[Terms]
    crs: Crs
    source: Source
    notes: NotRequired[str]
    datasets: list[Dataset]


class Totals(TypedDict):
    countries: int
    datasets: int
    features: int
    bytes: int


class Index(TypedDict):
    """``data/index.json``: every territory and dataset in one file."""

    schema_version: int
    bodies: list[Body]
    totals: Totals
    countries: list[Country]


class CountrySummary(TypedDict):
    """What :meth:`geoworld.GeoWorld.countries` returns: the index entry without its datasets."""

    iso_a3: str
    iso_a2: str | None
    name: Localised
    m49_region: str | None
    status: Status
    license: str
    licenses: list[str]
    levels: list[Level]
    municipal_level: Level | None
    datasets: int
    features: int
    bytes: int


class FeatureProperties(TypedDict):
    """The documented keys of a feature's ``properties``.

    Features carry them as a plain ``dict[str, Any]`` because ``src_*`` keys
    (verbatim upstream attributes) vary by source.
    """

    shapeName: str
    shapeISO: str
    shapeGroup: str
    shapeType: Level
    adm1ISO: NotRequired[str]
    parentISO: NotRequired[str]
    parentID: NotRequired[str]


class Geometry(TypedDict):
    type: Literal["Polygon", "MultiPolygon"]
    coordinates: Any


class Feature(TypedDict):
    type: Literal["Feature"]
    id: str
    """``{ISO3}:{LEVEL}:{key}``, unique within a data version."""
    properties: dict[str, Any]
    geometry: Geometry
    bbox: NotRequired[BBox]


class FeatureCollection(TypedDict):
    type: Literal["FeatureCollection"]
    bbox: NotRequired[BBox]
    features: list[Feature]


class FeatureId(TypedDict):
    """A parsed feature id."""

    iso3: str
    level: Level
    key: str
