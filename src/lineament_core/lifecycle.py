"""Single-job state and replay rules for Worker clients and contract adapters."""

from enum import IntEnum, StrEnum
from uuid import UUID

from .application import Job
from .diagnostics import ContractError, ErrorCode
from .domain import ArtifactRef, JobResult
from .wire import Cancel, EventKind, WorkerEvent, decode_event


class JobState(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    CANCEL_REQUESTED = "cancel_requested"
    COMMITTING = "committing"
    CANCELLED = "cancelled"
    FAILED = "failed"
    COMPLETED = "completed"


class ExitCode(IntEnum):
    COMPLETED = 0
    FAILED = 1
    INVALID_REQUEST = 2
    CANCELLED = 3


_TERMINAL_EXITS = {
    JobState.COMPLETED: ExitCode.COMPLETED,
    JobState.FAILED: ExitCode.FAILED,
    JobState.CANCELLED: ExitCode.CANCELLED,
}
_ACTIVE = frozenset({JobState.RUNNING, JobState.CANCEL_REQUESTED, JobState.COMMITTING})


class JobLifecycle:
    """Replay a single accepted job. Deliver commands and events serially."""

    def __init__(self, job: Job) -> None:
        self._job_id = job.id
        self._algorithm = job.algorithm
        self._state = JobState.PENDING
        self._sequence = 0
        self._stage: str | None = None
        self._progress: int | None = None
        self._artifacts: dict[UUID, ArtifactRef] = {}
        self._result: JobResult | None = None
        self._exit_confirmed = False
        self._transport_failed = False

    @property
    def state(self) -> JobState:
        return self._state

    @property
    def progress(self) -> int | None:
        return self._progress

    @property
    def stage(self) -> str | None:
        return self._stage

    @property
    def result(self) -> JobResult | None:
        return self._result if self._exit_confirmed else None

    def can_acknowledge_cancel(self, command: Cancel) -> bool:
        """An acknowledgement is recorded by the corresponding event."""
        if command.job_id != self._job_id:
            raise ContractError(ErrorCode.INVALID_MESSAGE)
        return self._state is JobState.RUNNING

    def accept(self, event: WorkerEvent) -> None:
        if (
            event.job_id != self._job_id
            or event.sequence != self._sequence + 1
            or self._state in _TERMINAL_EXITS
        ):
            raise ContractError(ErrorCode.INVALID_TRANSITION)
        kind, data = event.kind, event.data
        if kind is EventKind.STARTED and self._state is JobState.PENDING:
            self._state = JobState.RUNNING
        elif kind is EventKind.FAILED and self._state in _ACTIVE:
            self._state = JobState.FAILED
        elif kind is EventKind.WARNING and self._state in _ACTIVE:
            pass
        elif kind is EventKind.CANCEL_REQUESTED and self._state is JobState.RUNNING:
            self._state = JobState.CANCEL_REQUESTED
        elif kind is EventKind.CANCELLED and self._state is JobState.CANCEL_REQUESTED:
            self._state = JobState.CANCELLED
        elif (
            kind is EventKind.COMMIT_STARTED
            and self._state is JobState.RUNNING
            and self._stage is None
        ):
            self._state = JobState.COMMITTING
        elif kind is EventKind.ARTIFACT_CREATED and self._state is JobState.COMMITTING:
            if data.id in self._artifacts:
                raise ContractError(ErrorCode.INVALID_RESULT)
            self._artifacts[data.id] = data
        elif kind is EventKind.COMPLETED and self._state is JobState.COMMITTING:
            self._complete(data)
        elif (
            kind is EventKind.STAGE_STARTED
            and self._state is JobState.RUNNING
            and self._stage is None
        ):
            self._stage = data
        elif (
            kind is EventKind.STAGE_COMPLETED
            and self._state in _ACTIVE
            and data == self._stage
        ):
            self._stage = None
        elif kind is EventKind.PROGRESS and self._state is JobState.RUNNING:
            if self._progress is not None and data < self._progress:
                raise ContractError(ErrorCode.INVALID_TRANSITION)
            self._progress = data
        else:
            raise ContractError(ErrorCode.INVALID_TRANSITION)
        if self._state in _TERMINAL_EXITS:
            self._stage = None
        self._sequence = event.sequence

    def _complete(self, result: JobResult) -> None:
        available = {artifact.id: artifact for artifact in result.artifacts}
        if (
            result.job_id != self._job_id
            or result.algorithm != self._algorithm
            or any(
                available.get(key) != value for key, value in self._artifacts.items()
            )
        ):
            raise ContractError(ErrorCode.INVALID_RESULT)
        self._result = result
        self._state = JobState.COMPLETED

    def accept_frame(self, frame: bytes) -> None:
        try:
            if self._transport_failed:
                raise ContractError(ErrorCode.TRANSPORT_FAILURE)
            self.accept(decode_event(frame))
        except ContractError:
            self._transport_failed = True
            self._exit_confirmed = False
            raise ContractError(ErrorCode.TRANSPORT_FAILURE) from None

    def finish(self, returncode: int) -> JobState:
        expected = _TERMINAL_EXITS.get(self._state)
        if self._transport_failed or expected is None or returncode != expected:
            self._transport_failed = True
            self._exit_confirmed = False
            raise ContractError(ErrorCode.TRANSPORT_FAILURE)
        self._exit_confirmed = True
        return self._state
