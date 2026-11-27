import json
import subprocess
import sys
from pathlib import Path


def test_smoke_reopens_in_fresh_process(tmp_path):
    command = Path(__file__).resolve().parents[2] / "scripts/vertical_slice.py"
    state = json.loads(
        subprocess.check_output([sys.executable, str(command), str(tmp_path)])
    )
    assert state["fresh_process_reopen"]
    assert state["preflight"]["valid_percent"] == 100
    assert (
        state["results"][0]["provenance"]["source_checksum"] == state["original_sha256"]
    )
