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
from rasterio.transform import Affine
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
            transform=Affine(100, 0, 0, 0, -100, 800),
            dtype="uint8",
        ) as ds:
            ds.write(pixels, 1)
        copy(source, gpkg, driver="GPKG", TILE_FORMAT="PNG")
        with rasterio.open(gpkg) as ds:
            assert ds.crs.to_epsg() == 3857
            assert ds.transform == Affine(100, 0, 0, 0, -100, 800)
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


def test_vector_geopackage_with_same_gdal(tmp_path):
    """Use the existing loaded GDAL, avoiding a second native stack."""
    import ctypes as c

    package = Path(rasterio.__file__).parent
    libraries = [
        p
        for directory in (package / ".libs", package.parent / "rasterio.libs", package)
        if directory.is_dir()
        for p in directory.iterdir()
        if "gdal" in p.name.lower() and (".so" in p.name or p.suffix == ".dll")
    ]
    if os.name == "nt" and not libraries:
        loaded = subprocess.check_output(
            [
                "powershell",
                "-NoProfile",
                "-NonInteractive",
                "-Command",
                f"(Get-Process -Id {os.getpid()}).Modules | Select-Object -ExpandProperty FileName",
            ],
            text=True,
        ).splitlines()
        libraries = [
            Path(p)
            for p in loaded
            if "gdal" in Path(p).name.lower() and "site-packages" in p.lower()
        ]
    assert len(libraries) == 1, libraries
    gdal = c.CDLL(str(libraries[0]))

    def api(name, result, *args):
        fn = getattr(gdal, name)
        fn.restype, fn.argtypes = result, args
        return fn

    ptr, string, integer = c.c_void_p, c.c_char_p, c.c_int
    open_dataset = api("GDALOpenEx", ptr, string, c.c_uint, ptr, ptr, ptr)
    close_dataset = api("GDALClose", None, ptr)
    options_new = api("GDALVectorTranslateOptionsNew", ptr, c.POINTER(string), ptr)
    options_free = api("GDALVectorTranslateOptionsFree", None, ptr)
    translate = api(
        "GDALVectorTranslate",
        ptr,
        string,
        ptr,
        integer,
        c.POINTER(ptr),
        ptr,
        c.POINTER(integer),
    )
    get_layer = api("GDALDatasetGetLayer", ptr, ptr, integer)
    count = api("OGR_L_GetFeatureCount", c.c_longlong, ptr, integer)
    geojson = tmp_path / "point.geojson"
    geojson.write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [12, 55]},
                        "properties": {"label": "control"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    output = tmp_path / "контроль.gpkg"
    with rasterio.Env(PROJ_NETWORK="OFF"):
        source = open_dataset(str(geojson).encode("utf-8"), 4, None, None, None)
        assert source
        opts = options_new((string * 4)(b"-f", b"GPKG", b"-overwrite", None), None)
        try:
            assert opts
            failed = integer()
            written = translate(
                str(output).encode("utf-8"),
                None,
                1,
                (ptr * 1)(source),
                opts,
                c.byref(failed),
            )
            assert written and not failed.value
            close_dataset(written)
        finally:
            if opts:
                options_free(opts)
            close_dataset(source)
        reopened = open_dataset(str(output).encode("utf-8"), 4, None, None, None)
        assert reopened
        try:
            layer = get_layer(reopened, 0)
            assert layer and count(layer, 1) == 1
        finally:
            close_dataset(reopened)
    with closing(sqlite3.connect(output)) as db:
        assert db.execute('SELECT label FROM "point"').fetchone() == ("control",)
        assert db.execute(
            "SELECT geometry_type_name,srs_id FROM gpkg_geometry_columns"
        ).fetchone() == ("POINT", 4326)
