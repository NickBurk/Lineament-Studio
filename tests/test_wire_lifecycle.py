from dataclasses import replace
from datetime import UTC, datetime
from io import BytesIO
from uuid import uuid4

import pytest

from lineament_core.diagnostics import ContractError, ErrorCode, WarningCode
from lineament_core.lifecycle import ExitCode, JobLifecycle, JobState
from lineament_core.wire import (
    MAX_FRAME_BYTES,
    Cancel,
    EventKind,
    WorkerEvent,
    decode_command,
    decode_event,
    decode_frame,
    decode_version_offer,
    encode_command,
    encode_event,
    encode_frame,
    encode_version_offer,
    negotiate_version,
    read_frame,
)

UTC_NOW = datetime(2026, 11, 27, tzinfo=UTC)


def test_version_offer_selects_highest_exact_shared_version():
    offer = encode_version_offer(("2.0", "1.0", "1.7"))
    assert negotiate_version(decode_version_offer(offer)) == "1.0"
    assert negotiate_version(("1.10", "1.9"), ("1.9", "1.10")) == "1.10"
    with pytest.raises(ContractError) as caught:
        negotiate_version(("1.1", "2.0"))
    assert caught.value.code == ErrorCode.UNSUPPORTED_VERSION


@pytest.mark.parametrize(
    "data",
    [
        b"\xff\n",
        b"{}",
        b"[]\n",
        b"{}\n{}\n",
        b'{"a":1,"a":2}\n',
        b'{"a":NaN}\n',
        b'{"a":1e400}\n',
        b'{"a":"\\ud800"}\n',
        b" " * MAX_FRAME_BYTES + b"{}\n",
        b'{"a":' + b"[" * 80 + b"0" + b"]" * 80 + b"}\n",
    ],
)
def test_frame_rejects_invalid_or_ambiguous_json(data):
    with pytest.raises(ContractError) as caught:
        decode_frame(data)
    assert caught.value.code == ErrorCode.INVALID_FRAME


def test_bounded_reader_and_crlf():
    maximum = b" " * (MAX_FRAME_BYTES - 3) + b"{}\n"
    stream = BytesIO(maximum + b"{}\r\n")
    assert decode_frame(read_frame(stream)) == {}
    assert decode_frame(read_frame(stream)) == {}
    assert read_frame(stream) is None
    large = BytesIO(b" " * (MAX_FRAME_BYTES + 100) + b"\n")
    with pytest.raises(ContractError):
        read_frame(large)
    assert large.tell() == MAX_FRAME_BYTES + 1


def test_command_round_trip_and_no_implicit_version_or_fields(job, job_frame):
    assert decode_command(encode_command(job)) == job
    assert decode_command(encode_command(Cancel(job.id))) == Cancel(job.id)
    for patch, code in (
        ({"protocol_version": "1.1"}, ErrorCode.UNSUPPORTED_VERSION),
        ({"protocol_version": "2.0"}, ErrorCode.UNSUPPORTED_VERSION),
        ({"unknown_field": 1}, ErrorCode.INVALID_MESSAGE),
        ({"inputs": {"source": "C:/example.tif"}}, ErrorCode.INVALID_MESSAGE),
        ({"job_id": str(job.id).replace("-", "")}, ErrorCode.INVALID_MESSAGE),
    ):
        with pytest.raises(ContractError) as caught:
            decode_command(encode_frame({**decode_frame(job_frame), **patch}))
        assert caught.value.code == code


def test_golden_event_replay_only_exposes_result_after_exit(job, event_frames):
    lifecycle = JobLifecycle(job)
    for frame in event_frames:
        event = decode_event(frame)
        assert decode_event(encode_event(event)) == event
        lifecycle.accept_frame(frame)
    assert lifecycle.state == JobState.COMPLETED
    assert lifecycle.result is None
    assert lifecycle.finish(ExitCode.COMPLETED) == JobState.COMPLETED
    assert lifecycle.result.artifacts[0].spatial.horizontal_unit == "degree"


def test_cancel_wins_before_commit_and_acknowledgement_is_idempotent(job):
    lifecycle = JobLifecycle(job)
    command = Cancel(job.id)
    lifecycle.accept(WorkerEvent(EventKind.STARTED, job.id, 1, UTC_NOW))
    assert lifecycle.can_acknowledge_cancel(command)
    lifecycle.accept(WorkerEvent(EventKind.CANCEL_REQUESTED, job.id, 2, UTC_NOW))
    assert not lifecycle.can_acknowledge_cancel(command)
    with pytest.raises(ContractError):
        lifecycle.accept(WorkerEvent(EventKind.COMMIT_STARTED, job.id, 3, UTC_NOW))
    lifecycle.accept(WorkerEvent(EventKind.CANCELLED, job.id, 3, UTC_NOW))
    assert lifecycle.finish(ExitCode.CANCELLED) == JobState.CANCELLED
    assert lifecycle.result is None


def test_commit_wins_over_late_cancel(job, event_frames):
    lifecycle = JobLifecycle(job)
    for frame in event_frames[:6]:
        lifecycle.accept_frame(frame)
    assert lifecycle.state == JobState.COMMITTING
    assert not lifecycle.can_acknowledge_cancel(Cancel(job.id))
    for frame in event_frames[6:]:
        lifecycle.accept_frame(frame)
    assert lifecycle.finish(ExitCode.COMPLETED) == JobState.COMPLETED


@pytest.mark.parametrize(
    "fault", ["wrong-id", "gap", "duplicate-start", "extra-terminal", "bad-exit", "eof"]
)
def test_invalid_transport_cannot_be_used_to_publish_a_result(job, event_frames, fault):
    lifecycle = JobLifecycle(job)
    with pytest.raises(ContractError) as caught:
        if fault == "wrong-id":
            event = replace(decode_event(event_frames[0]), job_id=uuid4())
            lifecycle.accept_frame(encode_event(event))
        elif fault == "gap":
            lifecycle.accept_frame(event_frames[1])
        elif fault == "duplicate-start":
            lifecycle.accept_frame(event_frames[0])
            lifecycle.accept_frame(event_frames[0])
        elif fault == "eof":
            lifecycle.accept_frame(event_frames[0])
            lifecycle.finish(0)
        else:
            for frame in event_frames:
                lifecycle.accept_frame(frame)
            if fault == "extra-terminal":
                lifecycle.accept_frame(event_frames[-1])
            else:
                lifecycle.finish(1)
    assert caught.value.code == ErrorCode.TRANSPORT_FAILURE
    with pytest.raises(ContractError):
        lifecycle.finish(0)
    assert lifecycle.result is None


def test_progress_and_stage_transitions(job, event_frames):
    lifecycle = JobLifecycle(job)
    for frame in event_frames[:3]:
        lifecycle.accept_frame(frame)
    assert lifecycle.stage == "example"
    assert lifecycle.progress == 50
    for event in (
        WorkerEvent(EventKind.PROGRESS, job.id, 4, UTC_NOW, 49),
        WorkerEvent(EventKind.STAGE_COMPLETED, job.id, 4, UTC_NOW, "other"),
        WorkerEvent(EventKind.COMMIT_STARTED, job.id, 4, UTC_NOW),
    ):
        with pytest.raises(ContractError):
            lifecycle.accept(event)


def test_warning_and_failure_have_fixed_public_diagnostics(job, event_frames):
    warning = WorkerEvent(
        EventKind.WARNING, job.id, 2, UTC_NOW, WarningCode.PARTIAL_COVERAGE
    )
    assert decode_event(encode_event(warning)).diagnostic_message
    lifecycle = JobLifecycle(job)
    lifecycle.accept_frame(event_frames[0])
    secret = "private-token-example"
    failure = WorkerEvent(
        EventKind.FAILED, job.id, 2, UTC_NOW, ErrorCode.EXECUTION_FAILED
    )
    frame = encode_event(failure)
    with pytest.raises(ContractError) as caught:
        decode_event(encode_frame({**decode_frame(frame), "debug_secret": secret}))
    assert secret not in str(caught.value)
    assert secret.encode() not in frame
    assert (
        decode_event(frame).diagnostic_message
        == "The worker could not complete the operation."
    )
    lifecycle.accept_frame(frame)
    assert lifecycle.finish(ExitCode.FAILED) == JobState.FAILED


@pytest.mark.parametrize(
    "timestamp", ["2026-11-27T06:00:00+00:00", "2026-02-30T06:00:00Z"]
)
def test_event_requires_a_real_utc_timestamp(event_frames, timestamp):
    event = decode_frame(event_frames[0])
    with pytest.raises(ContractError) as caught:
        decode_event(encode_frame({**event, "timestamp": timestamp}))
    assert caught.value.code == ErrorCode.INVALID_MESSAGE


def test_result_has_an_independent_version(event_frames):
    event = decode_frame(event_frames[-1])
    event["result"]["result_version"] = "2.0"
    with pytest.raises(ContractError) as caught:
        decode_event(encode_frame(event))
    assert caught.value.code == ErrorCode.UNSUPPORTED_VERSION


def test_completed_result_must_include_announced_artifacts(job, event_frames):
    lifecycle = JobLifecycle(job)
    for frame in event_frames[:-1]:
        lifecycle.accept_frame(frame)
    event = decode_frame(event_frames[-1])
    event["result"]["artifacts"] = []
    with pytest.raises(ContractError) as caught:
        lifecycle.accept_frame(encode_frame(event))
    assert caught.value.code == ErrorCode.TRANSPORT_FAILURE
    assert lifecycle.result is None


def test_unknown_cancel_id_cannot_change_job(job, event_frames):
    lifecycle = JobLifecycle(job)
    lifecycle.accept_frame(event_frames[0])
    with pytest.raises(ContractError) as caught:
        lifecycle.can_acknowledge_cancel(Cancel(uuid4()))
    assert caught.value.code == ErrorCode.INVALID_MESSAGE
    assert lifecycle.state == JobState.RUNNING
