"""Canonical provenance for outputs produced by the project Hillshade runner."""

import math
import re
from datetime import datetime

from lineament_core.science.hillshade import VERSION, Illumination

from .manifest import ProjectError, encode, identity

FIELDS = frozenset(
    """
schema_version source_asset_id source_version_id source_checksum band algorithm
algorithm_version parameters source dependencies created_at output output_checksum
""".split()
)
GRID = ("crs", "transform", "bounds", "resolution", "width", "height")
RASTER = (
    *GRID,
    "format",
    "band",
    "bands",
    "dtype",
    "nodata",
    "band_scale",
    "band_offset",
    "horizontal_unit",
    "horizontal_metres_per_unit",
    "vertical_unit",
)
PARAMETERS = frozenset(("azimuth", "altitude", "z_factor", "vertical_metres_per_unit"))
HISTORICAL_HILLSHADE_VERSIONS = frozenset(("2.0.0", "2.0.1"))


def executable_supported(algorithm, version):
    return algorithm == "hillshade" and version == VERSION


DEPENDENCIES = frozenset(("rasterio", "gdal", "proj", "numpy"))


def raster_metadata(info):
    return {key: info[key] for key in RASTER}


def valid_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def validate_provenance(record, *, source_id, output_checksum, bound_asset=None):
    try:
        if (
            type(record) is not dict
            or record.keys() != FIELDS
            or record["schema_version"] != "1"
        ):
            raise ValueError("Unknown schema or missing provenance fields")
        if identity(record["source_asset_id"]) != identity(source_id):
            raise ValueError("Source asset mismatch")
        identity(record["source_version_id"])
        for key in ("source_checksum", "output_checksum"):
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", record[key]):
                raise ValueError("Malformed checksum")
        if record["output_checksum"] != output_checksum:
            raise ValueError("Output checksum mismatch")
        if bound_asset and (
            record["source_version_id"] != bound_asset["source_version_id"]
            or record["source_checksum"] != bound_asset["checksum"]
        ):
            raise ValueError("Source snapshot differs from declared source version")
        if (
            record["algorithm"] != "hillshade"
            or record["algorithm_version"] not in HISTORICAL_HILLSHADE_VERSIONS
        ):
            raise ValueError("Unsupported algorithm or version")
        params = record["parameters"]
        if (
            type(params) is not dict
            or params.keys() != PARAMETERS
            or any(type(v) is not float for v in params.values())
        ):
            raise ValueError("Incomplete or noncanonical processing parameters")
        light = Illumination(**params)
        deps = record["dependencies"]
        if (
            type(deps) is not dict
            or deps.keys() != DEPENDENCIES
            or any(
                not re.fullmatch(r"\d+\.\d+(?:\.[0-9A-Za-z.+-]+)?", v)
                for v in deps.values()
            )
        ):
            raise ValueError("Missing or malformed dependency versions")
        stamp = record["created_at"]
        if type(stamp) is not str or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|\+00:00)",
            stamp,
        ):
            raise ValueError("Processing timestamp must be explicit UTC ISO-8601")
        if datetime.fromisoformat(stamp).utcoffset().total_seconds() != 0:
            raise ValueError("Processing timestamp must be UTC")
        source, output = record["source"], record["output"]
        for raster in (source, output):
            if (
                type(raster) is not dict
                or raster.keys() != set(RASTER)
                or raster["format"] != "GTiff"
                or type(raster["crs"]) is not str
                or not raster["crs"]
                or type(raster["dtype"]) is not str
                or not raster["dtype"]
                or type(raster["horizontal_unit"]) is not str
                or not raster["horizontal_unit"]
            ):
                raise ValueError("Incomplete raster metadata")
            for key in ("width", "height", "band", "bands"):
                if type(raster[key]) is not int or raster[key] < 1:
                    raise ValueError("Invalid raster dimensions or band")
            for key, size in (("transform", 6), ("bounds", 4), ("resolution", 2)):
                if (
                    type(raster[key]) is not list
                    or len(raster[key]) != size
                    or not all(map(valid_number, raster[key]))
                ):
                    raise ValueError("Invalid raster spatial metadata")
            for key in ("band_scale", "horizontal_metres_per_unit"):
                if not valid_number(raster[key]) or raster[key] <= 0:
                    raise ValueError("Invalid raster scaling metadata")
            if not valid_number(raster["band_offset"]):
                raise ValueError("Invalid band offset")
        if (
            type(record["band"]) is not int
            or record["band"] != source["band"]
            or source["band"] > source["bands"]
        ):
            raise ValueError("Selected band mismatch")
        if not isinstance(source["vertical_unit"], str) or not source["vertical_unit"]:
            raise ValueError("Missing vertical units")
        unit = source["vertical_unit"].strip().lower()
        factors = {
            "m": 1.0,
            "metre": 1.0,
            "meter": 1.0,
            "ft": 0.3048,
            "foot": 0.3048,
            "us survey foot": 1200 / 3937,
        }
        if unit != "explicit metres-per-unit" and (
            unit not in factors
            or not math.isclose(light.vertical_metres_per_unit, factors[unit])
        ):
            raise ValueError("Vertical units conflict with processing scale")
        if any(
            source[k] != output[k]
            for k in GRID + ("horizontal_unit", "horizontal_metres_per_unit")
        ) or (
            output["band"],
            output["bands"],
            output["dtype"],
            output["nodata"],
            output["band_scale"],
            output["band_offset"],
            output["vertical_unit"],
        ) != (1, 1, "float32", -1.0, 1.0, 0.0, None):
            raise ValueError("Incompatible Hillshade output metadata")
        return encode(record)
    except (ValueError, TypeError, KeyError, OverflowError) as exc:
        raise ProjectError(f"Invalid result provenance: {exc}") from exc
