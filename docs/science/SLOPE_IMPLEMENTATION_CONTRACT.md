# Slope 1.0.0 implementation contract

Architecture review pending. Preparation base b2f76d70981097167415079ac2cbaa4f59ec19ac includes accepted Phase 3 scope and verified hardening d958322bdc95e51001a6d6d037d736c0a391a272.

## Proposed CCR-005

Preserve the existing Project.register_result keyword interface for Hillshade callers. Add an optional keyword slope with normalized SlopeParameters and make light optional. Require exactly one of light or slope. Select a fixed internal algorithm specification with runner, version, parameter serializer and metadata validator. Both branches use the existing private source snapshot, cancellation boundaries, durable publication and recovery.

Provenance schema 1 admits a second explicit algorithm/version pair slope/1.0.0 with its own exact parameter keys. Parameters are method=horn, vertical_metres_per_unit, output_unit=degree and mask_policy=all-nine-valid-internal. Validate finite positive conversion and known compatible source vertical units. Missing units require an explicit declared recognized unit, recorded in source metadata. Hillshade historical 2.0.0/2.0.1 validation and executable support remain independently checked. Unknown algorithms, versions and extra parameter keys fail. Slope output metadata has vertical_unit=degree and float32/nodata=-1/scale1/offset0 with preserved grid. The actual file must have an internal per-dataset validity mask and finite valid samples in [0,90]. The snapshot checksum covers mask and output bytes. Manifest 1.1 and SQLite 2 stay compatible. Public Wire messages remain unchanged.

Implement slope.py with an algorithm descriptor and Horn kernel. Reuse raster window, calibration and masked-read utilities. Share only the existing publication machinery. Preserve the established Hillshade numerical path. A tile contains 1024 core pixels per side with a one-cell halo. Set GDAL_TIFF_INTERNAL_MASK for the output creation context and write the binary mask for each window. Cancellation and progress use existing execution helpers.

Raw row-down/column-right derivatives divide weighted opposite-neighbor differences by 8. Multiply both by band scale and vertical metres/unit. Multiply the affine linear 2x2 matrix by horizontal metres/unit. Apply its inverse transpose to the derivative vector. Slope is degrees(atan(hypot(gx,gy))). Constant offset is excluded before derivatives. No exaggeration parameter exists.

## Test matrix before implementation

| Group | Evidence |
|---|---|
| Analytic planes | Flat and signed east/north/diagonal gradients, multiple steepnesses. Absolute error <=1e-5 degree in float32 interior. |
| Coordinates/units | Projected metre and US survey foot CRS, separate metre/foot vertical factors, anisotropic/rotated/skewed affine. Reject absent/geographic CRS, singular/nonfinite affine, unrecognized units and nonpositive factors. |
| Calibration | Scaled integer versus physical float, large constant offset, independent scalar Horn oracle. |
| Validity | Nodata -1, input internal mask, NaN/Inf, each missing neighbor, border, rasters smaller than 3x3, all-invalid output surfaced in metadata. Exact internal output mask. |
| Tiling | 1024 halo1 versus full-array oracle, partial edge tile, several tile sizes and identical masks. |
| Execution | Cancellation during read/compute/prepublication, callback exceptions, no partial output publication. |
| Project | Reference/Copy import, immutable input digest, output registration, strict provenance malformed cases, fresh process reopen/recovery and historical Hillshade fixture. |
| Resources | Explicit working-set estimate and runtime/peak RSS/temp disk/cancel measurements on 1k/5k/10k/20k fixtures, recorded per actual execution. |

OQ-20 and OQ-31 remain open for broader scientific and resource acceptance. This proposal covers Slope only.
