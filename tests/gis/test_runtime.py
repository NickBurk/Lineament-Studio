"""Exercise the candidate wheel stack, including GDAL's GeoPackage raster driver."""

import json
import os
import sqlite3
import subprocess
from contextlib import closing
from pathlib import Path

import numpy as np
import rasterio
from rasterio._env import get_proj_data_search_paths
from rasterio.shutil import copy
from rasterio.transform import from_origin
from rasterio.warp import transform


def test_offline_runtime_inventory_and_geopackage(tmp_path):
    pixels = np.arange(64, dtype="uint8").reshape((8, 8))
    source, gpkg = tmp_path / "grid.tif", tmp_path / "grid.gpkg"
    with rasterio.Env(PROJ_NETWORK="OFF") as env:
        drivers = env.drivers()
        assert {"GTiff", "GPKG"} <= drivers.keys()
        with rasterio.open(
            source,
            "w",
            driver="GTiff",
            width=8,
            height=8,
            count=1,
            crs="EPSG:3857",
            transform=from_origin(0, 800, 100, 100),
            dtype="uint8",
        ) as ds:
            ds.write(pixels, 1)
        copy(source, gpkg, driver="GPKG", TILE_FORMAT="PNG")
        with rasterio.open(gpkg) as ds:
            assert ds.crs.to_epsg() == 3857
            assert ds.transform == from_origin(0, 800, 100, 100)
            np.testing.assert_array_equal(ds.read(1), pixels)
        with closing(sqlite3.connect(gpkg)) as db:
            assert db.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        x, y = transform("EPSG:4326", "EPSG:3857", [1.0], [0.0])
        np.testing.assert_allclose((x[0], y[0]), (111319.49079327357, 0.0), atol=1e-7)
        proj_paths = [Path(p) for p in get_proj_data_search_paths()]
        databases = [p / "proj.db" for p in proj_paths if (p / "proj.db").is_file()]
        assert databases
        with closing(
            sqlite3.connect(databases[0].as_uri() + "?mode=ro", uri=True)
        ) as db:
            metadata = dict(db.execute("SELECT key,value FROM metadata"))
        assert "DATABASE.LAYOUT.VERSION.MAJOR" in metadata
        native = []
        if os.name == "nt":
            native = subprocess.check_output(
                [
                    "powershell",
                    "-NoProfile",
                    "-NonInteractive",
                    "-Command",
                    f"(Get-Process -Id {os.getpid()}).Modules | Select-Object -ExpandProperty FileName",
                ],
                text=True,
                encoding="utf-8",
                errors="replace",
            ).splitlines()
            gis_native = [
                p
                for p in native
                if any(
                    part in Path(p).name.lower()
                    for part in ("gdal", "proj_", "proj-", "geos")
                )
            ]
            assert gis_native
            assert all(
                "site-packages" in p.lower() and "qgis" not in p.lower()
                for p in gis_native
            )
        print(
            json.dumps(
                dict(
                    gdal=rasterio.__gdal_version__,
                    proj=rasterio.__proj_version__,
                    numpy=np.__version__,
                    sqlite=sqlite3.sqlite_version,
                    proj_db=str(databases[0]),
                    proj_metadata=metadata,
                    grid_resources=sorted(
                        p.name for p in databases[0].parent.iterdir()
                    ),
                    drivers=sorted(drivers),
                    native_paths=native,
                )
            )
        )
