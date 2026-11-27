from io import BytesIO

import pytest

from lineament_core.infrastructure.execution import Cancelled, copy_stream, digest_file


@pytest.mark.parametrize("operation", ["copy", "checksum"])
def test_cancel_between_bounded_reads(tmp_path, operation):
    source = tmp_path / "large.bin"
    source.write_bytes(b"x" * (3 * 1024**2))
    calls = 0

    def cancelled():
        nonlocal calls
        calls += 1
        return calls == 3

    with pytest.raises(Cancelled):
        if operation == "checksum":
            digest_file(source, cancelled)
        else:
            out = BytesIO()
            with source.open("rb") as inp:
                copy_stream(inp, out, cancelled)
            pytest.fail("copy must stop")
    assert calls == 3
    if operation == "copy":
        assert len(out.getvalue()) == 1024**2
