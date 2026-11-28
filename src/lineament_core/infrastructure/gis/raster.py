"""Local GeoTIFF inspection with bounded reads and explicit spatial metadata."""

import math
import shutil

from ..execution import check_cancelled
from contextlib import contextmanager
from pathlib import Path


def windows(width, height, tile):
    from rasterio.windows import Window

    if type(tile) is not int or tile < 1:
        raise ValueError("Tile size must be a positive integer")
    for y in range(0, height, tile):
        for x in range(0, width, tile):
            yield Window(x, y, min(tile, width - x), min(tile, height - y))


class SidecarError(ValueError):
    """The development profile requires a self-contained GeoTIFF."""


def require_self_contained(path):
    path = Path(path)
    names = {path.name.casefold(), path.stem.casefold()}
    suffixes = (
        ".msk",
        ".aux",
        ".aux.xml",
        ".ovr",
        ".tfw",
        ".tifw",
        ".tiffw",
        ".wld",
        ".tab",
        ".rrd",
        ".xml",
        ".prj",
        ".ige",
        ".rpb",
        "_rpc.txt",
    )
    excluded = {name + suffix for name in names for suffix in suffixes}
    for sibling in path.parent.iterdir():
        if sibling.name.casefold() in excluded:
            raise SidecarError(
                f"External GeoTIFF sidecar is unsupported: {sibling.name}"
            )


@contextmanager
def open_tiff(path):
    import rasterio

    path = Path(path)
    require_self_contained(path)
    # Force one physical file even if another sidecar appears after discovery.
    with (
        rasterio.Env(
            GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR",
            GDAL_PAM_ENABLED="NO",
            PROJ_NETWORK="OFF",
        ),
        rasterio.open(path, driver="GTiff", GEOREF_SOURCES="INTERNAL") as src,
    ):
        if any(Path(item).resolve() != path.resolve() for item in src.files):
            raise SidecarError("GDAL discovered an external GeoTIFF dependency")
        yield src
    require_self_contained(path)


def band_calibration(src, band):
    scale, offset = src.scales[band - 1], src.offsets[band - 1]
    if not math.isfinite(scale) or scale <= 0 or not math.isfinite(offset):
        raise ValueError("DEM requires finite positive band scale and finite offset")
    return scale, offset


def read_dem_samples(src, band, window):
    """Combine GDAL's active mask with the explicit raw NoData sentinel."""
    import numpy as np

    raw = src.read(band, window=window, masked=True)
    nodata = src.nodatavals[band - 1]
    if nodata is not None and math.isfinite(nodata):
        raw.mask = np.ma.getmaskarray(raw) | (raw.data == nodata)
    return raw


def physical_samples(raw, scale, offset):
    """Convert only finite unmasked samples, preserving raw NoData semantics."""
    import numpy as np

    valid = np.isfinite(raw.data) & ~np.ma.getmaskarray(raw)
    data = np.full(raw.shape, np.nan)
    with np.errstate(over="raise", invalid="raise"):
        try:
            data[valid] = raw.data[valid].astype("float64") * scale + offset
        except FloatingPointError as exc:
            raise ValueError("Physical DEM elevation exceeds float64 range") from exc
    return np.ma.array(data, mask=~valid)


def inspect_dem(
    path,
    *,
    band=1,
    tile=512,
    memory_bytes=64 * 1024**2,
    vertical_unit=None,
    cancelled=lambda: False,
):
    import numpy as np

    check_cancelled(cancelled)
    path = Path(path)
    with open_tiff(path) as src:
        if type(band) is not int or not 1 <= band <= src.count:
            raise ValueError("Selected band does not exist")
        dtype = np.dtype(src.dtypes[band - 1])
        if dtype.kind not in "uif":
            raise ValueError("DEM requires a real numeric band")
        scale, offset = band_calibration(src, band)
        native_block = math.prod(src.block_shapes[band - 1])
        estimate = (tile * tile + native_block) * (dtype.itemsize + 40)
        if estimate > memory_bytes:
            raise MemoryError("DEM preflight working-set estimate exceeds budget")
        transform = src.transform
        if not all(map(math.isfinite, transform[:6])) or transform.determinant == 0:
            raise ValueError("DEM has a non-finite or singular affine transform")
        valid = nan = inf = 0
        lo = raw_lo = math.inf
        hi = raw_hi = -math.inf
        for window in windows(src.width, src.height, tile):
            check_cancelled(cancelled)
            data = read_dem_samples(src, band, window)
            finite = np.isfinite(data.data)
            nan += int(np.count_nonzero(np.isnan(data.data)))
            inf += int(np.count_nonzero(np.isinf(data.data)))
            values = data.data[finite & ~np.ma.getmaskarray(data)]
            valid += values.size
            if values.size:
                raw_lo, raw_hi = (
                    min(raw_lo, float(values.min())),
                    max(raw_hi, float(values.max())),
                )
                physical = physical_samples(data, scale, offset).compressed()
                lo, hi = min(lo, float(physical.min())), max(hi, float(physical.max()))
        check_cancelled(cancelled)
        crs = src.crs
        crs_state = (
            "absent"
            if crs is None
            else ("known" if crs.is_projected or crs.is_geographic else "unknown")
        )
        unit, factor = (
            crs.linear_units_factor
            if crs and crs.is_projected
            else (("degree", None) if crs and crs.is_geographic else (None, None))
        )
        nodata = src.nodatavals[band - 1]
        if nodata is not None and not math.isfinite(nodata):
            nodata = str(nodata)
        corners = [
            transform @ corner
            for corner in (
                (0, 0),
                (0, src.height),
                (src.width, 0),
                (src.width, src.height),
            )
        ]
        xs, ys = zip(*corners)
        return dict(
            format=src.driver,
            width=src.width,
            height=src.height,
            bands=src.count,
            band=band,
            dtype=dtype.name,
            crs=crs.to_wkt() if crs else None,
            crs_state=crs_state,
            projected=bool(crs and crs.is_projected),
            horizontal_unit=unit,
            horizontal_metres_per_unit=factor,
            vertical_unit=vertical_unit or src.units[band - 1],
            transform=list(transform[:6]),
            bounds=[min(xs), min(ys), max(xs), max(ys)],
            resolution=list(src.res),
            rotated=bool(transform.b or transform.d),
            nodata=nodata,
            band_scale=scale,
            band_offset=offset,
            raw_minimum=raw_lo if valid else None,
            raw_maximum=raw_hi if valid else None,
            mask=[flag.name for flag in src.mask_flag_enums[band - 1]],
            nan_count=nan,
            inf_count=inf,
            valid_pixels=valid,
            valid_percent=100 * valid / (src.width * src.height),
            empty=valid == 0,
            constant=bool(valid and lo == hi),
            minimum=lo if valid else None,
            maximum=hi if valid else None,
            full_array_bytes=src.width * src.height * dtype.itemsize,
            window_working_bytes=estimate,
            available_disk_bytes=shutil.disk_usage(path.parent).free,
            sidecars=[
                str(Path(name).name)
                for name in src.files
                if Path(name).resolve() != path.resolve()
            ],
        )
