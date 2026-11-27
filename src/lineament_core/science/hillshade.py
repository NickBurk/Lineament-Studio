"""PRE-001: single-direction Lambertian hillshade on projected DEMs."""

import math
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from lineament_core.infrastructure.gis.raster import (
    band_calibration,
    open_tiff,
    physical_samples,
    read_dem_samples,
    windows,
)

VERSION = "2.0.0"


class Cancelled(Exception):
    """Processing stopped at a tile boundary."""


@dataclass(frozen=True)
class Illumination:
    azimuth: float
    vertical_metres_per_unit: float
    z_factor: float
    altitude: float = 45.0

    def __post_init__(self):
        for name in ("azimuth", "altitude", "z_factor", "vertical_metres_per_unit"):
            value = getattr(self, name)
            if type(value) not in (int, float):
                raise ValueError("Illumination parameters must be real numbers")
            object.__setattr__(self, name, float(value))
        if not all(
            map(
                math.isfinite,
                (
                    self.azimuth,
                    self.altitude,
                    self.z_factor,
                    self.vertical_metres_per_unit,
                ),
            )
        ):
            raise ValueError("Illumination parameters must be finite")
        if not (
            0 <= self.azimuth < 360
            and 0 < self.altitude <= 90
            and self.z_factor > 0
            and self.vertical_metres_per_unit > 0
        ):
            raise ValueError("Invalid illumination angle or elevation scaling")


def shade(data, transform, horizontal_metres_per_unit, light):
    """Evaluate the Horn stencil for interior pixels, masking invalid neighbors."""
    import numpy as np
    from numpy.lib.stride_tricks import sliding_window_view

    elevations = np.asarray(data.filled(np.nan), dtype=np.float64)
    cells = sliding_window_view(elevations, (3, 3))
    valid = np.isfinite(cells).all(axis=(-2, -1))
    scale = light.z_factor * light.vertical_metres_per_unit / horizontal_metres_per_unit
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        p = ((cells[..., :, 2] - cells[..., :, 0]) @ np.array([1.0, 2.0, 1.0])) * (
            scale / 8
        )
        q = ((cells[..., 2, :] - cells[..., 0, :]) @ np.array([1.0, 2.0, 1.0])) * (
            scale / 8
        )
        det = transform.determinant
        dx = (transform.e * p - transform.d * q) / det
        dy = (-transform.b * p + transform.a * q) / det
        az, alt = map(math.radians, (light.azimuth, light.altitude))
        norm = np.hypot(np.hypot(dx, dy), 1)
        cosine = (
            math.sin(alt) / norm
            - dx / norm * math.cos(alt) * math.sin(az)
            - dy / norm * math.cos(alt) * math.cos(az)
        )
    if any(not np.isfinite(value[valid]).all() for value in (dx, dy, norm, cosine)):
        raise ValueError("Terrain gradient exceeds numerical range")
    return np.where(valid, np.clip(cosine, 0.0, 1.0), -1.0).astype("float32")


def run(
    source,
    output,
    light,
    *,
    band=1,
    tile=512,
    memory_bytes=128 * 1024**2,
    cancelled=lambda: False,
    progress=lambda fraction: None,
):
    """Write a new float32 GeoTIFF and report progress in [0, 1]."""
    import numpy as np
    import rasterio
    from rasterio.windows import Window

    output = Path(output)
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    if type(tile) is not int or tile < 1:
        raise ValueError("Tile size must be a positive integer")
    with tempfile.TemporaryDirectory(dir=output.parent) as temp:
        staged = Path(temp) / "hillshade.tif"
        with open_tiff(source) as src:
            if type(band) is not int or not 1 <= band <= src.count:
                raise ValueError("Selected band does not exist")
            if np.dtype(src.dtypes[band - 1]).kind not in "uif":
                raise ValueError("DEM requires a real numeric band")
            if not src.crs or not src.crs.is_projected:
                raise ValueError("Hillshade requires a known projected CRS")
            band_scale, band_offset = band_calibration(src, band)
            _, factor = src.crs.linear_units_factor
            if (
                not math.isfinite(factor)
                or factor <= 0
                or not all(map(math.isfinite, src.transform[:6]))
                or not math.isfinite(src.transform.determinant)
                or src.transform.determinant == 0
            ):
                raise ValueError("Invalid horizontal scale or transform")
            if (
                256 * (tile + 2) ** 2 + 16 * math.prod(src.block_shapes[band - 1])
            ) > memory_bytes:
                raise MemoryError("Hillshade working-set estimate exceeds budget")
            kwargs = dict(
                driver="GTiff",
                width=src.width,
                height=src.height,
                count=1,
                dtype="float32",
                nodata=-1.0,
                crs=src.crs,
                transform=src.transform,
                tiled=True,
                blockxsize=256,
                blockysize=256,
                compress="deflate",
                BIGTIFF="IF_SAFER",
            )
            count = math.ceil(src.height / tile) * math.ceil(src.width / tile)
            with rasterio.open(staged, "w", **kwargs) as dst:
                dst.update_tags(
                    algorithm="hillshade",
                    algorithm_version=VERSION,
                    azimuth=light.azimuth,
                    azimuth_convention="clockwise from grid north",
                    altitude=light.altitude,
                    z_factor=light.z_factor,
                    vertical_metres_per_unit=light.vertical_metres_per_unit,
                    band=band,
                    source_band_scale=band_scale,
                    source_band_offset=band_offset,
                )
                for index, window in enumerate(windows(src.width, src.height, tile), 1):
                    if cancelled():
                        raise Cancelled()
                    halo = Window(
                        window.col_off - 1,
                        window.row_off - 1,
                        window.width + 2,
                        window.height + 2,
                    )
                    # Clip the read, then pad outside the actual raster with NaN.
                    clipped = halo.intersection(Window(0, 0, src.width, src.height))
                    arr = np.ma.masked_all(
                        (int(halo.height), int(halo.width)), dtype="float64"
                    )
                    x, y = (
                        int(clipped.col_off - halo.col_off),
                        int(clipped.row_off - halo.row_off),
                    )
                    arr[y : y + int(clipped.height), x : x + int(clipped.width)] = (
                        physical_samples(
                            read_dem_samples(src, band, clipped),
                            band_scale,
                            band_offset,
                        )
                    )
                    dst.write(
                        shade(arr, src.transform, factor, light), 1, window=window
                    )
                    if index < count:
                        progress(index / count)
            if cancelled():
                raise Cancelled()
        # Publish only after the source handle closes and the sidecar check succeeds.
        os.link(staged, output)
    progress(1.0)
