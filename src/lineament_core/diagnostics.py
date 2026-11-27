"""Stable diagnostics. Wire diagnostics use codes with fixed, public explanations."""

from enum import StrEnum


class ErrorCode(StrEnum):
    INVALID_FRAME = "invalid_frame"
    INVALID_MESSAGE = "invalid_message"
    UNSUPPORTED_VERSION = "unsupported_version"
    UNKNOWN_OPERATION = "unknown_operation"
    UNSUPPORTED_ALGORITHM_VERSION = "unsupported_algorithm_version"
    DUPLICATE_OPERATION = "duplicate_operation"
    INVALID_PARAMETERS = "invalid_parameters"
    INVALID_INPUTS = "invalid_inputs"
    INVALID_RESULT = "invalid_result"
    INVALID_TRANSITION = "invalid_transition"
    TRANSPORT_FAILURE = "transport_failure"
    EXECUTION_FAILED = "execution_failed"


class WarningCode(StrEnum):
    PARTIAL_COVERAGE = "partial_coverage"
    APPROXIMATE_RESULT = "approximate_result"


_EXPLANATIONS = {
    ErrorCode.INVALID_FRAME: "The JSONL record is malformed or exceeds the size limit.",
    ErrorCode.INVALID_MESSAGE: "The record does not match the message contract.",
    ErrorCode.UNSUPPORTED_VERSION: "The requested protocol or result version is unsupported.",
    ErrorCode.UNKNOWN_OPERATION: "The operation is not registered.",
    ErrorCode.UNSUPPORTED_ALGORITHM_VERSION: "The requested algorithm version is unavailable.",
    ErrorCode.DUPLICATE_OPERATION: "This algorithm version is already registered.",
    ErrorCode.INVALID_PARAMETERS: "The parameters do not match the operation declaration.",
    ErrorCode.INVALID_INPUTS: "The inputs do not match the operation declaration.",
    ErrorCode.INVALID_RESULT: "The result does not match the job or its output declaration.",
    ErrorCode.INVALID_TRANSITION: "The event is inconsistent with the job state.",
    ErrorCode.TRANSPORT_FAILURE: "The worker stream or process ended unexpectedly.",
    ErrorCode.EXECUTION_FAILED: "The worker could not complete the operation.",
    WarningCode.PARTIAL_COVERAGE: "The available data covers only part of the requested area.",
    WarningCode.APPROXIMATE_RESULT: "The operation produced an approximation.",
}


def explanation(code: ErrorCode | WarningCode) -> str:
    return _EXPLANATIONS[code]


class ContractError(Exception):
    def __init__(self, code: ErrorCode) -> None:
        self.code = code
        super().__init__(explanation(code))
