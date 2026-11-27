import numpy as np
import pytest
import rasterio
from rasterio.transform import Affine

from lineament_core.science.hillshade import Cancelled, Illumination, run


@pytest.mark.parametrize(
    "transform",
    [
        Affine(2, 0, 500000, 0, -2, 5500000),
        Affine(4, 0, 500000, 0, -3, 5500000),
        Affine(2, 0.3, 500000, 0.7, -3, 5500000),
    ],
)
@pytest.mark.parametrize(
    "fixture", ["flat", "plane", "sin", "impulse", "step", "masked"]
)
def test_analytic_oracle_and_tile_equivalence(tmp_path, transform, fixture):
    row, col = np.indices((15, 19))
    x, y = transform.a * col + transform.b * row, transform.d * col + transform.e * row
    data = {
        "flat": np.full(row.shape, 42, dtype="int16"),
        "plane": 0.3 * x - 0.4 * y,
        "sin": np.sin(0.12 * x),
        "impulse": np.where((row == 6) & (col == 7), 9.0, 0.0),
        "step": np.where(col >= 7, 9.0, 0.0),
        "masked": (0.3 * x - 0.4 * y).copy(),
    }[fixture]
    if fixture == "masked":
        data[3, 4], data[6, 8], data[9, 11] = np.nan, np.inf, -9999
    src = tmp_path / "source.tif"
    with rasterio.open(
        src,
        "w",
        driver="GTiff",
        width=19,
        height=15,
        count=1,
        crs="EPSG:32633",
        transform=transform,
        dtype=data.dtype,
        nodata=-9999,
    ) as ds:
        ds.write(data, 1)
    light = Illumination(90, 1, 1)
    for tile in (4, 32):
        run(src, tmp_path / f"{tile}.tif", light, tile=tile)
    with (
        rasterio.open(tmp_path / "4.tif") as small,
        rasterio.open(tmp_path / "32.tif") as whole,
    ):
        got = small.read(1)
        assert np.array_equal(got, whole.read(1))
        assert small.transform == transform and small.crs.to_epsg() == 32633
        assert small.nodata == -1 and small.dtypes == ("float32",)
    expected = np.full(data.shape, -1.0)
    inverse = np.linalg.inv([[transform.a, transform.b], [transform.d, transform.e]])
    for r in range(1, 14):
        for c in range(1, 18):
            a = data[r - 1 : r + 2, c - 1 : c + 2].astype(float)
            if not np.isfinite(a).all() or (a == -9999).any():
                continue
            if fixture == "flat":
                gradient = (0.0, 0.0)
            elif fixture in ("plane", "masked"):
                gradient = (0.3, -0.4)
            else:
                # Independent scalar regression on the stencil with separable weights.
                p = (
                    sum(
                        float(a[i, 2] - a[i, 0]) * (2 if i == 1 else 1)
                        for i in range(3)
                    )
                    / 8
                )
                q = (
                    sum(
                        float(a[2, i] - a[0, i]) * (2 if i == 1 else 1)
                        for i in range(3)
                    )
                    / 8
                )
                gradient = np.array([p, q]) @ inverse
            normal = np.array([-gradient[0], -gradient[1], 1.0])
            light_vector = np.array([2**-0.5, 0.0, 2**-0.5])
            expected[r, c] = max(0.0, normal @ light_vector / np.linalg.norm(normal))
    error = np.abs(got - expected)
    print(f"{fixture}: mean={error.mean():.3g}, max={error.max():.3g}")
    assert np.array_equal(got == -1.0, expected == -1.0)
    assert error.max() < 2e-7


def test_cancellation_and_small_raster(tmp_path):
    src = tmp_path / "tiny.tif"
    with rasterio.open(
        src,
        "w",
        driver="GTiff",
        width=1,
        height=1,
        count=1,
        transform=Affine(2, 0, 20, 0, -2, 30),
        crs="EPSG:32633",
        dtype="int16",
    ) as ds:
        ds.write(np.ones((1, 1), dtype="int16"), 1)
    out = tmp_path / "output.tif"
    updates = []
    light = Illumination(90, 1, 1)
    with pytest.raises(Cancelled):
        run(src, out, light, cancelled=lambda: True, progress=updates.append)
    assert not out.exists() and updates == []
    run(src, out, light, progress=updates.append)
    with rasterio.open(out) as got:
        assert got.read(1).item() == -1
    assert updates == [1.0]


@pytest.mark.parametrize("offset", [0.0, 113.0])
def test_physical_scaled_integer_matches_float(tmp_path, offset):
    transform = Affine(2, 0.5, 500000, 0.25, -3, 5500000)
    raw = np.arange(99, dtype="int16").reshape(9, 11)
    raw[4, 4] = -9999
    physical = raw.astype("float64") * 0.5 + offset
    physical[4, 4] = -9999
    light = Illumination(135, 1, 1)
    results = []
    for name, values, scale, bias in (
        ("float", physical, 1.0, 0.0),
        ("scaled", raw, 0.5, offset),
    ):
        source = tmp_path / f"{name}.tif"
        with rasterio.open(
            source,
            "w",
            driver="GTiff",
            width=11,
            height=9,
            count=1,
            transform=transform,
            crs="EPSG:32633",
            dtype=values.dtype,
            nodata=-9999,
        ) as ds:
            ds.write(values, 1)
            ds.scales, ds.offsets = (scale,), (bias,)
        for tile in (3, 12):
            output = tmp_path / f"{name}-{tile}.tif"
            run(source, output, light, tile=tile)
            with rasterio.open(output) as ds:
                results.append(ds.read(1))
    for result in results[1:]:
        np.testing.assert_array_equal(result == -1.0, results[0] == -1.0)
        np.testing.assert_allclose(result, results[0], atol=2e-7, rtol=0)
    assert np.all(results[0][3:6, 3:6] == -1.0)


@pytest.mark.parametrize(
    "scale,offset,error",
    [
        (0.0, 0.0, "positive band scale"),
        (-1.0, 0.0, "positive band scale"),
        (1e308, 0.0, "float64 range"),
        (1e308, 1e308, "float64 range"),
        (float("inf"), 0.0, "positive band scale"),
        (1.0, float("nan"), "finite offset"),
    ],
)
def test_unsupported_calibration_fails_explicitly(tmp_path, scale, offset, error):
    from lineament_core.infrastructure.gis.raster import inspect_dem

    source, output = tmp_path / "source.tif", tmp_path / "result.tif"
    with rasterio.open(
        source,
        "w",
        driver="GTiff",
        width=5,
        height=5,
        count=1,
        transform=Affine(2, 0, 20, 0, -2, 30),
        crs="EPSG:32633",
        dtype="int16",
    ) as ds:
        ds.write(np.full((5, 5), 3, dtype="int16"), 1)
        ds.scales, ds.offsets = (scale,), (offset,)
    with pytest.raises(ValueError, match=error):
        inspect_dem(source)
    with pytest.raises(ValueError, match=error):
        run(source, output, Illumination(315, 1, 1), tile=3)
    assert not output.exists()


def test_internal_mask_and_raw_nodata_precede_calibration(tmp_path):
    from lineament_core.infrastructure.gis.raster import inspect_dem

    src = tmp_path / "masked.tif"
    raw = np.full((9, 9), 7, dtype="int16")
    raw[2, 2] = -9999
    mask = np.full((9, 9), 255, dtype="uint8")
    mask[6, 6] = 0
    with (
        rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True),
        rasterio.open(
            src,
            "w",
            driver="GTiff",
            width=9,
            height=9,
            count=1,
            dtype="int16",
            crs="EPSG:32633",
            transform=Affine(2, 0, 500, 0, -2, 700),
            nodata=-9999,
        ) as ds,
    ):
        ds.write(raw, 1)
        ds.write_mask(mask)
        ds.scales, ds.offsets = (0.5,), (10.0,)
    assert inspect_dem(src)["valid_pixels"] == 79
    outcome = tmp_path / "result.tif"
    run(src, outcome, Illumination(135, 1, 1), tile=3)
    with rasterio.open(outcome) as ds:
        values = ds.read(1)
    assert np.all(values[1:4, 1:4] == -1.0)
    assert np.all(values[5:8, 5:8] == -1.0)
    assert values[4, 4] == pytest.approx(2**-0.5, abs=2e-7)
