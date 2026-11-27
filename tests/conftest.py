from pathlib import Path

import pytest

from lineament_core.application import Job
from lineament_core.wire import decode_command

FIXTURES = Path(__file__).with_name("fixtures")


@pytest.fixture
def job_frame() -> bytes:
    # Git may check out JSONL fixtures with CRLF on Windows.
    return (FIXTURES / "job.jsonl").read_bytes()


@pytest.fixture
def job(job_frame) -> Job:
    request = decode_command(job_frame)
    assert isinstance(request, Job)
    return request


@pytest.fixture
def event_frames() -> list[bytes]:
    return (FIXTURES / "completed.jsonl").read_bytes().splitlines(keepends=True)
