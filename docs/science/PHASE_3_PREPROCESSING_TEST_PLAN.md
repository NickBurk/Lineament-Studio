# Phase 3 Preprocessing — Scientific Validation Test Plan

**Status:** test design only; no preprocessing implementation or numerical tolerance approved.
**Specification:** `03_ALGORITHMS/DEM_PROCESSING.md`; baseline `eab8396dc358ccf888b5ade00e5a76553c1fc602`.

## Scope and acceptance discipline

Methods in scope: hillshade, slope, curvature, topographic position index (TPI), local relief
model (LRM), and tiled processing. This plan defines fixtures and evidence to collect; it does not
select formulas, kernels, edge conventions, defaults or scientific constants. Where the existing
specification does not define them, status is **TBD** and approval is required before an algorithm
can pass. Candidate equation families below are test oracles only after an authoritative method
reference and exact implementation convention are chosen.

For each run, record method/version, full parameter set, input checksum, source and output metadata,
software/runtime versions, platform, thread count, environment, output checksum, wall time and peak
resident memory. The intended repeatability contract (bitwise or numerical) is **TBD** per method;
do not silently treat those as interchangeable.

## Synthetic fixture matrix

Generate arrays analytically in float64 first, then explicit conversions for other dtypes. Store
grid CRS, affine transform, units, nodata mask, expected interior/edge regions, generator expression
and checksum with each fixture. Values and grid spacings should be parameterized; no universal
scientific scale is assumed.

| Fixture | Construction / oracle | Main coverage |
|---|---|---|
| Plane | `z(x,y)=a x+b y+c`; analytic gradient is `(a,b)` and true slope is `atan(sqrt(a²+b²))` only after horizontal/vertical units and slope convention are fixed. | Slope orientation, units, interior error; hillshade direction after azimuth convention is fixed. |
| Known-slope plane | Select `a,b` from a declared target angle and orientation; derive coefficients from physical grid spacing. | Slope magnitude and direction; axis order/row direction. |
| Sinusoid | `z=A sin(kx x+φx) sin(ky y+φy)`; derive derivatives analytically. | Slope/curvature response, resolution sensitivity, phase and edge effects. |
| Constant | `z=c`. | Zero-derivative expectation for differential methods; undefined/degenerate normalization and zero-relief behavior must be specified. |
| Impulse | Constant background with one changed cell. | Kernel support, response symmetry, influence radius, tiled halo and dtype range. |
| Step | Two constant regions separated by a straight edge. | Edge response, smoothing/window support, boundary artifacts. |
| Paraboloid | `z=c+αx²+βy²+γxy`, with coefficients declared. | Curvature operator and sign/orientation convention using analytic first/second derivatives. |
| NoData mask | Apply explicit interior, edge-touching, narrow-gap and nodata-only masks to analytic surfaces. | Mask propagation, valid-neighbor policy, contamination prevention. |
| Nonfinite values | Place NaN and ±Inf separately and together, plus all-invalid case. | Required rejection/masking/warning behavior; no silent numeric output. |
| Raster edge/small arrays | Dimensions 1×1, 1×N, N×1 and smaller/equal/larger than each chosen kernel. | Explicit edge policy, padding and degenerate shapes. |
| Rotated affine | Nonzero affine rotation/skew with defined CRS and physical coordinates. | Gradient geometry and coordinate basis; verify no north-up assumption. |
| Resolution pair | Same analytic physical surface sampled at distinct cell sizes. | Dimensional scaling and convergence; compare only after method-specific normalization is defined. |
| Dtype/range | Float32/64 and supported integer types with safe, boundary and overflow-sensitive values. | Casting, overflow, rounding, output dtype and reproducibility. |

## Method validation contracts

| Method | Mathematical basis and required parameters | Expected behavior and fixtures | Metrics / unresolved items |
|---|---|---|---|
| Hillshade | Illumination from terrain orientation and a declared light vector; adopt an authoritative reference (e.g. selected GDAL algorithm) and exact azimuth convention before oracle generation. Inputs: azimuth, altitude, z-factor, horizontal/vertical units, multidirectional mode. | Flat plane response is spatially constant for fixed illumination; plane orientation changes response according to chosen convention. Constant surface, known-slope plane, rotated affine and edges required. | Compare against analytical illumination oracle and/or pinned reference implementation. MAE, max absolute error, directional bias, edge-region error. Formula variant, azimuth convention, scale units, clipping/rounding, edge policy and tolerance: **TBD**; approve with GIS/science owner. |
| Slope | Gradient magnitude mapped to angle or other explicitly declared output unit; authoritative derivative estimator and physical coordinate scaling required. | Plane must yield constant interior slope matching its analytic gradient after units are reconciled. Sinusoid/paraboloid test spatial derivatives; constant has zero gradient if defined. | MAE/max error in declared units, orientation error if aspect also emitted, edge vs interior error. Kernel/estimator, rotated-grid handling, vertical units, edge and NoData policy/tolerance: **TBD**. |
| Curvature | Named curvature definition(s), derivative operator, sign convention, scaling and units must be selected from an authoritative reference. The term “curvature” alone is not a unique mathematical contract. | Paraboloid and sinusoidal surfaces provide analytical first/second derivatives for the selected definition; plane is zero for second-derivative forms. | MAE/max error, sign agreement, spatial bias, resolution convergence. Which curvature (profile/plan/general/etc.), estimator, units, regularization and tolerance: **TBD**; block pass until selected. |
| TPI | Define center value relative to a specified neighborhood statistic and metric/geodesic neighborhood. Radius, shape, weighting and normalization must be declared. | Constant gives zero only if chosen definition preserves constants. Plane behavior depends on neighborhood symmetry and detrending; sinusoid/step probe scale response. | MAE/max against explicit discrete oracle, bias, valid-neighbor count. Neighborhood, physical radius, CRS rules, normalization, edge/NoData rule and tolerance: **TBD**. |
| LRM | Define as residual relative to a declared terrain background/smoothing operator; specify filter, scale, boundary and mask semantics. No unique operator follows from the name alone. | Constant residual expected zero only for constant-preserving operator; plane/paraboloid and sinusoid reveal trend removal and scale response; impulse reveals support. | Residual MAE/max against the selected operator oracle, mean residual, edge artifacts, scale sensitivity. Operator/kernel/scale, detrending, output units and tolerance: **TBD**. |
| Gaussian smoothing (P0) | Continuous Gaussian is a rotationally symmetric normal kernel; discrete implementation must declare sampled vs integrated weights and normalization. Parameters: sigma, truncation radius, pixel vs physical units, and X/Y spacing. For anisotropic pixels, physical isotropy requires spacing-aware sampling; exact rule TBD. | Independent oracle: constant surface (preservation under normalized complete support), centered impulse (discrete normalized kernel), step (independently convolved small fixture), a hand-calculated small array, NoData edge and tiled/full-array. Test multiple sigma/truncation values as parameters without asserting defaults. | Kernel sum/normalization error, impulse response against independently computed weights, MAE/max vs reference convolution, edge/mask-region error. Boundary extension, nodata renormalization vs propagation, minimum support, output dtype/rounding and tolerance **TBD**. |
| Median filtering (P1) | Order statistic over an explicitly defined neighborhood. Specify window dimensions and physical interpretation. Even sample count median convention must be declared (lower/upper/mean or other); do not infer. | Independent sorted-list oracle: impulse/outlier, constant, step, small array with expected medians enumerated by hand, partial NoData and nodata-only window. Test odd/even window policy separately; no Gaussian oracle reused. | Exact cell agreement for integer-preserving cases where policy yields it; otherwise value error by declared dtype conversion. Edge, NoData/minimum-valid-sample rules, even-window median definition, physical-resolution mapping, halo and tolerance **TBD**. |
| Multi-directional Hillshade (P0) | Multiple directional hillshades followed by a declared aggregation. Inputs include azimuth set, sun altitude, azimuth convention, z-factor/units and weighting/aggregation. DEC-A10/A11 are initial engineering profiles (8 azimuths at 45°, altitude 45°), not validated scientific parameters. | Flat surface; planes facing each tested direction; opposite/asymmetric orientations; rotated affine; NoData boundary; repeated/tiled runs. Independent per-direction illumination oracle precedes aggregate oracle. | Per-direction and aggregate MAE/max, directional symmetry/bias, edge/mask error, deterministic repeat and tiled/full comparison. Formula/aggregation/weights, clipping, nodata rule, azimuth convention and tolerances **TBD/Proposed** pending owner approval. |
| Tiled processing | Same method and parameters as full-array reference; tile core excludes halo. Required halo must follow the support/radius of the selected operator. | Compare tiled and full-array outputs for all fixtures, offsets, partial tiles, tile smaller than support, nodata crossing seams and rotated affine. | Exact equality if algorithm and execution permit; otherwise MAE/max plus method-approved tolerance (currently **TBD**). Measure seams separately, output checksum/repeatability, wall time and peak RSS. Halo, overlap and parallel reduction ordering: **TBD**. |

## DEM Preflight scenario matrix

Preflight diagnostics below are observable test expectations, not a proposal to add mandatory API
fields. A diagnostic may be represented through the existing approved contract; if that contract
cannot express a case, raise a Contract Change Request before implementation.

| Scenario | Expected diagnostic / test oracle | Permitted continuation |
|---|---|---|
| Missing, empty, corrupt, inaccessible or unsupported source | Distinguishable source/read failure with path-safe context; no crash, hang or false success. Verify original remains untouched. | Block processing until source is selected/repaired/readable; unsupported format remains blocked. |
| Malformed/missing raster metadata | Report which metadata cannot be read; never invent dimensions, transform or CRS. | Block operations requiring missing/invalid metadata; allow only explicitly metadata-independent inspection if defined. |
| CRS missing vs unknown | Report absent CRS distinctly from present but unrecognized/unsupported CRS. Never assign a guessed CRS. | No CRS-dependent transform or metric-distance operation; user-directed CRS assignment belongs to an explicit derivative workflow. |
| Invalid affine transform or resolution | Report non-finite/singular transform or zero/negative/non-finite pixel resolution; preserve raw source metadata for diagnosis. | Block spatial derivative/resampling; any exception needs a method-specific documented basis. |
| Band count/selection | Report available band count and invalid requested band; valid selected band is traceable. | Continue only with a valid explicit/defined default band. |
| NoData value and mask | Distinguish absent nodata declaration from declared value; inspect mask validity; report inconsistent/invalid mask metadata. | Continue with explicit valid-cell semantics; nodata-only input blocks numerical processing. |
| NaN/Inf and nodata-only | Report nonfinite counts/valid fraction; nodata-only has no valid samples. | Method-specific policy required; no silent replacement. Nodata-only blocks all numerical derivatives. |
| Source and vertical units | Report known/unknown units and whether vertical/horizontal units are compatible for slope/illumination. | Unit-dependent algorithms blocked until explicit conversion/interpretation; non-unit-dependent metadata inspection may continue. |
| Rotated/skewed grid | Report full affine transform and physical pixel basis; test not assuming north-up. | Continue only for algorithms whose coordinate handling supports that transform. |
| Resource estimate | Report dimensions, dtype-based estimate and available-space/RAM estimate inputs; estimator uncertainty is visible. | Large operation may be declined/deferred under existing resource policy; no silent full-array allocation promise. |
| Reopen source | Close and reopen same source, compare read metadata and fixture samples/checksum; detect stale/locked handle. | Continue if stable; otherwise report read/consistency failure and block dependent processing. |

Requirement-to-test-plan mapping: DATA-001/002/008/009 → the Preflight matrix and synthetic fixture
matrix; DATA-006 → metadata-preserving CRS/transform checks; DATA-007 → resource estimate and
benchmark protocol; PRE-001 → P0 Hillshade, Multi-directional Hillshade, Gaussian smoothing, Slope;
PRE-002/PRE-003 → P1 Curvature, TPI, LRM, Median filtering. These are plan mappings only and do
not claim implementation or verification.

### Common spatial and missing-data rules

- Require known CRS semantics and linear units where metric distances or derivatives need them; do
  not apply metre radii directly in angular coordinates. Unknown/missing CRS must not be guessed.
- Preserve source transform, bounds, resolution, CRS, dtype and nodata metadata unless a declared
  derivative output policy changes one of them; record every such change.
- Do not alter source DEM. Nonfinite and nodata behavior must be explicit for each method.
- Report edge and interior metrics separately. Never hide edge behavior inside one global score.
- Tolerances are not supplied by this plan. Set them from method derivation, reference implementation
  behavior, floating precision/error propagation and intended scientific use; identify the approving
  GIS/scientific owner before gating.

## Tiled equivalence and resource protocol

For each finite-support operator, derive halo from its declared dependency radius. For operators
with global/adaptive dependencies, define a valid tiled strategy or classify exact equivalence as
unsupported. Process the same analytic raster as one array and with tile grids whose origins are
shifted relative to the surface. Include full tiles, partial edge tiles, narrow rasters, tile
smaller than halo, and nodata regions crossing boundaries. Compare only core pixels; separately
inspect output around every seam and outer raster edge. Test overlap handling to ensure each output
cell is written once or follows a defined deterministic merge rule.

Record per case: tile shape, halo, overlap, order, concurrency, peak RSS, elapsed time, output
checksum, seam MAE/max error and full-array difference. Repeat after changing tile traversal and
thread count. Establish whether determinism is bitwise or tolerance-based only after method owners
approve it. Resource targets are **TBD** and require benchmark hardware/profile; do not infer them
from the 1024×1024 initial engineering tile or 6 GB initial worker budget in Master TZ.

## Test execution sequence and gate

1. Approve exact mathematical definition, units, input CRS requirements, parameters/defaults,
   NoData/NaN/Inf behavior, edge policy and version for each method.
2. Implement an independent analytic oracle/generator; verify fixture expressions and metadata.
3. Run minimal interior analytic checks, then dtype/resolution/rotated-grid and degenerate cases.
4. Run mask/nonfinite and edge cases; require explicit expected warning/error or output semantics.
5. Run tiled/full-array equivalence across tile offsets, seams, halo sizes and traversal orders.
6. Run repeatability checks on the declared platform/runtime and compare outputs by approved rule.
7. Benchmark wall time and peak RSS on named representative hardware; include I/O and computation
   separately where feasible.
8. Review all errors, edge/seam maps, provenance, metadata and checksums; publish evidence before
   claiming a Phase 3 method validated.

**Pass gate:** all method definitions and numerical tolerances approved; all fixtures produce the
declared outcomes; no unreported geospatial metadata drift; tiled result meets the approved
equivalence rule; reproducibility and performance evidence are recorded. Any TBD scientific
contract item makes that method's gate **BLOCKED**, not provisionally passed.
