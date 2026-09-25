"""Exceptions raised by the client. All inherit from :class:`GeoWorldError`."""

from __future__ import annotations


class GeoWorldError(Exception):
    """Base class for every error the client raises on purpose."""


class UnknownCountry(GeoWorldError, KeyError):
    """No territory with that ISO 3166-1 alpha-3 code in the index."""

    def __init__(self, iso3: str) -> None:
        super().__init__(iso3)
        self.iso3 = iso3

    def __str__(self) -> str:
        return f"no territory {self.iso3!r} in this data version"


class UnknownLevel(GeoWorldError, KeyError):
    """The territory exists but does not publish that level."""

    def __init__(self, iso3: str, level: str, available: list[str]) -> None:
        super().__init__(level)
        self.iso3 = iso3
        self.level = level
        self.available = available

    def __str__(self) -> str:
        return f"{self.iso3} has no {self.level}; available: {', '.join(self.available) or 'none'}"


class UnknownPart(GeoWorldError, KeyError):
    """The level is split but has no part with that code."""

    def __init__(self, iso3: str, level: str, code: str) -> None:
        super().__init__(code)
        self.iso3 = iso3
        self.level = level
        self.code = code

    def __str__(self) -> str:
        return f"{self.iso3} {self.level} has no part {self.code!r}"


class NotSplit(GeoWorldError):
    """Parts were requested for a level that is published as one file."""

    def __init__(self, iso3: str, level: str) -> None:
        super().__init__(iso3, level)
        self.iso3 = iso3
        self.level = level

    def __str__(self) -> str:
        return f"{self.iso3} {self.level} is not split into parts; use get()"


class NoCombinedFile(GeoWorldError):
    """The level is published as parts only (Brazil ADM2); use ``iter_parts``."""

    def __init__(self, iso3: str, level: str) -> None:
        super().__init__(iso3, level)
        self.iso3 = iso3
        self.level = level

    def __str__(self) -> str:
        return (
            f"{self.iso3} {self.level} has no combined file; "
            "use iter_parts() or get_part() to read it part by part"
        )


class NoPreview(GeoWorldError):
    """The dataset has no simplified preview."""

    def __init__(self, iso3: str, level: str) -> None:
        super().__init__(iso3, level)
        self.iso3 = iso3
        self.level = level

    def __str__(self) -> str:
        return f"{self.iso3} {self.level} has no preview"


class UnknownFeature(GeoWorldError, KeyError):
    """No feature with that id in its dataset."""

    def __init__(self, feature_id: str) -> None:
        super().__init__(feature_id)
        self.feature_id = feature_id

    def __str__(self) -> str:
        return f"no feature {self.feature_id!r}"


class InvalidFeatureId(GeoWorldError, ValueError):
    """The string is not a ``{ISO3}:{LEVEL}:{key}`` id."""


class UnsupportedSchema(GeoWorldError):
    """The index declares a ``schema_version`` newer than this client understands."""

    def __init__(self, found: object, supported: int) -> None:
        super().__init__(found, supported)
        self.found = found
        self.supported = supported

    def __str__(self) -> str:
        return (
            f"index schema_version {self.found!r} is newer than this client supports "
            f"({self.supported}); upgrade geoworld"
        )


class DownloadError(GeoWorldError):
    """A file could not be fetched."""

    def __init__(self, url: str, reason: str, status: int | None = None) -> None:
        super().__init__(url, reason, status)
        self.url = url
        self.reason = reason
        self.status = status

    def __str__(self) -> str:
        code = f" (HTTP {self.status})" if self.status else ""
        return f"could not fetch {self.url}{code}: {self.reason}"


class ChecksumMismatch(GeoWorldError):
    """The downloaded bytes do not hash to the ``sha256`` the index promises."""

    def __init__(self, path: str, expected: str, actual: str) -> None:
        super().__init__(path, expected, actual)
        self.path = path
        self.expected = expected
        self.actual = actual

    def __str__(self) -> str:
        return (
            f"{self.path}: sha256 {self.actual[:12]}… does not match "
            f"the index ({self.expected[:12]}…)"
        )
