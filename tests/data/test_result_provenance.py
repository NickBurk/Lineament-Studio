import copy
import json
import shutil
import sqlite3
import subprocess
import sys
from contextlib import closing
from uuid import uuid4

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

from lineament_core.infrastructure.data.manifest import ProjectError, checksum
from lineament_core.infrastructure.data.project import Project
from lineament_core.infrastructure.data.provenance import validate_provenance
from lineament_core.infrastructure.gis.raster import SidecarError
from lineament_core.science.hillshade import Illumination


def _dem(path, offset=0):
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=11,
        height=9,
        count=1,
        crs="EPSG:32633",
        transform=Affine(2, 0.25, 500, 0.5, -2, 700),
        dtype="int16",
    ) as dst:
        dst.write(np.arange(99, dtype="int16").reshape(9, 11), 1)
        dst.scales = (0.5,)
        dst.offsets = (offset,)
        dst.set_band_unit(1, "m")
    return path


@pytest.fixture
def seeded(tmp_path):
    dem = _dem(tmp_path / "DEM.tif")
    project = Project.create(tmp_path / "project")
    key = project.add_dem(dem, "reference")
    return project, dem, key


def _compute(project, key, **kwargs):
    return project.register_result(
        source_id=key,
        job_id=str(uuid4()),
        light=Illumination(315, 1, 1),
        tile=4,
        **kwargs,
    )


def _reopen(root):
    code = """
import json
import sys
from lineament_core.infrastructure.data.project import Project
print(json.dumps(Project.open(sys.argv[1]).snapshot()))
"""
    return json.loads(subprocess.check_output([sys.executable, "-c", code, str(root)]))


def _crash(root, key, job, point):
    code = """
import os
import sys
from lineament_core.infrastructure.data.project import Project
from lineament_core.science.hillshade import Illumination
def kill(name):
    if name == sys.argv[4]:
        os._exit(73)
Project.open(sys.argv[1], checkpoint=kill).register_result(
    source_id=sys.argv[2], job_id=sys.argv[3], light=Illumination(135, 1, 1), tile=4)
"""
    assert (
        subprocess.run(
            [sys.executable, "-c", code, str(root), key, job, point]
        ).returncode
        == 73
    )


@pytest.mark.parametrize(
    "point,visible",
    [
        ("staged", False),
        ("before_prepared_commit", False),
        ("prepared_committed", True),
        ("artifact_promoted", True),
        ("manifest_staged", True),
        ("manifest_installed", True),
        ("catalog_transaction", True),
        ("catalog_committed", True),
    ],
)
def test_result_process_death(seeded, point, visible):
    project, dem, key = seeded
    first_id = _compute(project, key)
    original = project.snapshot()["results"][0]
    job = str(uuid4())
    _crash(project.root, key, job, point)
    state = _reopen(project.root)
    assert state == _reopen(project.root)
    assert original in state["results"]
    assert len(state["results"]) == 1 + visible
    new = [result for result in state["results"] if result["job_id"] == job]
    assert bool(new) == visible
    if new:
        assert new[0]["id"] != first_id
        assert new[0]["provenance"]["source_asset_id"] == key
        assert (
            new[0]["provenance"]["source_version_id"]
            == state["assets"][0]["source_version_id"]
        )
        assert new[0]["provenance"]["source_checksum"] == checksum(dem)
        assert new[0]["checksum"] == checksum(project.root / new[0]["path"])
    with closing(sqlite3.connect(project.root / "project.sqlite")) as db:
        ids = db.execute(
            "SELECT result_id FROM receipts WHERE result_id IS NOT NULL"
        ).fetchall()
        assert sorted(ids) == sorted((result["id"],) for result in state["results"])
        assert db.execute("SELECT count(*) FROM receipts").fetchone() == (2 + visible,)
        assert db.execute("SELECT count(*) FROM pending").fetchone() == (0,)


@pytest.mark.parametrize(
    "boundary,directory,pattern",
    [
        ("prepared_committed", "cache", "*.stage"),
        ("artifact_promoted", "results", "*.tif"),
    ],
)
def test_damaged_uncommitted_result_fails_closed(seeded, boundary, directory, pattern):
    project, _, key = seeded
    _compute(project, key)
    original = project.snapshot()["results"][0]
    _crash(project.root, key, str(uuid4()), boundary)
    (candidate,) = [
        p
        for p in (project.root / directory).glob(pattern)
        if p != project.root / original["path"]
    ]
    candidate.write_bytes(b"damaged")
    with pytest.raises(ProjectError, match="differs|damaged"):
        Project.open(project.root)
    assert checksum(project.root / original["path"]) == original["checksum"]
    assert candidate.read_bytes() == b"damaged"


def test_recovery_can_itself_be_interrupted(seeded):
    project, _, key = seeded
    _compute(project, key)
    _crash(project.root, key, str(uuid4()), "prepared_committed")
    code = """
import os
import sys
from lineament_core.infrastructure.data.project import Project
Project.open(sys.argv[1], checkpoint=lambda name: os._exit(74) if name == "manifest_installed" else None)
"""
    assert (
        subprocess.run([sys.executable, "-c", code, str(project.root)]).returncode == 74
    )
    state = _reopen(project.root)
    assert state == _reopen(project.root)
    assert len(state["results"]) == 2
    with closing(sqlite3.connect(project.root / "project.sqlite")) as db:
        assert db.execute(
            "SELECT count(*) FROM receipts WHERE result_id IS NOT NULL"
        ).fetchone() == (2,)


def test_relink_keeps_historical_provenance(seeded):
    project, dem, key = seeded
    _compute(project, key)
    original = project.snapshot()["results"][0]["provenance"]
    identical = dem.with_name("identical.tif")
    shutil.copyfile(dem, identical)
    project.relink(key, identical)
    assert (
        project.snapshot()["assets"][0]["source_version_id"]
        == original["source_version_id"]
    )
    changed = _dem(dem.with_name("changed.tif"), 100)
    with pytest.raises(ProjectError, match="confirmation"):
        project.relink(key, changed)
    project.relink(key, changed, accept_changed=True)
    state = _reopen(project.root)
    assert state["assets"][0]["source_version_id"] != original["source_version_id"]
    assert state["results"][0]["provenance"] == original


@pytest.mark.parametrize("change", ["bytes", "relink", "sidecar"])
def test_source_changes_during_processing_leave_no_intent(seeded, change):
    project, dem, key = seeded
    target = _dem(dem.with_name("next.tif"), 42)
    mutated = False

    def change_during_tile(_):
        nonlocal mutated
        if mutated:
            return
        mutated = True
        if change == "bytes":
            shutil.copyfile(target, dem)
        elif change == "relink":
            project.relink(key, target, accept_changed=True)
        else:
            dem.with_suffix(".tfw").write_text("1\n0\n0\n-1\n500\n700\n")

    with pytest.raises((ProjectError, SidecarError)):
        _compute(project, key, progress=change_during_tile)
    assert mutated and not project.snapshot()["results"]
    with closing(sqlite3.connect(project.root / "project.sqlite")) as db:
        assert db.execute("SELECT count(*) FROM pending").fetchone() == (0,)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_asset_id", "not-a-uuid"),
        ("source_version_id", "b805558d-6ed5-4535-8dcd-e2f9db164ce6"),
        ("source_checksum", "sha256:123"),
        ("output_checksum", "sha256:" + "1" * 64),
        ("band", 2),
        ("algorithm", "different"),
        ("algorithm_version", ""),
        ("parameters", {}),
        ("dependencies", {}),
        ("created_at", "2026-11-27T00:00:00"),
        ("source", {}),
        ("output", {}),
    ],
)
def test_strict_provenance(seeded, field, value):
    project, _, key = seeded
    _compute(project, key)
    state = project.snapshot()
    result = state["results"][0]
    record = copy.deepcopy(result["provenance"])
    record[field] = value
    with pytest.raises(ProjectError, match="Invalid result provenance"):
        validate_provenance(
            record,
            source_id=key,
            output_checksum=result["checksum"],
            bound_asset=state["assets"][0],
        )


def test_invalid_publication_provenance_leaves_no_intent(seeded):
    project, _, key = seeded
    with pytest.raises(ProjectError, match="Vertical units conflict"):
        project.register_result(
            source_id=key,
            job_id=str(uuid4()),
            light=Illumination(315, 0.3048, 1),
            tile=4,
        )
    assert not project.snapshot()["results"]
    with closing(sqlite3.connect(project.root / "project.sqlite")) as db:
        assert db.execute("SELECT count(*) FROM pending").fetchone() == (0,)


def test_selected_band_provenance_uses_actual_calibration(tmp_path):
    dem = tmp_path / "multiband.tif"
    with rasterio.open(
        dem,
        "w",
        driver="GTiff",
        width=9,
        height=7,
        count=2,
        crs="EPSG:32633",
        transform=Affine(2, 0, 500, 0, -2, 700),
        dtype="int16",
    ) as dst:
        dst.write(np.zeros((7, 9), dtype="int16"), 1)
        dst.write(np.arange(63, dtype="int16").reshape(7, 9), 2)
        dst.scales, dst.offsets = (1.0, 0.5), (0.0, 125.0)
        dst.set_band_unit(2, "m")
    project = Project.create(tmp_path / "project")
    key = project.add_dem(dem, "reference")
    _compute(project, key, band=2)
    result = project.snapshot()["results"][0]
    record = result["provenance"]
    assert (
        record["band"],
        record["source"]["band_scale"],
        record["source"]["band_offset"],
    ) == (2, 0.5, 125.0)
    assert record["output"]["band"] == 1 and record["output"]["vertical_unit"] is None
    record["output"]["transform"][0] += 1
    with pytest.raises(ProjectError, match="Incompatible Hillshade output"):
        validate_provenance(record, source_id=key, output_checksum=result["checksum"])


def test_legacy_manifest_is_rejected_without_rewrite(tmp_path):
    root = tmp_path / "project"
    Project.create(root)
    manifest = root / "project.lspx"
    legacy = manifest.read_bytes().replace(
        b'"format_version":"1.1"', b'"format_version":"1.0"'
    )
    manifest.write_bytes(legacy)
    with pytest.raises(ProjectError, match="Unsupported"):
        Project.open(root)
    assert manifest.read_bytes() == legacy
