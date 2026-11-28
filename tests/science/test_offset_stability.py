"""Independent plane oracle for calibrated integer elevations."""

import math

import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

from lineament_core.science.hillshade import Illumination, run


@pytest.mark.parametrize("offset", [0.0, 1e20, -1e20])
@pytest.mark.parametrize("scale", [0.5, 2.0])
def test_large_offset_preserves_plane_gradient(tmp_path, offset, scale):
    y, x = np.mgrid[:9, :11]
    source = tmp_path / "plane.tif"
    with rasterio.open(
        source,
        "w",
        driver="GTiff",
        width=11,
        height=9,
        count=1,
        dtype="int16",
        crs="EPSG:32633",
        transform=Affine(2, 0, 500000, 0, -3, 5500000),
    ) as ds:
        ds.write((2 * x + 3 * y).astype("int16"), 1)
        ds.scales, ds.offsets = (scale,), (offset,)
    dx, dy = scale, -scale
    norm = math.sqrt(1 + dx * dx + dy * dy)
    expected = max(
        0,
        (
            math.sin(math.pi / 4)
            - dx * math.cos(math.pi / 4) * math.sin(math.pi / 4)
            - dy * math.cos(math.pi / 4) * math.cos(math.pi / 4)
        )
        / norm,
    )
    outputs = []
    for tile in (3, 20):
        output = tmp_path / f"out-{tile}.tif"
        run(source, output, Illumination(45, 1, 1), tile=tile)
        with rasterio.open(output) as ds:
            values = ds.read(1)
        error = np.abs(values[1:-1, 1:-1] - expected)
        assert error.max() <= 6e-8
        assert error.mean() <= 6e-8
        assert (error / max(abs(expected), 1e-12)).max() <= 2e-7
        outputs.append(values)
    np.testing.assert_array_equal(*outputs)
