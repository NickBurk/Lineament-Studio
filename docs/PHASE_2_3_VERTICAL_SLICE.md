# Phase 2–3 vertical slice

## Run from a clean checkout

```sh
uv sync --locked --python 3.11
uv run --locked python scripts/vertical_slice.py /path/to/empty-smoke-directory
```

The directory's parent must exist. The command generates a Unicode-named GeoTIFF, adds it as Reference and Copy, reports actual Preflight metadata, calculates and registers Hillshade, then opens the project from a fresh interpreter. It verifies both source declarations, the published result and the original SHA-256. Reopening verifies the catalog projection and the result checksum. The base wheel remains importable without GIS dependencies. The locked GIS group supplies the native candidate for development.

## ARCHITECT_SELECTED for this slice

Manifest v1.0 owns identity, settings and source asset declarations. SQLite schema 1 owns results and their job/source references, publication intents and receipts. The catalog stores the last committed manifest bytes as a consistency witness and indexes source identities for foreign keys. Those copies are written only by Project Storage. The migration table records creation of schema 1. No earlier format is supported and no upgrade path is inferred. Unknown fields and versions are refused before rewrite.

Internal paths use portable relative names, with links and reparse points refused. References use native absolute local paths. Network/device URI forms are outside the supported profile. Copies must be self-contained GeoTIFFs. A changed checksum on relink needs explicit confirmation. The project keeps a stable asset ID and an audit receipt. Source paths remain untouched and backup remains manual.

The supported profile is cooperating processes on a local filesystem with atomic replacement and byte-range/advisory lock support. A single lock covers reads, writes and recovery. SQLite WAL + FULL commits the PREPARED record and readback establishes its visibility. The stages are validate → allocate publication UUID → copy, flush and validate staging → commit/read PREPARED → promote checked artifact → install manifest → commit SQLite projection, result and receipt together → clean staging. Reopen replays the same intent, checks file digests and rejects an unknown prior/current state or unreadable catalog. An interrupted pre-intent copy may leave unreferenced cache files. A post-intent error can complete on reopen. A new calculation uses a new job UUID, while publication recovery replays the existing publication and result IDs. No wire fields were added.

The fault suite measures abrupt process termination. Device power-loss durability, remote storage and automatic repair of a corrupted SQLite catalog remain unverified. ADR-0003 and OQ-25–27 retain their existing status as broader project decisions. ACR-003 evidence in this PR is limited to the tested process-failure profile.

## GIS candidate and limitations

Rasterio 1.4.4 (BSD-3-Clause) provides a single GDAL/PROJ wheel stack with NumPy 2.4.6 (BSD-3-Clause). Native bundled components have their own notices and release review remains required. No second standalone GDAL, pyproj or Pyogrio wheel is installed. The runtime test inventories PROJ's database, available resources and drivers. It checks a known offline coordinate and a GeoPackage raster round-trip. Mounted resource paths and GDAL/PROJ/GEOS DLL provenance are sampled in Windows CI. Vector GeoPackage operations, QGIS coexistence, grid-dependent transforms and the standalone installer still need Windows evidence before closing OQ-03/OQ-28.

## PRE-001 method and validation

Version 1.0.0 evaluates a Horn 3×3 stencil in float64, converting the pixel gradient to world gradients by the inverse transpose of the affine linear part. Elevation scaling is z-factor times vertical metres per unit divided by horizontal metres per unit. The raster must have a known projected CRS. Azimuth is clockwise from projected grid north and altitude is above the horizon. The configurable initial altitude is 45° per DEC-A11. Azimuth, z-factor and vertical scale are explicit inputs. The light vector is (cos altitude × sin azimuth, cos altitude × cos azimuth, sin altitude). A normalized surface normal (-dz/dx, -dz/dy, 1) is dotted with that vector and clamped to [0, 1].

Each tile reads a one-pixel halo. The outer border and any stencil containing masked or nonfinite data become NoData (-1). The output is float32 GeoTIFF with source grid and CRS, explicit parameters and version tags. No source array is mutated. The reference oracle uses analytic plane/flat gradients plus independent scalar stencils for discrete analytical fixtures. The engineering acceptance tolerance is max absolute error below 2e-7 in normalized intensity, allowing float32 rounding and affine-gradient arithmetic. The tile test requires identical values and mask for one-window and multiwindow runs. The oracle also records mean error. Representative scientific validation and comparison with the chosen GDAL/QGIS output encoding remain open under OQ-20.

| Priority crosswalk | FR | DEM Processing | Slice |
|---|---|---|---|
| Hillshade | PRE-001 P0 | P0 | Implemented |
| Multi-directional | PRE-002 P1 | P0 | OQ-30 |
| Slope | PRE-003 P1 | P0 | OQ-30 |
| Gaussian | No explicit FR | P0 | OQ-30 |

Phase 4 Detection Engine starts after Phase 2–3 integration acceptance, outstanding runtime and durability gates, and an approved detection task.
