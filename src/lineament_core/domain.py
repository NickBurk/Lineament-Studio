"""Domain values shared by clients and Core, independent of persistence and IO."""

import re
from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


def require_id(value: UUID) -> None:
    if not isinstance(value, UUID) or not value.int:
        raise ValueError("Expected a non-nil UUID")


def require_label(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Expected a non-empty label")


@dataclass(frozen=True, slots=True)
class ProjectRef:
    id: UUID

    def __post_init__(self) -> None:
        require_id(self.id)


@dataclass(frozen=True, slots=True)
class SourceAssetRef:
    id: UUID

    def __post_init__(self) -> None:
        require_id(self.id)


class CrsStatus(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    ABSENT = "absent"


@dataclass(frozen=True, slots=True)
class SpatialReference:
    """Declared CRS and units. Core does not infer or transform coordinates."""

    status: CrsStatus
    crs: str | None = None
    horizontal_unit: str | None = None
    vertical_unit: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.status, CrsStatus):
            raise ValueError("Expected a CrsStatus")
        if self.status is CrsStatus.KNOWN:
            if self.crs is None or self.horizontal_unit is None:
                raise ValueError("Known CRS requires a definition and horizontal unit")
        if self.status is CrsStatus.ABSENT and self.crs is not None:
            raise ValueError("Absent CRS cannot have a definition")
        for value in (self.crs, self.horizontal_unit, self.vertical_unit):
            if value is not None:
                require_label(value)


class GeometricRank(StrEnum):
    G1 = "G1"
    G2 = "G2"
    G3 = "G3"


@dataclass(frozen=True, slots=True)
class GeologicalOrder:
    """An independently supplied expert classification."""

    label: str

    def __post_init__(self) -> None:
        require_label(self.label)


@dataclass(frozen=True, slots=True)
class AlgorithmRef:
    id: str
    version: str

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.id):
            raise ValueError("Invalid algorithm identifier")
        if not re.fullmatch(
            r"(?:0|[1-9][0-9]{0,8})(?:\.(?:0|[1-9][0-9]{0,8})){2}", self.version
        ):
            raise ValueError("Expected an algorithm version X.Y.Z")


@dataclass(frozen=True, slots=True)
class ArtifactRef:
    id: UUID
    kind: str
    spatial: SpatialReference | None = None

    def __post_init__(self) -> None:
        require_id(self.id)
        require_label(self.kind)
        if self.spatial is not None and not isinstance(self.spatial, SpatialReference):
            raise ValueError("Expected a SpatialReference")


RESULT_VERSION = "1.0"


@dataclass(frozen=True, slots=True)
class JobResult:
    job_id: UUID
    algorithm: AlgorithmRef
    artifacts: tuple[ArtifactRef, ...] | list[ArtifactRef] = ()
    version: str = RESULT_VERSION

    def __post_init__(self) -> None:
        require_id(self.job_id)
        if self.version != RESULT_VERSION:
            raise ValueError("Unsupported result version")
        if type(self.artifacts) not in (list, tuple):
            raise ValueError("Expected a list or tuple of artifacts")
        if any(not isinstance(artifact, ArtifactRef) for artifact in self.artifacts):
            raise ValueError("Expected ArtifactRef elements")
        object.__setattr__(self, "artifacts", tuple(self.artifacts))
        if len({artifact.id for artifact in self.artifacts}) != len(self.artifacts):
            raise ValueError("Duplicate result artifact ID")
