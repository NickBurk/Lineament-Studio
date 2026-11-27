"""Project storage with a persisted, replayable publication intent."""

import json
import os
import shutil
import sqlite3
import tempfile
from contextlib import closing, contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..gis.raster import SidecarError, inspect_dem, require_self_contained
from .provenance import raster_metadata, validate_provenance

from .manifest import (
    DIRECTORIES,
    FORMAT,
    SCHEMA,
    VERSION,
    ProjectError,
    checksum,
    decode,
    encode,
    external,
    identity,
    internal,
    read,
)


def now():
    return datetime.now(UTC).isoformat()


def write(path, data):
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def project_lock(path):
    with path.open("r+b") as stream:
        if os.name == "nt":
            import msvcrt

            msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield  # Closing the handle also releases the lock after process termination.


def connect(path, *, create=False):
    uri = path.resolve().as_uri() + ("?mode=rwc" if create else "?mode=rw")
    db = sqlite3.connect(uri, uri=True, timeout=3)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        if create:
            db.execute("PRAGMA journal_mode=WAL")
        if db.execute("PRAGMA journal_mode").fetchone()[0] != "wal":
            raise ProjectError("Unexpected SQLite journal mode")
        db.execute("PRAGMA synchronous=FULL")
        return db
    except BaseException:
        db.close()
        raise


DDL = """
CREATE TABLE project(id TEXT PRIMARY KEY, manifest BLOB NOT NULL);
CREATE TABLE assets(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES project(id));
CREATE TABLE results(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES project(id),
                     source_id TEXT NOT NULL REFERENCES assets(id), job_id TEXT NOT NULL,
                     path TEXT NOT NULL UNIQUE, checksum TEXT NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE pending(slot INTEGER PRIMARY KEY CHECK(slot=1), publication_id TEXT NOT NULL,
                     before BLOB NOT NULL, after BLOB NOT NULL, payload TEXT NOT NULL);
CREATE TABLE receipts(publication_id TEXT PRIMARY KEY, relink_json TEXT,
                      result_id TEXT UNIQUE REFERENCES results(id));
CREATE TABLE migrations(version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL);
PRAGMA user_version=2;
"""


class Project:
    """Each operation acquires the same project lock and verifies current state."""

    def __init__(self, root, *, checkpoint=None):
        supplied = Path(root).absolute()
        if (
            supplied.is_symlink()
            or getattr(supplied.stat(), "st_file_attributes", 0) & 0x400
        ):
            raise ProjectError("Project root cannot be a link")
        self.root = supplied.resolve()
        self.closed = False
        self.checkpoint = checkpoint or (lambda name: None)

    @classmethod
    def create(cls, root, *, project_crs=None, storage_policy="mixed"):
        root = Path(root).absolute()
        if root.exists() or root.is_symlink():
            raise FileExistsError(root)
        with tempfile.TemporaryDirectory(
            dir=root.parent, prefix=".lineament-create-"
        ) as temp:
            stage = Path(temp) / "project"
            stage.mkdir()
            for name in DIRECTORIES:
                (stage / name).mkdir(parents=True, exist_ok=True)
            write(stage / ".project.lock", b"\0")
            ts = now()
            manifest = encode(
                dict(
                    format_id=FORMAT,
                    format_version=VERSION,
                    schema_version=SCHEMA,
                    project_id=str(uuid4()),
                    application_version="0.1.0",
                    created_at=ts,
                    modified_at=ts,
                    project_crs=project_crs,
                    storage_policy=storage_policy,
                    catalog_uri="project.sqlite",
                    assets=[],
                    default_profiles={},
                )
            )
            project = decode(manifest, stage)
            write(stage / "project.lspx", manifest)
            with closing(connect(stage / "project.sqlite", create=True)) as db, db:
                db.executescript(DDL)
                db.execute(
                    "INSERT INTO project VALUES(?,?)", (project["project_id"], manifest)
                )
                db.execute("INSERT INTO migrations VALUES(?,?)", (int(SCHEMA), ts))
            stage.rename(root)
        return cls.open(root)

    @classmethod
    def open(cls, root, *, checkpoint=None):
        project = cls(root, checkpoint=checkpoint)
        with project._access():
            pass
        return project

    def close(self):
        self.closed = True

    @contextmanager
    def _access(self):
        if self.closed:
            raise ProjectError("Project is closed")
        for name in DIRECTORIES:
            if not internal(self.root, name).is_dir():
                raise ProjectError(f"Missing project directory: {name}")
        manifest = internal(self.root, "project.lspx")
        with project_lock(internal(self.root, ".project.lock")):
            current = read(manifest, self.root)
            project = decode(current, self.root)
            catalog = internal(self.root, "project.sqlite")
            for suffix in ("-wal", "-shm", "-journal"):
                internal(self.root, "project.sqlite" + suffix)
            with closing(connect(catalog)) as db:
                if db.execute("PRAGMA user_version").fetchone() != (int(SCHEMA),):
                    raise ProjectError("Unsupported catalog version")
                row = db.execute("SELECT id, manifest FROM project").fetchall()
                if len(row) != 1 or row[0][0] != project["project_id"]:
                    raise ProjectError(
                        "Manifest and catalog project identities disagree"
                    )
                pending = db.execute(
                    "SELECT publication_id,before,after,payload FROM pending"
                ).fetchone()
                if pending:
                    self._recover(db, row[0][1], current, *pending)
                    current = read(manifest, self.root)
                    project = decode(current, self.root)
                elif row[0][1] != current:
                    raise ProjectError(
                        "Manifest and catalog disagree without recovery intent"
                    )
                indexed = {
                    row[0]
                    for row in db.execute(
                        "SELECT id FROM assets WHERE project_id=?",
                        (project["project_id"],),
                    )
                }
                if (
                    indexed != {asset["asset_id"] for asset in project["assets"]}
                    or db.execute("PRAGMA foreign_key_check").fetchone()
                    or db.execute(
                        "SELECT 1 FROM results r LEFT JOIN receipts p ON p.result_id=r.id "
                        "WHERE p.result_id IS NULL LIMIT 1"
                    ).fetchone()
                ):
                    raise ProjectError("Catalog projection is inconsistent")
                yield db, current, project

    def _recover(self, db, indexed, current, operation, before, after, data):
        identity(operation)
        old = decode(before, self.root)
        new = decode(after, self.root)
        if (
            old["project_id"] != new["project_id"]
            or indexed != before
            or current not in (before, after)
        ):
            raise ProjectError("Unrecognized publication state")
        item = json.loads(data)
        if encode(item).decode() != data:
            raise ProjectError("Noncanonical publication intent")
        result = item.get("result")
        if result is not None:
            source_id = identity(result["source_id"])
            identity(result["job_id"])
            asset = next((a for a in new["assets"] if a["asset_id"] == source_id), None)
            if (
                asset is None
                or item["file"][0] != f"results/{identity(result['id'])}.tif"
            ):
                raise ProjectError("Inconsistent result publication intent")
            validate_provenance(
                result["provenance"],
                source_id=source_id,
                output_checksum=item["file"][1],
                bound_asset=asset,
            )
        if item.get("file"):
            uri, digest = item["file"]
            if not uri.startswith(("inputs/dem/", "results/")):
                raise ProjectError("Unsafe publication destination")
            final = internal(self.root, uri)
            stage = internal(self.root, f"cache/{operation}.stage")
            require_self_contained(final)
            require_self_contained(stage)
            if final.exists():
                if checksum(final) != digest:
                    raise ProjectError("Publication target differs from intent")
            else:
                if not stage.is_file() or checksum(stage) != digest:
                    raise ProjectError("Publication staging is missing or damaged")
                os.link(stage, final)
            self.checkpoint("artifact_promoted")
        if current != after:
            temp = internal(self.root, f"cache/{operation}.manifest")
            if temp.exists():
                temp.unlink()
            write(temp, after)
            self.checkpoint("manifest_staged")
            temp.replace(internal(self.root, "project.lspx"))
        self.checkpoint("manifest_installed")
        with db:
            for asset in new["assets"]:
                db.execute(
                    "INSERT OR IGNORE INTO assets VALUES(?,?)",
                    (asset["asset_id"], new["project_id"]),
                )
            if (result := item.get("result")) is not None:
                db.execute(
                    "INSERT INTO results VALUES(?,?,?,?,?,?,?)",
                    (
                        result["id"],
                        new["project_id"],
                        result["source_id"],
                        result["job_id"],
                        *item["file"],
                        encode(result["provenance"]).decode(),
                    ),
                )
            db.execute(
                "UPDATE project SET manifest=? WHERE id=?", (after, new["project_id"])
            )
            db.execute(
                "INSERT INTO receipts VALUES(?,?,?)",
                (
                    operation,
                    json.dumps(item.get("relink")),
                    result["id"] if result else None,
                ),
            )
            db.execute("DELETE FROM pending")
            self.checkpoint("catalog_transaction")
        self.checkpoint("catalog_committed")
        self._cleanup(operation)

    def _cleanup(self, operation):
        for suffix in ("stage", "manifest"):
            internal(self.root, f"cache/{operation}.{suffix}").unlink(missing_ok=True)

    def _publish(
        self,
        db,
        before,
        project,
        *,
        source=None,
        uri=None,
        validator=None,
        result=None,
        relink=None,
        expected=None,
        before_intent=None,
    ):
        project["modified_at"] = now()
        after = encode(project)
        decode(after, self.root)
        operation = str(uuid4())
        stage = internal(self.root, f"cache/{operation}.stage")
        item = {"result": result, "relink": relink}
        intent_started = False
        try:
            if source is not None:
                if source.stat().st_size > shutil.disk_usage(self.root).free:
                    raise OSError("Insufficient disk space for staged copy")
                with source.open("rb") as inp, stage.open("xb") as out:
                    shutil.copyfileobj(inp, out)
                    out.flush()
                    os.fsync(out.fileno())
                digest = checksum(stage)
                if expected is not None and expected != digest:
                    raise ProjectError("Source changed while copying")
                if validator:
                    validator(stage)
                item["file"] = [uri, digest]
            self.checkpoint("staged")
            if result is not None:
                validate_provenance(
                    result["provenance"],
                    source_id=result["source_id"],
                    output_checksum=item["file"][1],
                )
            if before_intent:
                before_intent()
            intent_started = True
            with db:
                db.execute(
                    "INSERT INTO pending VALUES(1,?,?,?,?)",
                    (operation, before, after, encode(item).decode()),
                )
                self.checkpoint("before_prepared_commit")
            self.checkpoint("prepared_committed")
            observed = db.execute(
                "SELECT publication_id,before,after,payload FROM pending"
            ).fetchone()
            if observed != (operation, before, after, encode(item).decode()):
                raise ProjectError("Committed intent could not be verified")
            self._recover(db, before, before, *observed)
        except BaseException:
            if not intent_started:
                self._cleanup(operation)
            raise

    def snapshot(self):
        with self._access() as (db, _, project):
            results = db.execute(
                "SELECT id,source_id,job_id,path,checksum,provenance FROM results ORDER BY id"
            )
            project["results"] = [
                dict(
                    id=i,
                    source_id=s,
                    job_id=j,
                    path=p,
                    checksum=c,
                    provenance=self._read_provenance(v, s, c),
                )
                for i, s, j, p, c, v in results
            ]
            for result in project["results"]:
                path = internal(self.root, result["path"])
                require_self_contained(path)
                if not path.is_file() or checksum(path) != result["checksum"]:
                    raise ProjectError("Published raster is missing or damaged")
            return project

    @staticmethod
    def _read_provenance(raw, source_id, digest):
        record = json.loads(raw)
        if (
            validate_provenance(
                record, source_id=source_id, output_checksum=digest
            ).decode()
            != raw
        ):
            raise ProjectError("Noncanonical result provenance")
        return record

    def save(self, *, default_profiles):
        with self._access() as (db, before, project):
            project["default_profiles"] = default_profiles
            self._publish(db, before, project)

    def add_dem(self, source, mode, inspect=inspect_dem):
        if mode not in ("reference", "copy"):
            raise ProjectError("Expected Reference or Copy")
        source = external(str(Path(source).absolute()))
        with self._access() as (db, before, project):
            key = str(uuid4())
            uri = str(source) if mode == "reference" else f"inputs/dem/{key}.tif"
            require_self_contained(source)
            digest = checksum(source)
            metadata = inspect(source)
            require_self_contained(source)
            if checksum(source) != digest:
                raise ProjectError("Source changed during inspection")
            if metadata.get("sidecars"):
                raise ProjectError("A self-contained GeoTIFF is required")
            project["assets"].append(
                dict(
                    asset_id=key,
                    source_version_id=str(uuid4()),
                    role="primary_dem",
                    storage_mode=mode,
                    uri=uri,
                    checksum=digest,
                    metadata=metadata,
                )
            )
            self._publish(
                db,
                before,
                project,
                source=source if mode == "copy" else None,
                uri=uri,
                validator=inspect,
                expected=digest,
            )
            return key

    def _asset_path(self, asset):
        if asset["storage_mode"] == "reference":
            return external(asset["uri"])
        return internal(self.root, asset["uri"])

    def source(self, key):
        with self._access() as (_, _, project):
            asset = next((a for a in project["assets"] if a["asset_id"] == key), None)
            if asset is None:
                raise ProjectError("Unknown asset")
            path = self._asset_path(asset)
            try:
                digest = checksum(path)
                require_self_contained(path)
            except SidecarError:
                return path, "unsupported_sidecars"
            except FileNotFoundError:
                return path, "missing"
            except OSError:
                return path, "unavailable"
            return path, "changed" if asset["checksum"] not in (
                None,
                digest,
            ) else "available"

    def relink(self, key, path, inspect=inspect_dem, *, accept_changed=False):
        path = external(str(Path(path).absolute()))
        with self._access() as (db, before, project):
            asset = next((a for a in project["assets"] if a["asset_id"] == key), None)
            if asset is None or asset["storage_mode"] != "reference":
                raise ProjectError("Only external references can be relinked")
            require_self_contained(path)
            digest = checksum(path)
            metadata = inspect(path)
            require_self_contained(path)
            if metadata.get("sidecars"):
                raise SidecarError("A self-contained GeoTIFF is required")
            if checksum(path) != digest:
                raise ProjectError("Candidate changed during inspection")
            if digest != asset["checksum"] and not accept_changed:
                raise ProjectError("Relink checksum differs and requires confirmation")
            version = (
                asset["source_version_id"]
                if digest == asset["checksum"]
                else str(uuid4())
            )
            event = dict(
                previous_source_version_id=asset["source_version_id"],
                source_version_id=version,
                asset_id=key,
                previous_uri=asset["uri"],
                previous_checksum=asset["checksum"],
                uri=str(path),
                checksum=digest,
            )
            asset.update(
                uri=str(path),
                checksum=digest,
                metadata=metadata,
                source_version_id=version,
            )
            self._publish(db, before, project, relink=event)

    def register_result(
        self,
        *,
        source_id,
        job_id,
        light,
        band=1,
        tile=512,
        cancelled=lambda: False,
        progress=lambda fraction: None,
    ):
        """Compute and publish Hillshade from a verified private byte snapshot."""
        from dataclasses import asdict

        import numpy
        import rasterio

        from lineament_core.science.hillshade import (
            VERSION,
            Cancelled,
            Illumination,
            run,
        )

        identity(source_id)
        identity(job_id)
        if type(light) is not Illumination:
            raise ProjectError("Expected normalized Hillshade parameters")
        with self._access() as (_, _, project):
            asset = self._find_asset(project, source_id)
            original = self._asset_path(asset)
        # The temporary workspace is private to this run. GDAL only reads this copy.
        with tempfile.TemporaryDirectory(prefix="lineament-hillshade-") as tmp:
            snapshot = Path(tmp) / "input.tif"
            require_self_contained(original)
            if original.stat().st_size > shutil.disk_usage(tmp).free:
                raise OSError("Insufficient disk space for verified DEM snapshot")
            shutil.copyfile(original, snapshot)
            if checksum(snapshot) != asset["checksum"]:
                raise ProjectError(
                    "Input snapshot differs from declared source content"
                )
            self._verify_source(asset)
            source = raster_metadata(inspect_dem(snapshot, band=band))
            if not source["vertical_unit"]:
                source["vertical_unit"] = "explicit metres-per-unit"
            output = Path(tmp) / "hillshade.tif"
            run(
                snapshot,
                output,
                light,
                band=band,
                tile=tile,
                cancelled=cancelled,
                progress=lambda fraction: progress(fraction) if fraction < 1 else None,
            )
            if checksum(snapshot) != asset["checksum"]:
                raise ProjectError("Input snapshot changed during processing")
            digest = checksum(output)
            provenance = dict(
                schema_version="1",
                source_asset_id=source_id,
                source_checksum=asset["checksum"],
                source_version_id=asset["source_version_id"],
                source=source,
                band=band,
                created_at=now(),
                algorithm="hillshade",
                algorithm_version=VERSION,
                parameters=asdict(light),
                output=raster_metadata(inspect_dem(output)),
                output_checksum=digest,
                dependencies=dict(
                    rasterio=rasterio.__version__,
                    gdal=rasterio.__gdal_version__,
                    proj=rasterio.__proj_version__,
                    numpy=numpy.__version__,
                ),
            )
            with self._access() as (db, before, project):
                current = self._find_asset(project, source_id)
                validate_provenance(
                    provenance,
                    source_id=source_id,
                    output_checksum=digest,
                    bound_asset=current,
                )

                def check_before_intent():
                    if cancelled():
                        raise Cancelled()
                    self._verify_source(current)

                key = str(uuid4())
                self._publish(
                    db,
                    before,
                    project,
                    source=output,
                    uri=f"results/{key}.tif",
                    expected=digest,
                    validator=require_self_contained,
                    before_intent=check_before_intent,
                    result=dict(
                        id=key,
                        source_id=source_id,
                        job_id=job_id,
                        provenance=provenance,
                    ),
                )
        progress(1.0)
        return key

    @staticmethod
    def _find_asset(project, source_id):
        for asset in project["assets"]:
            if asset["asset_id"] == source_id:
                return asset
        raise ProjectError("Unknown source asset")

    def _verify_source(self, asset):
        path = self._asset_path(asset)
        require_self_contained(path)
        if checksum(path) != asset["checksum"]:
            raise ProjectError("Source content changed during processing")
        require_self_contained(path)
