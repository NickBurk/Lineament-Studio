# Phase 2–3 vertical slice

## Run from a clean checkout

```sh
uv sync --locked --python 3.11
uv run --locked python scripts/vertical_slice.py /path/to/empty-smoke-directory
```

The directory's parent must exist. The command generates a Unicode-named GeoTIFF, adds it as Reference and Copy, reports actual Preflight metadata, calculates and registers Hillshade, then opens the project from a fresh interpreter. It verifies both source declarations, raw and physical elevation ranges, the published result, preservation of its provenance after relink and the original SHA-256. Reopening verifies the catalog projection and the result checksum. The base wheel remains importable without GIS dependencies. The locked GIS group supplies the native candidate for development.

## ARCHITECT_SELECTED for this slice

Manifest v1.1 owns identity, settings and source asset declarations. SQLite schema 2 owns results and their job/source references, publication intents and receipts. The catalog stores the last committed manifest bytes as a consistency witness and indexes source identities for foreign keys. Those copies are written only by Project Storage. The migration table records creation of schema 2. No earlier format is supported and no upgrade path is inferred. Unknown fields and versions are refused before rewrite.

Internal paths use portable relative names, with links and reparse points refused. References use native absolute local paths. Network/device URI forms are outside the supported profile. Both Reference and Copy require self-contained GeoTIFFs. A changed checksum on relink needs explicit confirmation. The project keeps a stable asset ID and an audit receipt. Source paths remain untouched and backup remains manual.

The supported profile is cooperating processes on a local filesystem with atomic replacement and byte-range/advisory lock support. A single lock covers reads, writes and recovery. SQLite WAL + FULL commits the PREPARED record and readback establishes its visibility. The stages are validate → allocate publication UUID → copy, flush and validate staging → commit/read PREPARED → promote checked artifact → install manifest → commit SQLite projection, result and receipt together → clean staging. Reopen replays the same intent, checks file digests and rejects an unknown prior/current state or unreadable catalog. An interrupted pre-intent copy may leave unreferenced cache files. A post-intent error can complete on reopen. A new calculation uses a new job UUID, while publication recovery replays the existing publication and result IDs. No wire fields were added.

The fault suite measures abrupt process termination. Device power-loss durability, remote storage and automatic repair of a corrupted SQLite catalog remain unverified. ADR-0003 and OQ-25–27 retain their existing status as broader project decisions. ACR-003 evidence in this PR is limited to the tested process-failure profile.

## GIS candidate and limitations

Rasterio 1.4.4 (BSD-3-Clause) provides a single GDAL/PROJ wheel stack with NumPy 2.4.6 (BSD-3-Clause). Native bundled components have their own notices and release review remains required. No second standalone GDAL, pyproj or Pyogrio wheel is installed. The runtime test inventories PROJ's database, available resources and drivers. It checks a known offline coordinate and GeoPackage raster and vector round-trips. Resource paths and GDAL/PROJ/GEOS DLL provenance are sampled in Windows CI. QGIS coexistence, grid-dependent transforms and the standalone installer still need Windows evidence before closing OQ-03/OQ-28.

## PRE-001 method and validation

Version 2.0.0 evaluates a Horn 3×3 stencil in float64, converting the pixel gradient to world gradients by the inverse transpose of the affine linear part. Elevation scaling is z-factor times vertical metres per unit divided by horizontal metres per unit. The raster must have a known projected CRS. Azimuth is clockwise from projected grid north and altitude is above the horizon. The configurable initial altitude is 45° per DEC-A11. Azimuth, z-factor and vertical scale are explicit inputs. The light vector is (cos altitude × sin azimuth, cos altitude × cos azimuth, sin altitude). A normalized surface normal (-dz/dx, -dz/dy, 1) is dotted with that vector and clamped to [0, 1].

Each tile reads a one-pixel halo. The outer border and any stencil containing masked or nonfinite data become NoData (-1). The output is float32 GeoTIFF with source grid and CRS, explicit parameters and version tags. No source array is mutated. The reference oracle uses analytic plane/flat gradients plus independent scalar stencils for discrete analytical fixtures. The engineering acceptance tolerance is max absolute error below 2e-7 in normalized intensity, allowing float32 rounding and affine-gradient arithmetic. The tile test requires identical values and mask for one-window and multiwindow runs. The oracle also records mean error. Representative scientific validation and comparison with the chosen GDAL/QGIS output encoding remain open under OQ-20.

| Priority crosswalk | FR | DEM Processing | Slice |
|---|---|---|---|
| Hillshade | PRE-001 P0 | P0 | Implemented |
| Multi-directional | PRE-002 P1 | P0 | OQ-30 |
| Slope | PRE-003 P1 | P0 | OQ-30 |
| Gaussian | No explicit FR | P0 | OQ-30 |

Phase 4 Detection Engine starts after Phase 2–3 integration acceptance, outstanding runtime and durability gates, and an approved detection task.

## TASK-AG01-08 development verification

`ARCHITECT_SELECTED` under the owner's restricted engineering authorization. This profile covers the new-project developer slice on local filesystems providing hard links, same-volume atomic rename and process locks. Legacy development manifests 1.0 / catalogs 1 are rejected before mutation. An explicit migration for legacy data remains outside this slice. Backup remains manual.

### Source and result identity

Each source declaration has a stable asset UUID and a source-version UUID bound to the SHA-256 of its self-contained TIFF. Matching-content relink preserves the version. Confirmed changed-content relink allocates a new version and stores old and new identities in the receipt. Results keep historical identities even when the current source declaration changes.

The storage adapter calculates Hillshade in a private temporary workspace. It hashes the copied input against the declared source version before processing, reads that copy throughout processing, checks it again afterwards and checks the current version and live source digest before PREPARED. A concurrently changed-content relink or detectable source modification is rejected. A same-content move can proceed with the same source version. The generated provenance schema 1 is validated and serialized as canonical UTF-8 JSON. It carries the source asset/version/digest, band and raster metadata, versioned algorithm and canonical parameters, dependency versions, UTC processing timestamp, output grid and checksum. The checked output digest binds the actual staged bytes to provenance. Arbitrary externally prepared rasters or caller-supplied provenance are outside the publication contract. Mutation by another actor with write access to private processing directories and activity after the PREPARED boundary are outside the supported concurrency model. Recovery publishes the already-verified snapshot output.

Import, availability, relink, processing and result publication reject recognized external companions, including masks, PAM XML, overviews and world files. GDAL is restricted to internal georeferencing with directory discovery, PAM and PROJ networking disabled. The adapter checks discovered files as well as companion names. It leaves rejected sources and companions untouched.

### PRE-001 calibration

Apply `physical = raw * band_scale + band_offset` exactly once in float64 after raw masking and filtering nonfinite samples. Report raw and physical ranges separately. Zero or negative scale, nonfinite calibration and overflow on valid pixels produce explicit errors. Version 2.0.0 changes calibrated-raster semantics. Equivalent float and calibrated integer GeoTIFFs, with or without offset, are checked on a rotated grid with NoData and multiple tile sizes. Output remains dimensionless. The explicit vertical metres-per-unit parameter supplies the unit scale when a TIFF lacks one and must agree with supported named units when present.

### ACR-003 process-failure state machine

| Stage | Persisted evidence and interrupted-run behavior |
|---|---|
| Initial create | Build manifest, directories and catalog in a sibling temporary directory and close SQLite before rename into place. A process death before rename may leave a temporary directory without exposing a project at the designated path. A successful atomic rename is the supported create boundary. Partial power-loss writes remain outside this guarantee. |
| Validate and stage | Compute and validate source version, result provenance and output digest. Write and flush exclusive staging. A death before committed PREPARED leaves the old state and may leave orphan temporary files. |
| PREPARED_COMMITTED | Commit intent in one SQLite transaction using WAL + FULL and verify exact readback. The lock covers the before/after manifest witnesses and the publication ID. Readback proves visibility for the process-failure profile. |
| Artifact promoted | Link the checked stage to an unused result path without overwrite. Recovery reuses an existing target only if its digest matches the intent. Damaged or missing artifacts fail closed. |
| Manifest installed | Write and flush sibling-volume temporary manifest, then replace atomically. Recognize only the exact old or intended bytes. |
| Catalog committed | In one SQLite transaction update project witness and projection, add the result row, link one receipt to the result ID and clear intent. Reopen checks projection and receipt linkage. |
| Cleanup | Drop project-owned stage and manifest temporaries after commit. A process death can leave orphan temporaries. Replaying pending recovery under the same lock cannot allocate a new result ID or receipt. |

The nonblocking project lock uses Windows byte-range locking or POSIX flock and spans project access and recovery. Tests cover abrupt independent subprocess death at eight Copy and eight result boundaries, repeat reopen, a second death during recovery, damaged staging/target, conflicting access, sharing interruption, disk-space rejection and corrupt SQLite. Power-loss durability remains **NOT VERIFIED**. Final product closure requires an agreed device/filesystem guarantee and corresponding interruption evidence or an explicitly accepted narrower product guarantee.

The candidate Rasterio/NumPy versions are retained. Windows/Linux candidate CI evidence covers Rasterio native resources, GeoTIFF/GPKG and offline coordinate transforms. Standalone Windows bundle, QGIS coexistence, grid-dependent transforms and native redistribution are release gates. The earlier eight Affine warnings came from Rasterio 1.4.4 calling Affine 3.0.1 multiplication in bounds and from_origin helpers. The slice now uses equivalent corner transforms with `@` and constructs the test affine directly. No filters or dependency changes are required.
