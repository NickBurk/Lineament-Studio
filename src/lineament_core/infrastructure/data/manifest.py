"""Version 1 project manifest and local path policy."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path, PureWindowsPath
from uuid import UUID


class ProjectError(ValueError):
    """Corrupt, unsupported or unsafe project state."""


LIMIT = 8 * 1024 * 1024
FORMAT = "org.lineament-studio.project"
VERSION = "1.1"
SCHEMA = "2"
DIRECTORIES = (
    "inputs/dem",
    "inputs/geology",
    "inputs/osm",
    "processing",
    "experiments",
    "results",
    "annotations",
    "datasets",
    "reports",
    "cache",
    "logs",
)
FIELDS = set(
    "format_id format_version schema_version project_id application_version created_at modified_at project_crs storage_policy catalog_uri assets default_profiles".split()
)
ASSET_FIELDS = set(
    "asset_id source_version_id role storage_mode uri checksum metadata".split()
)


def identity(value):
    if type(value) is not str or str(UUID(value)) != value or not UUID(value).int:
        raise ProjectError("Expected a canonical nonzero UUID")
    return value


def internal(root: Path, uri: str) -> Path:
    if type(uri) is not str:
        raise ProjectError("Expected a relative internal path")
    parts = uri.split("/")
    windows = PureWindowsPath(uri)
    if (
        windows.drive
        or windows.root
        or any(
            not part
            or part in (".", "..")
            or part.endswith((" ", "."))
            or re.search(r'[<>:"\\|?*\x00-\x1f]', part)
            or PureWindowsPath(part).is_reserved()
            for part in parts
        )
    ):
        raise ProjectError("Unsafe internal path")
    path = root
    for part in parts:
        path /= part
        if (
            path.is_symlink()
            or getattr(path.lstat() if path.exists() else None, "st_file_attributes", 0)
            & 0x400
        ):
            raise ProjectError("Project paths cannot cross links or reparse points")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ProjectError("Internal path escapes project")
    return path


def external(uri: str) -> Path:
    if type(uri) is not str or "\0" in uri or not Path(uri).is_absolute():
        raise ProjectError("Reference requires a native absolute path")
    if uri.startswith(("//", "\\\\")):
        raise ProjectError("Network and device paths are unsupported")
    return Path(uri)


def encode(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ).encode("utf-8")


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ProjectError("Duplicate JSON key")
        result[key] = value
    return result


def decode(raw: bytes, root: Path) -> dict:
    try:
        if len(raw) > LIMIT:
            raise ProjectError("Manifest too large")
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=_object)
        if type(value) is not dict or value.keys() != FIELDS:
            raise ProjectError("Unknown or missing manifest fields")
        if (value["format_id"], value["format_version"], value["schema_version"]) != (
            FORMAT,
            VERSION,
            SCHEMA,
        ):
            raise ProjectError("Unsupported project format or catalog schema")
        identity(value["project_id"])
        if (
            type(value["application_version"]) is not str
            or not value["application_version"]
        ):
            raise ProjectError("Missing application version")
        for key in ("created_at", "modified_at"):
            if datetime.fromisoformat(value[key]).utcoffset() is None:
                raise ProjectError("Timestamp requires a timezone")
        if value["project_crs"] is not None and (
            type(value["project_crs"]) is not str or not value["project_crs"].strip()
        ):
            raise ProjectError("Invalid project CRS declaration")
        if value["catalog_uri"] != "project.sqlite" or value["storage_policy"] not in (
            "mixed",
            "reference",
            "copy",
        ):
            raise ProjectError("Invalid storage policy or catalog path")
        if (
            type(value["default_profiles"]) is not dict
            or type(value["assets"]) is not list
        ):
            raise ProjectError("Invalid profiles or assets")
        seen = set()
        versions = set()
        for asset in value["assets"]:
            if type(asset) is not dict or asset.keys() != ASSET_FIELDS:
                raise ProjectError("Unknown or missing asset fields")
            key = identity(asset["asset_id"])
            version = identity(asset["source_version_id"])
            if (
                key in seen
                or version in versions
                or asset["role"] != "primary_dem"
                or type(asset["metadata"]) is not dict
            ):
                raise ProjectError("Invalid or duplicate source asset")
            seen.add(key)
            versions.add(version)
            mode = asset["storage_mode"]
            if mode == "reference":
                external(asset["uri"])
            elif mode == "copy" and asset["uri"].startswith("inputs/dem/"):
                internal(root, asset["uri"])
            else:
                raise ProjectError("Invalid source location")
            if value["storage_policy"] not in ("mixed", mode):
                raise ProjectError("Source mode does not match project policy")
            if not re.fullmatch(r"sha256:[0-9a-f]{64}", asset["checksum"]):
                raise ProjectError("Invalid source checksum")
        encode(
            value
        )  # Reject non-finite values, invalid Unicode and invalid nested data.
        return value
    except (ValueError, TypeError, AttributeError, RecursionError) as exc:
        raise ProjectError(f"Invalid project manifest: {exc}") from exc


def read(path: Path, root: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(LIMIT + 1)
    decode(raw, root)
    return raw


def checksum(path: Path) -> str:
    with path.open("rb") as stream:
        return "sha256:" + hashlib.file_digest(stream, "sha256").hexdigest()
