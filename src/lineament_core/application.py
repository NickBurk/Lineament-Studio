"""Algorithm declarations and ports. Composition is owned by the caller."""

import math
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from enum import Enum, StrEnum
from threading import Event
from types import MappingProxyType
from typing import Protocol
from uuid import UUID

from .diagnostics import ContractError, ErrorCode, WarningCode
from .domain import (
    AlgorithmRef,
    JobResult,
    ProjectRef,
    SourceAssetRef,
    require_id,
    require_label,
)


@dataclass(frozen=True, slots=True)
class Job:
    id: UUID
    project: ProjectRef
    algorithm: AlgorithmRef
    inputs: Mapping[str, SourceAssetRef]
    parameters: Mapping[str, object]
    resource_profile: str

    def __post_init__(self) -> None:
        require_id(self.id)
        require_label(self.resource_profile)
        object.__setattr__(self, "inputs", MappingProxyType(dict(self.inputs)))
        object.__setattr__(self, "parameters", MappingProxyType(dict(self.parameters)))


def is_json_value(value: object, depth: int = 0) -> bool:
    """Check JSON-native types and bound nesting, including for in-process callers."""
    if depth > 64:
        return False
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is list:
        return all(is_json_value(item, depth + 1) for item in value)
    if type(value) is dict:
        return all(
            isinstance(key, str) and is_json_value(item, depth + 1)
            for key, item in value.items()
        )
    return value is None or isinstance(value, str) or type(value) in (int, bool)


class ParameterType(StrEnum):
    BOOLEAN = "boolean"
    INTEGER = "integer"
    NUMBER = "number"
    STRING = "string"
    ARRAY = "array"
    OBJECT = "object"

    def accepts(self, value: object) -> bool:
        value_types = {
            self.BOOLEAN: (bool,),
            self.INTEGER: (int,),
            self.NUMBER: (int, float),
            self.STRING: (str,),
            self.ARRAY: (list,),
            self.OBJECT: (dict,),
        }
        return type(value) in value_types[self] and is_json_value(value)


class _Missing(Enum):
    VALUE = 0


@dataclass(frozen=True, slots=True)
class Parameter:
    kind: ParameterType
    default: object = _Missing.VALUE

    def __post_init__(self) -> None:
        if self.default is not _Missing.VALUE and (
            not self.kind.accepts(self.default)
            or self.kind in (ParameterType.ARRAY, ParameterType.OBJECT)
        ):
            raise ValueError("Default must be an immutable value of the declared type")


@dataclass(frozen=True, slots=True)
class AlgorithmDescriptor:
    algorithm: AlgorithmRef
    input_names: frozenset[str]
    output_kinds: frozenset[str]
    parameters: Mapping[str, Parameter] = field(default_factory=dict)
    resource_profiles: frozenset[str] = frozenset({"standard"})
    supports_progress: bool = False
    supports_cancellation: bool = False
    # Numeric algorithms supply a reference to their CRS, units, NoData, tolerance,
    # boundary, complexity, memory and fixture specifications at registration.
    scientific_spec: str | None = None

    def __post_init__(self) -> None:
        for name in ("input_names", "output_kinds", "resource_profiles"):
            values = frozenset(getattr(self, name))
            for value in values:
                require_label(value)
            object.__setattr__(self, name, values)
        parameters = dict(self.parameters)
        for name, parameter in parameters.items():
            require_label(name)
            if not isinstance(parameter, Parameter):
                raise ValueError("Expected a Parameter declaration")
        object.__setattr__(self, "parameters", MappingProxyType(parameters))


class AlgorithmRegistry:
    """An instance-scoped registry of explicit algorithm declarations."""

    def __init__(self) -> None:
        self._descriptors: dict[AlgorithmRef, AlgorithmDescriptor] = {}

    def register(self, descriptor: AlgorithmDescriptor) -> None:
        if descriptor.algorithm in self._descriptors:
            raise ContractError(ErrorCode.DUPLICATE_OPERATION)
        self._descriptors[descriptor.algorithm] = descriptor

    def resolve(self, algorithm: AlgorithmRef) -> AlgorithmDescriptor:
        descriptor = self._descriptors.get(algorithm)
        if descriptor is not None:
            return descriptor
        if any(key.id == algorithm.id for key in self._descriptors):
            raise ContractError(ErrorCode.UNSUPPORTED_ALGORITHM_VERSION)
        raise ContractError(ErrorCode.UNKNOWN_OPERATION)

    def validate(self, job: Job) -> dict[str, object]:
        descriptor = self.resolve(job.algorithm)
        if job.inputs.keys() != descriptor.input_names or any(
            not isinstance(item, SourceAssetRef) for item in job.inputs.values()
        ):
            raise ContractError(ErrorCode.INVALID_INPUTS)
        if job.resource_profile not in descriptor.resource_profiles or (
            job.parameters.keys() - descriptor.parameters.keys()
        ):
            raise ContractError(ErrorCode.INVALID_PARAMETERS)
        values = {}
        for name, parameter in descriptor.parameters.items():
            value = job.parameters.get(name, parameter.default)
            if not parameter.kind.accepts(value):
                raise ContractError(ErrorCode.INVALID_PARAMETERS)
            values[name] = value
        return values

    def validate_result(self, job: Job, result: JobResult) -> None:
        descriptor = self.resolve(job.algorithm)
        if (
            result.job_id != job.id
            or result.algorithm != job.algorithm
            or any(
                item.kind not in descriptor.output_kinds for item in result.artifacts
            )
        ):
            raise ContractError(ErrorCode.INVALID_RESULT)


class CancellationToken:
    """A cooperative signal shared with work running in this process."""

    def __init__(self) -> None:
        self._requested = Event()

    def request(self) -> None:
        self._requested.set()

    @property
    def requested(self) -> bool:
        return self._requested.is_set()


class Algorithm(Protocol):
    @property
    def descriptor(self) -> AlgorithmDescriptor: ...

    def run(
        self,
        job: Job,
        parameters: Mapping[str, object],
        cancellation: CancellationToken,
        report_progress: Callable[[int], None],
        report_warning: Callable[[WarningCode], None],
    ) -> JobResult: ...
