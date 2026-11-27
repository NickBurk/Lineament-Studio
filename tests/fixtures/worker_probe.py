"""Subprocess fixture for the contract suite. No production operations are registered."""

import sys
from datetime import UTC, datetime
from pathlib import Path

from lineament_core.application import Job
from lineament_core.diagnostics import ContractError
from lineament_core.lifecycle import ExitCode, JobLifecycle
from lineament_core.wire import (
    Cancel,
    EventKind,
    WorkerEvent,
    decode_command,
    encode_event,
    encode_version_offer,
    read_frame,
)


def main() -> int:
    source = sys.stdin.buffer
    sink = sys.stdout.buffer
    mode = sys.argv[1]
    if mode == "describe":
        sink.write(encode_version_offer())
        return 0

    frame = read_frame(source)
    if frame is None:
        return ExitCode.INVALID_REQUEST
    try:
        job = decode_command(frame)
    except ContractError:
        return ExitCode.INVALID_REQUEST
    if not isinstance(job, Job):
        return ExitCode.INVALID_REQUEST

    lifecycle = JobLifecycle(job)
    stdout_fixture = Path(__file__).with_name("completed.jsonl")
    started, *remaining = stdout_fixture.read_bytes().splitlines(keepends=True)
    lifecycle.accept_frame(started)
    sink.write(started)
    sink.flush()
    if mode == "crash":
        return 90

    # A pipe buffer-sized read from stdout alone can deadlock at this boundary.
    sys.stderr.buffer.write(b"x" * (256 * 1024))
    sys.stderr.buffer.flush()
    cancelled = False
    while (frame := read_frame(source)) is not None:
        command = decode_command(frame)
        if not isinstance(command, Cancel):
            return ExitCode.INVALID_REQUEST
        if lifecycle.can_acknowledge_cancel(command):
            event = WorkerEvent(
                EventKind.CANCEL_REQUESTED, job.id, 2, datetime.now(UTC)
            )
            lifecycle.accept(event)
            sink.write(encode_event(event))
            cancelled = True
    if cancelled:
        sink.write(
            encode_event(WorkerEvent(EventKind.CANCELLED, job.id, 3, datetime.now(UTC)))
        )
        return ExitCode.CANCELLED
    for record in remaining:
        sink.write(record)
    return ExitCode.COMPLETED


if __name__ == "__main__":
    raise SystemExit(main())
