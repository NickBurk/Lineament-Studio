import subprocess
import sys
from pathlib import Path

import pytest

from lineament_core.diagnostics import ContractError, ErrorCode
from lineament_core.lifecycle import ExitCode, JobLifecycle, JobState
from lineament_core.wire import (
    Cancel,
    decode_frame,
    decode_version_offer,
    encode_command,
    encode_frame,
    negotiate_version,
)

PROBE = Path(__file__).with_name("fixtures") / "worker_probe.py"


def worker(mode, payload=b""):
    return subprocess.run(
        [sys.executable, "-I", str(PROBE), mode],
        input=payload,
        capture_output=True,
        timeout=15,
        check=False,
    )


def replay(job, completed):
    lifecycle = JobLifecycle(job)
    for frame in completed.stdout.splitlines(keepends=True):
        lifecycle.accept_frame(frame)
    lifecycle.finish(completed.returncode)
    return lifecycle


def test_subprocess_version_preflight_and_completed_exchange(job, job_frame):
    preflight = worker("describe")
    assert preflight.returncode == 0
    assert negotiate_version(decode_version_offer(preflight.stdout)) == "1.0"
    result = worker("run", job_frame)
    assert len(result.stderr) == 256 * 1024
    assert replay(job, result).result.job_id == job.id


def test_subprocess_cancel_twice(job, job_frame):
    cancel = encode_command(Cancel(job.id))
    result = worker("run", job_frame + cancel + cancel)
    assert len(result.stdout.splitlines()) == 3
    assert replay(job, result).state == JobState.CANCELLED


def test_subprocess_malformed_request_and_early_exit(job, job_frame):
    wrong = {**decode_frame(job_frame), "protocol_version": "2.0"}
    result = worker("run", encode_frame(wrong))
    assert result.returncode == ExitCode.INVALID_REQUEST
    assert not result.stdout
    with pytest.raises(ContractError) as caught:
        replay(job, worker("crash", job_frame))
    assert caught.value.code == ErrorCode.TRANSPORT_FAILURE
    assert replay(job, worker("run", job_frame)).state == JobState.COMPLETED
