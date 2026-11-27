"""Local GeoTIFF inspection with bounded reads and explicit spatial metadata."""

import math
import shutil
from pathlib import Path


def windows(width, height, tile):
    from rasterio.windows import Window

    if type(tile) is not int or tile < 1:
        raise ValueError("Tile size must be a positive integer")
    for y in range(0, height, tile):
        for x in range(0, width, tile):
            yield Window(x, y, min(tile, width - x), min(tile, height - y))


def open_tiff(path):
    import rasterio

    return rasterio.open(Path(path), driver="GTiff", GEOREF_SOURCES="INTERNAL")


def inspect_dem(path, *, band=1, tile=512, memory_bytes=64 * 1024**2, vertical_unit=None):
    import numpy as np

    path = Path(path)
    with open_tiff(path) as src:
        if type(band) is not int or not 1 <= band <= src.count:
            raise ValueError("Selected band does not exist")
        dtype = np.dtype(src.dtypes[band - 1])
        if dtype.kind not in "uif":
            raise ValueError("DEM requires a real numeric band")
        native_block = math.prod(src.block_shapes[band - 1])
        estimate = (tile * tile + native_block) * (dtype.itemsize + 8)
        if estimate > memory_bytes:
            raise MemoryError("DEM preflight working-set estimate exceeds budget")
        transform = src.transform
        if not all(map(math.isfinite, transform[:6])) or transform.determinant == 0:
            raise ValueError("DEM has a non-finite or singular affine transform")
        valid = nan = inf = 0
        lo, hi = math.inf, -math.inf
        for window in windows(src.width, src.height, tile):
            data = src.read(band, window=window, masked=True)
            finite = np.isfinite(data.data)
            nan += int(np.count_nonzero(np.isnan(data.data)))
            inf += int(np.count_nonzero(np.isinf(data.data)))
            values = data.data[finite & ~np.ma.getmaskarray(data)]
            valid += values.size
            if values.size:
                lo, hi = min(lo, float(values.min())), max(hi, float(values.max()))
        crs = src.crs
        crs_state = "absent" if crs is None else (
            "known" if crs.is_projected or crs.is_geographic else "unknown"
        )
        unit, factor = crs.linear_units_factor if crs and crs.is_projected else (
            ("degree", None) if crs and crs.is_geographic else (None, None)
        )
        nodata = src.nodatavals[band - 1]
        if nodata is not None and not math.isfinite(nodata):
            nodata = str(nodata)
        return dict(
            format=src.driver, width=src.width, height=src.height, bands=src.count,
            band=band, dtype=dtype.name, crs=crs.to_wkt() if crs else None,
            crs_state=crs_state, projected=bool(crs and crs.is_projected),
            horizontal_unit=unit, horizontal_metres_per_unit=factor,
            vertical_unit=vertical_unit or src.units[band - 1],
            transform=list(transform[:6]), bounds=list(src.bounds),
            resolution=list(src.res), rotated=bool(transform.b or transform.d),
            nodata=nodata, mask=[flag.name for flag in src.mask_flag_enums[band - 1]],
            nan_count=nan, inf_count=inf, valid_pixels=valid,
            valid_percent=100 * valid / (src.width * src.height),
            empty=valid == 0, constant=bool(valid and lo == hi),
            minimum=lo if valid else None, maximum=hi if valid else None,
            full_array_bytes=src.width * src.height * dtype.itemsize,
            window_working_bytes=estimate, available_disk_bytes=shutil.disk_usage(path.parent).free,
            sidecars=[str(Path(name).name) for name in src.files if Path(name).resolve() != path.resolve()],
        )
