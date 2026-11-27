"""UTF-8 JSONL codec and versioned Worker message contracts."""

import json
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import BinaryIO
from uuid import UUID

from .application import Job, is_json_value
from .diagnostics import ContractError, ErrorCode, WarningCode, explanation
from .domain import (
    RESULT_VERSION,
    AlgorithmRef,
    ArtifactRef,
    CrsStatus,
    JobResult,
    ProjectRef,
    SourceAssetRef,
    SpatialReference,
    require_id,
)

PROTOCOL_VERSION = "1.0"
SUPPORTED_VERSIONS = (PROTOCOL_VERSION,)
MAX_FRAME_BYTES = 64 * 1024
_VERSION_PATTERN = re.compile(r"(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})")
_UTC_TIMESTAMP = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z"
)


def _version(value: object) -> tuple[int, int]:
    match = _VERSION_PATTERN.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise ContractError(ErrorCode.INVALID_MESSAGE)
    return int(match[1]), int(match[2])


def negotiate_version(
    offered: tuple[str, ...], supported: tuple[str, ...] = SUPPORTED_VERSIONS
) -> str:
    for value in (*offered, *supported):
        _version(value)
    common = set(offered).intersection(supported)
    if not common:
        raise ContractError(ErrorCode.UNSUPPORTED_VERSION)
    return max(common, key=_version)


def encode_version_offer(versions: tuple[str, ...] = SUPPORTED_VERSIONS) -> bytes:
    for value in versions:
        _version(value)
    if not versions or len(versions) != len(set(versions)):
        raise ContractError(ErrorCode.INVALID_MESSAGE)
    return encode_frame({"type": "hello", "supported_versions": list(versions)})


def decode_version_offer(frame: bytes) -> tuple[str, ...]:
    message = decode_frame(frame)
    _fields(message, {"type", "supported_versions"})
    values = message["supported_versions"]
    if message["type"] != "hello" or not isinstance(values, list) or not values:
        raise ContractError(ErrorCode.INVALID_MESSAGE)
    for value in values:
        _version(value)
    if len(values) != len(set(values)):
        raise ContractError(ErrorCode.INVALID_MESSAGE)
    return tuple(values)


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = dict(pairs)
    if len(result) != len(pairs):
        raise ValueError("Repeated object key")
    return result


def _finite_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite number")
    return result


def encode_frame(message: dict[str, object]) -> bytes:
    try:
        if type(message) is not dict or not is_json_value(message):
            raise ValueError("Expected a JSON object")
        payload = json.dumps(
            message, ensure_ascii=False, allow_nan=False, separators=(",", ":")
        )
        frame = payload.encode("utf-8") + b"\n"
        if len(frame) > MAX_FRAME_BYTES:
            raise ValueError("Record exceeds the size limit")
    except (TypeError, ValueError, RecursionError):
        raise ContractError(ErrorCode.INVALID_FRAME) from None
    return frame


def decode_frame(frame: bytes) -> dict[str, object]:
    if len(frame) > MAX_FRAME_BYTES or not frame.endswith(b"\n") or b"\n" in frame[:-1]:
        raise ContractError(ErrorCode.INVALID_FRAME)
    try:
        message = json.loads(
            frame.decode("utf-8"),
            object_pairs_hook=_unique_object,
            parse_float=_finite_float,
            parse_constant=_finite_float,
        )
        # Escaped lone surrogates can be accepted by json.loads but cannot be sent as UTF-8.
        json.dumps(message, ensure_ascii=False).encode("utf-8")
    except (ValueError, RecursionError):
        raise ContractError(ErrorCode.INVALID_FRAME) from None
    if not isinstance(message, dict) or not is_json_value(message):
        raise ContractError(ErrorCode.INVALID_FRAME)
    return message


def read_frame(stream: BinaryIO) -> bytes | None:
    """Read one bounded frame. The stream must be discarded after a framing error."""
    frame = stream.readline(MAX_FRAME_BYTES + 1)
    if not frame:
        return None
    if len(frame) > MAX_FRAME_BYTES or not frame.endswith(b"\n"):
        raise ContractError(ErrorCode.INVALID_FRAME)
    return frame


def _fields(
    value: object, required: set[str], optional: frozenset[str] = frozenset()
) -> None:
    if (
        not isinstance(value, dict)
        or required - value.keys()
        or value.keys() - (required | optional)
    ):
        raise ContractError(ErrorCode.INVALID_MESSAGE)


def _uuid(value: object) -> UUID:
    if not isinstance(value, str):
        raise ValueError("Expected UUID string")
    result = UUID(value)
    require_id(result)
    if str(result) != value:
        raise ValueError("Expected canonical UUID")
    return result


def _protocol(message: dict[str, object]) -> None:
    version = message.get("protocol_version")
    _version(version)
    if version != PROTOCOL_VERSION:
        raise ContractError(ErrorCode.UNSUPPORTED_VERSION)


@dataclass(frozen=True, slots=True)
class Cancel:
    job_id: UUID

    def __post_init__(self) -> None:
        require_id(self.job_id)


def encode_command(command: Job | Cancel) -> bytes:
    if isinstance(command, Cancel):
        message = {"type": "cancel", "job_id": str(command.job_id)}
    else:
        message = {
            "type": "job",
            "job_id": str(command.id),
            "project_id": str(command.project.id),
            "operation": command.algorithm.id,
            "algorithm_version": command.algorithm.version,
            "inputs": {name: str(asset.id) for name, asset in command.inputs.items()},
            "parameters": _json_data(command.parameters),
            "resource_profile": command.resource_profile,
        }
    frame = encode_frame({"protocol_version": PROTOCOL_VERSION, **message})
    decode_command(frame)
    return frame


def _json_data(value: object) -> object:
    """Turn validated immutable parameters back into JSON-native containers."""
    if isinstance(value, Mapping):
        return {key: _json_data(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_data(item) for item in value]
    return value


def decode_command(frame: bytes) -> Job | Cancel:
    message = decode_frame(frame)
    _protocol(message)
    common = {"type", "protocol_version", "job_id"}
    try:
        if message.get("type") == "cancel":
            _fields(message, common)
            return Cancel(_uuid(message["job_id"]))
        _fields(
            message,
            common
            | {
                "project_id",
                "operation",
                "algorithm_version",
                "inputs",
                "parameters",
                "resource_profile",
            },
        )
        inputs, parameters = message["inputs"], message["parameters"]
        if (
            message["type"] != "job"
            or not isinstance(inputs, dict)
            or not isinstance(parameters, dict)
        ):
            raise ValueError("Invalid job payload")
        return Job(
            _uuid(message["job_id"]),
            ProjectRef(_uuid(message["project_id"])),
            AlgorithmRef(message["operation"], message["algorithm_version"]),
            {name: SourceAssetRef(_uuid(value)) for name, value in inputs.items()},
            parameters,
            message["resource_profile"],
        )
    except (TypeError, ValueError):
        raise ContractError(ErrorCode.INVALID_MESSAGE) from None


class EventKind(StrEnum):
    STARTED = "started"
    STAGE_STARTED = "stage_started"
    PROGRESS = "progress"
    WARNING = "warning"
    ARTIFACT_CREATED = "artifact_created"
    STAGE_COMPLETED = "stage_completed"
    CANCEL_REQUESTED = "cancel_requested"
    COMMIT_STARTED = "commit_started"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


_EVENT_FIELDS = {
    EventKind.STAGE_STARTED: ("stage", str),
    EventKind.STAGE_COMPLETED: ("stage", str),
    EventKind.PROGRESS: ("percent", int),
    EventKind.WARNING: ("warning_code", WarningCode),
    EventKind.ARTIFACT_CREATED: ("artifact", ArtifactRef),
    EventKind.FAILED: ("error_code", ErrorCode),
    EventKind.COMPLETED: ("result", JobResult),
}


@dataclass(frozen=True, slots=True)
class WorkerEvent:
    kind: EventKind
    job_id: UUID
    sequence: int
    timestamp: datetime
    data: str | int | WarningCode | ErrorCode | ArtifactRef | JobResult | None = None

    def __post_init__(self) -> None:
        require_id(self.job_id)
        if (
            not isinstance(self.kind, EventKind)
            or type(self.sequence) is not int
            or self.sequence < 1
        ):
            raise ValueError("Expected a known event and positive sequence")
        if not isinstance(
            self.timestamp, datetime
        ) or self.timestamp.utcoffset() != timedelta(0):
            raise ValueError("Expected UTC timestamp")
        _, expected_type = _EVENT_FIELDS.get(self.kind, ("", type(None)))
        if type(self.data) is not expected_type:
            raise ValueError("Incorrect event payload type")
        if self.kind is EventKind.PROGRESS and not 0 <= self.data <= 100:
            raise ValueError("Expected an integer percent between 0 and 100")
        if self.kind in (
            EventKind.STAGE_STARTED,
            EventKind.STAGE_COMPLETED,
        ) and not re.fullmatch(r"[a-z][a-z0-9_.-]{0,63}", self.data):
            raise ValueError("Expected a safe stage identifier")

    @property
    def diagnostic_message(self) -> str | None:
        if isinstance(self.data, (ErrorCode, WarningCode)):
            return explanation(self.data)
        return None


def _artifact_data(artifact: ArtifactRef) -> dict[str, object]:
    output = {"id": str(artifact.id), "kind": artifact.kind}
    if artifact.spatial is not None:
        spatial = artifact.spatial
        output["spatial"] = {
            "status": spatial.status,
            "crs": spatial.crs,
            "horizontal_unit": spatial.horizontal_unit,
            "vertical_unit": spatial.vertical_unit,
        }
    return output


def _artifact(value: object) -> ArtifactRef:
    _fields(value, {"id", "kind"}, frozenset({"spatial"}))
    spatial = None
    if "spatial" in value:
        data = value["spatial"]
        _fields(data, {"status", "crs", "horizontal_unit", "vertical_unit"})
        spatial = SpatialReference(
            CrsStatus(data["status"]),
            data["crs"],
            data["horizontal_unit"],
            data["vertical_unit"],
        )
    return ArtifactRef(_uuid(value["id"]), value["kind"], spatial)


def _result(value: object) -> JobResult:
    _fields(
        value,
        {"result_version", "job_id", "operation", "algorithm_version", "artifacts"},
    )
    if value["result_version"] != RESULT_VERSION:
        raise ContractError(ErrorCode.UNSUPPORTED_VERSION)
    if not isinstance(value["artifacts"], list):
        raise ValueError("Expected result artifact list")
    return JobResult(
        _uuid(value["job_id"]),
        AlgorithmRef(value["operation"], value["algorithm_version"]),
        tuple(_artifact(item) for item in value["artifacts"]),
    )


def encode_event(event: WorkerEvent) -> bytes:
    message = {
        "type": event.kind,
        "job_id": str(event.job_id),
        "protocol_version": PROTOCOL_VERSION,
        "sequence": event.sequence,
        "timestamp": event.timestamp.isoformat().replace("+00:00", "Z"),
    }
    if event.kind is EventKind.ARTIFACT_CREATED:
        message["artifact"] = _artifact_data(event.data)
    elif event.kind is EventKind.COMPLETED:
        result = event.data
        message["result"] = {
            "result_version": result.version,
            "job_id": str(result.job_id),
            "operation": result.algorithm.id,
            "algorithm_version": result.algorithm.version,
            "artifacts": [_artifact_data(item) for item in result.artifacts],
        }
    elif event.kind in _EVENT_FIELDS:
        message[_EVENT_FIELDS[event.kind][0]] = event.data
    return encode_frame(message)


def decode_event(frame: bytes) -> WorkerEvent:
    message = decode_frame(frame)
    _protocol(message)
    try:
        kind = EventKind(message.get("type"))
        keys = {"type", "job_id", "protocol_version", "sequence", "timestamp"}
        field = _EVENT_FIELDS.get(kind)
        if field is not None:
            keys.add(field[0])
        _fields(message, keys)
        data = None if field is None else message[field[0]]
        if kind is EventKind.ARTIFACT_CREATED:
            data = _artifact(data)
        elif kind is EventKind.COMPLETED:
            data = _result(data)
        elif kind is EventKind.WARNING:
            data = WarningCode(data)
        elif kind is EventKind.FAILED:
            data = ErrorCode(data)
        timestamp = message["timestamp"]
        if not isinstance(timestamp, str) or not _UTC_TIMESTAMP.fullmatch(timestamp):
            raise ValueError("Expected UTC timestamp ending in Z")
        return WorkerEvent(
            kind,
            _uuid(message["job_id"]),
            message["sequence"],
            datetime.fromisoformat(timestamp),
            data,
        )
    except (TypeError, ValueError):
        raise ContractError(ErrorCode.INVALID_MESSAGE) from None
