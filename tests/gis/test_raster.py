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
