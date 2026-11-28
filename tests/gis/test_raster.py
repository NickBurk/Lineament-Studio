import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

from lineament_core.infrastructure.gis.raster import inspect_dem


@pytest.mark.parametrize("crs,state", [(None, "absent"), ("EPSG:32633", "known")])
def test_preflight(tmp_path, crs, state):
    directory = tmp_path / ("地形" + "x" * 90) / ("Élévation" + "x" * 90)
    directory.mkdir(parents=True)
    path = directory / "Высота.tif"
    data = np.array([[1, np.nan, np.inf], [-9999, 1, 1]], dtype="float32")
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=3,
        height=2,
        count=1,
        transform=Affine(2, 0.5, 500, 0.25, -3, 700),
        crs=crs,
        dtype="float32",
        nodata=-9999,
    ) as ds:
        ds.write(data, 1)
        ds.set_band_unit(1, "m")
    info = inspect_dem(path, tile=2)
    assert info["crs_state"] == state and info["rotated"]
    assert info["valid_percent"] == 50 and info["constant"]
    assert info["nan_count"] == info["inf_count"] == 1
    assert info["vertical_unit"] == "m"
    with pytest.raises(MemoryError):
        inspect_dem(path, memory_bytes=1)
    with pytest.raises(ValueError, match="band"):
        inspect_dem(path, band=2)


def test_damaged_geotiff(tmp_path):
    path = tmp_path / "damaged.tif"
    path.write_bytes(b"not a raster")
    with pytest.raises(rasterio.errors.RasterioIOError):
        inspect_dem(path)


@pytest.mark.parametrize("sidecar", ["mask", "pam", "overview", "world"])
def test_external_dependencies_rejected_for_reference_and_copy(tmp_path, sidecar):
    from lineament_core.infrastructure.data.manifest import checksum
    from lineament_core.infrastructure.data.project import Project
    from lineament_core.infrastructure.gis.raster import SidecarError

    source = tmp_path / "source.tif"
    with (
        rasterio.Env(GDAL_TIFF_INTERNAL_MASK=False),
        rasterio.open(
            source,
            "w",
            driver="GTiff",
            width=5,
            height=5,
            count=1,
            crs="EPSG:32633",
            transform=Affine(2, 0, 500, 0, -2, 700),
            dtype="uint8",
        ) as ds,
    ):
        ds.write(np.ones((5, 5), dtype="uint8"), 1)
        if sidecar == "mask":
            ds.write_mask(np.eye(5, dtype="uint8") * 255)
    if sidecar == "mask":
        sibling = source.with_suffix(".tif.msk")
        assert sibling.is_file()
    elif sidecar == "pam":
        sibling = source.with_suffix(".tif.aux.xml")
        sibling.write_text(
            '<PAMDataset><PAMRasterBand band="1"><Scale>2</Scale></PAMRasterBand></PAMDataset>'
        )
    elif sidecar == "overview":
        sibling = source.with_suffix(".tif.ovr")
        sibling.write_bytes(b"external overview")
    else:
        sibling = source.with_suffix(".tfw")
        sibling.write_text("1\n0\n0\n-1\n500\n700\n")
    original, sibling_bytes = checksum(source), sibling.read_bytes()
    project = Project.create(tmp_path / "project")
    with pytest.raises(SidecarError):
        inspect_dem(source)
    for mode in ("reference", "copy"):
        with pytest.raises(SidecarError):
            project.add_dem(source, mode)
    assert project.snapshot()["assets"] == []
    assert checksum(source) == original and sibling.read_bytes() == sibling_bytes


def test_sidecar_introduced_after_import_and_relink(tmp_path):
    import shutil

    from lineament_core.infrastructure.data.project import Project
    from lineament_core.infrastructure.gis.raster import SidecarError

    source = tmp_path / "source.tif"
    with rasterio.open(
        source,
        "w",
        driver="GTiff",
        width=3,
        height=3,
        count=1,
        transform=Affine(2, 0, 20, 0, -2, 30),
        dtype="uint8",
    ) as ds:
        ds.write(np.ones((3, 3), dtype="uint8"), 1)
    project = Project.create(tmp_path / "project")
    key = project.add_dem(source, "reference")
    candidate = tmp_path / "moved.tif"
    shutil.copyfile(source, candidate)
    candidate.with_suffix(".tfw").write_text("1\n0\n0\n-1\n500\n700\n")
    with pytest.raises(SidecarError):
        project.relink(key, candidate)
    assert project.source(key) == (source, "available")
    source.with_suffix(".tif.aux.xml").write_text("<PAMDataset/>")
    assert project.source(key) == (source, "unsupported_sidecars")


@pytest.mark.parametrize(
    "definition,state,unit",
    [
        ("EPSG:4326", "known", "degree"),
        (
            'LOCAL_CS["Engineering",LOCAL_DATUM["Site",0],UNIT["metre",1],AXIS["X",EAST],AXIS["Y",NORTH]]',
            "unknown",
            None,
        ),
    ],
)
def test_crs_classification(tmp_path, definition, state, unit):
    path = tmp_path / "classification.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=4,
        height=4,
        count=1,
        dtype="uint8",
        crs=definition,
        transform=Affine(0.01, 0, 10, 0, -0.01, 50),
    ) as ds:
        ds.write(np.ones((4, 4), dtype="uint8"), 1)
    info = inspect_dem(path)
    assert info["crs_state"] == state
    assert info["horizontal_unit"] == unit


def test_preflight_cancellation_between_windows(tmp_path, monkeypatch):
    from lineament_core.infrastructure.execution import Cancelled
    from lineament_core.infrastructure.gis import raster

    path = tmp_path / "two-windows.tif"
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        width=4,
        height=2,
        count=1,
        dtype="uint8",
        transform=Affine(2, 0, 500, 0, -2, 700),
    ) as dataset:
        dataset.write(np.arange(8, dtype="uint8").reshape(2, 4), 1)

    reads = []
    read_samples = raster.read_dem_samples

    def record_read(src, band, window):
        samples = read_samples(src, band, window)
        reads.append(window)
        return samples

    monkeypatch.setattr(raster, "read_dem_samples", record_read)
    with pytest.raises(Cancelled):
        inspect_dem(path, tile=2, cancelled=lambda: bool(reads))
    assert reads == [rasterio.windows.Window(0, 0, 2, 2)]
