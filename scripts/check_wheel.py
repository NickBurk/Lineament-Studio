"""Install the built wheel offline and verify it outside the checkout."""

import subprocess
import sys
import tempfile
import venv
from pathlib import Path

SMOKE = """
import importlib
import pkgutil
import sys
from importlib.metadata import distribution
from pathlib import Path

import lineament_core

assert Path(lineament_core.__file__).is_relative_to(sys.prefix)
assert sys.version_info[:2] == (3, 11)
assert not distribution("lineament-core").requires
for module in pkgutil.walk_packages(lineament_core.__path__, "lineament_core."):
    importlib.import_module(module.name)
    print(module.name)
print(sys.version)
"""

(wheel,) = sorted(Path("dist").glob("lineament_core-*.whl"))
with tempfile.TemporaryDirectory(prefix="lineament-wheel-") as directory:
    clean = Path(directory)
    venv.EnvBuilder(with_pip=True).create(clean)
    python = clean / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run(
        [
            str(python),
            "-I",
            "-m",
            "pip",
            "install",
            "--no-index",
            "--no-cache-dir",
            str(wheel.resolve()),
        ],
        cwd=clean,
        check=True,
    )
    subprocess.run([str(python), "-I", "-c", SMOKE], cwd=clean, check=True)
