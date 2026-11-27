import sqlite3
import subprocess
import sys

import pytest

from lineament_core.infrastructure.data.manifest import ProjectError, internal
from lineament_core.infrastructure.data.project import Project, project_lock


@pytest.mark.parametrize(
    "point,published",
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
def test_process_death_and_repeated_reopen(tmp_path, point, published):
    source = tmp_path / "terrain.tif"
    source.write_bytes(b"independent storage fixture")
    root = tmp_path / "project"
    key = Project.create(root).snapshot()["project_id"]
    code = """
import os
import sys
from lineament_core.infrastructure.data.project import Project
def fault(name):
    if name == sys.argv[3]:
        os._exit(71)
Project.open(sys.argv[1], checkpoint=fault).add_dem(sys.argv[2], "copy", lambda _: {})
"""
    result = subprocess.run([sys.executable, "-c", code, str(root), str(source), point])
    assert result.returncode == 71
    first = Project.open(root).snapshot()
    assert first == Project.open(root).snapshot()
    assert first["project_id"] == key
    assert len(first["assets"]) == published
    assert len(list((root / "inputs/dem").iterdir())) == published
    assert source.read_bytes() == b"independent storage fixture"


def test_missing_drift_and_relink(tmp_path):
    source = tmp_path / "élevation.tif"
    source.write_bytes(b"source")
    project = Project.create(tmp_path / "project")
    key = project.add_dem(source, "reference", lambda _: {"band": 1})
    moved = source.rename(tmp_path / "new.tif")
    assert project.source(key)[1] == "missing"
    moved.write_bytes(b"changed")
    with pytest.raises(ProjectError, match="confirmation"):
        project.relink(key, moved, lambda _: {"band": 1})
    project.relink(key, moved, lambda _: {"band": 1}, accept_changed=True)
    assert project.source(key) == (moved, "available")
    moved.write_bytes(b"changed again")
    assert project.source(key)[1] == "changed"
    project.close()
    with pytest.raises(ProjectError, match="closed"):
        project.snapshot()


@pytest.mark.parametrize(
    "uri", ["../escape", "a/../../b", "C:/x", "x:stream", "aux.txt", "x\\y"]
)
def test_unsafe_internal_paths(tmp_path, uri):
    with pytest.raises(ProjectError):
        internal(tmp_path, uri)


def test_unsupported_manifest_is_preserved(tmp_path):
    root = tmp_path / "project"
    Project.create(root)
    path = root / "project.lspx"
    payload = path.read_bytes().replace(
        b'"format_version":"1.0"', b'"format_version":"9.0"'
    )
    path.write_bytes(payload)
    with pytest.raises(ProjectError, match="Unsupported"):
        Project.open(root)
    assert path.read_bytes() == payload


def test_concurrent_access_is_rejected(tmp_path):
    root = tmp_path / "project"
    Project.create(root)
    with project_lock(root / ".project.lock"), pytest.raises(OSError):
        Project.open(root)


def test_catalog_damage_fails_closed(tmp_path):
    root = tmp_path / "project"
    project = Project.create(root)
    manifest = (root / "project.lspx").read_bytes()
    project.close()
    (root / "project.sqlite").write_bytes(b"not sqlite")
    with pytest.raises(sqlite3.DatabaseError):
        Project.open(root)
    assert (root / "project.lspx").read_bytes() == manifest


def test_failed_recovery_is_replayable(tmp_path):
    root = tmp_path / "project"
    source = tmp_path / "source.tif"
    source.write_bytes(b"source")
    Project.create(root)

    def stop(name):
        if name == "prepared_committed":
            raise OSError("boundary")

    with pytest.raises(OSError, match="boundary"):
        Project.open(root, checkpoint=stop).add_dem(source, "copy", lambda _: {})

    def sharing(name):
        if name == "manifest_staged":
            raise PermissionError("sharing violation")

    with pytest.raises(PermissionError):
        Project.open(root, checkpoint=sharing)
    assert len(Project.open(root).snapshot()["assets"]) == 1


def test_no_space_leaves_old_manifest(tmp_path, monkeypatch):
    root = tmp_path / "project"
    source = tmp_path / "source.tif"
    source.write_bytes(b"source")
    project = Project.create(root)
    # Supply a disk usage result with zero free bytes.
    from types import SimpleNamespace

    monkeypatch.setattr("shutil.disk_usage", lambda _: SimpleNamespace(free=0))
    with pytest.raises(OSError, match="disk space"):
        project.add_dem(source, "copy", lambda _: {})
    assert Project.open(root).snapshot()["assets"] == []
