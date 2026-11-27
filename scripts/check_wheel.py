"""Install the built wheel offline and verify it outside the checkout."""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path

(wheel,) = sorted(Path("dist").glob("lineament_core-*.whl"))
with tempfile.TemporaryDirectory(prefix="lineament-wheel-") as directory:
    clean = Path(directory)
    venv.EnvBuilder(with_pip=True).create(clean)
    python = clean / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run(
        [str(python), "-I", "-m", "pip", "install", "--no-index", str(wheel.resolve())],
        cwd=clean,
        check=True,
    )
    subprocess.run(
        [
            str(python),
            "-I",
            "-c",
            "import lineament_core, sys; from pathlib import Path; "
            "assert Path(lineament_core.__file__).is_relative_to(sys.prefix); "
            "assert sys.version_info[:2] == (3, 11); print(sys.version)",
        ],
        cwd=clean,
        check=True,
    )
