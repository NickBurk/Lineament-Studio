# Phase 3 Scope Decision Package

## 1. Executive Summary

**OPTION A SELECTED — DOCUMENTATION UPDATE FOR CHAT02 REVIEW.**
TASK-AG01-10 (2026-11-28) records delegated Owner authorization: DEC-A35 makes the
FR catalogue authoritative, preserving PRE-001 P0, PRE-002 P1 and bundled PRE-003 P1.
Gaussian/Median are excluded from current implementation scope pending separate
registration. The earlier proposal was independently reviewed at d7d071c (PR #11,
review 6095370708); that review does not accept this subsequent documentation delta.

Preparation base remains `f7a52f7dd5d96b89ccdd34bf1b820e66a3bd483a` on
`integration/phase-2-3-baseline`. PR #10 was merged by Owner from HEAD
`e933c2535c760320f1dbc169f0a8db83582f14d2`. The integration ref reached merge commit
`d958322bdc95e51001a6d6d037d736c0a391a272`. Verification of this merge remains pending. Owner's subsequent
manual GitHub Settings verification is separate evidence: no repository rulesets,
no displayed classic protection rules, zero collaborators and Owner-only direct
access. Screenshots were reported by Owner; Agent01 has not independently inspected
the image files. HTTP 403 limits connector inspection and is not evidence of a
GitHub merge block. Owner specifies manual CHAT02 review followed by Owner Merge;
no new rules, collaborators or configuration changes are required. Slope still
requires successful Ubuntu and Windows CI on the merge SHA and publication of the verified baseline.

Current branch `feature/agent01-phase-03-scope-package` contains documentation only.
Slope 1.0.0 is the first authorized future vertical slice, with frozen physical
contract and analytic-plane tolerance below. Its registration/publication adaptation
needs a CCR and architecture review before code. Other method cards remain candidates;
no Curvature/TPI/LRM definition or Gaussian/Median implementation is approved here.

## 2. Current Implementation Audit

Audit method: source/test inspection, not new execution. No code tests or scientific
benchmarks were run for this documentation task. Existing test references identify
real coverage; they do not imply a fresh PASS or full normative acceptance.

| Requirement / method | Base f7a52f7 | PR #10 e933c25 | Actual evidence |
|---|---|---|---|
| PRE-001 Horn Hillshade | Executable 2.0.0 | Executable 2.0.1; historical 2.0.0 validation | `src/lineament_core/science/hillshade.py`, provenance validator and science/data suites |
| PRE-002 multidirectional | NOT_STARTED | NOT_STARTED | No production implementation or dedicated scientific tests found |
| PRE-003 Slope | NOT_STARTED | NOT_STARTED | Same |
| PRE-003 Curvature | NOT_STARTED | NOT_STARTED | Same |
| PRE-003 TPI | NOT_STARTED | NOT_STARTED | Same |
| PRE-003 LRM | NOT_STARTED | NOT_STARTED | Same |
| Gaussian smoothing, no FR ID | NOT_STARTED | NOT_STARTED | Previously DEM P0, now unregistered/out of current scope; no implementation found |
| Median filtering, no FR ID | NOT_STARTED | NOT_STARTED | Previously DEM P1, now unregistered/out of current scope; no implementation found |

This distinction corrects a potential baseline misunderstanding: **2.0.1 is present
in PR #10, not in the permitted preparation base**. Future implementation must not
start from this document branch's old executable code.

PRE-001 details inspected in source:

| Aspect | Existing behavior / limitation |
|---|---|
| Operator | Horn 3×3 weighted differences; float64 arithmetic, inverse-transpose affine conversion |
| Calibration | Base applies raw*scale+offset before differences. PR #10 2.0.1 omits the constant offset for derivatives; retains original scale/offset in metadata |
| Units | Explicit positive vertical metres/unit and z-factor; projected CRS linear metres/unit factor; azimuth clockwise from projected grid north, altitude above horizon |
| CRS | Known projected, finite nonsingular affine; no silent reprojection; rotation/skew and anisotropic pixels handled |
| NoData | Raw active mask plus explicit raw NoData, nonfinite neighbors invalid; full 3×3 stencil required |
| Tiles | One-pixel halo; outside-raster border invalid; partial tiles and small rasters considered |
| Output | New single-band float32 GeoTIFF; normalized intensity [0,1], NoData -1; grid/CRS unchanged |
| Provenance | Strict schema 1, source asset/version/digest, band, parameters, dependency versions, UTC, output metadata/digest; storage computes from a private verified snapshot |
| Versions | Base validates only current executable VERSION. Hardening explicitly allows historical 2.0.0/2.0.1 and independently tests executable support; records are not rewritten |
| Coverage | Existing analytic/rotated/anisotropic/mask/tile fixtures and fresh-process project reopen; hardening adds large offset and historical project fixture |
| Remaining gates | Representative terrain, chosen GDAL/QGIS encoding/method comparison, scientific acceptance OQ-20/OQ-31, large-raster performance |

Real existing references at base:

- [hillshade.py](../src/lineament_core/science/hillshade.py),
  [raster.py](../src/lineament_core/infrastructure/gis/raster.py),
  [project.py](../src/lineament_core/infrastructure/data/project.py),
  [provenance.py](../src/lineament_core/infrastructure/data/provenance.py).
- [test_hillshade.py](../tests/science/test_hillshade.py):
  `test_analytic_oracle_and_tile_equivalence`, `test_physical_scaled_integer_matches_float`,
  `test_cancellation_and_small_raster`, `test_unsupported_calibration_fails_explicitly`.
- [test_result_provenance.py](../tests/data/test_result_provenance.py),
  [test_vertical_slice.py](../tests/integration/test_vertical_slice.py).

Hardening-only references are pinned externally so this base does not imply those
files/features are integrated:
[remediation plan](https://github.com/NickBurk/Lineament-Studio/blob/e933c2535c760320f1dbc169f0a8db83582f14d2/docs/security/RELIABILITY_SECURITY_REMEDIATION_PLAN.md),
[offset test](https://github.com/NickBurk/Lineament-Studio/blob/e933c2535c760320f1dbc169f0a8db83582f14d2/tests/science/test_offset_stability.py),
[historical/cancellation tests](https://github.com/NickBurk/Lineament-Studio/blob/e933c2535c760320f1dbc169f0a8db83582f14d2/tests/data/test_result_provenance.py).
Storage-adapter hardening does not establish production Worker terminal-status
integration, physical power-loss durability, generic orphan cleanup, untrusted
project safety, native SBOM security or compliant branch governance. LS-AUD-006–009
remain separate gates; none are closed here.

## 3. Requirements Conflict Matrix

The table records the **pre-decision** discrepancy at d7d071c for audit history.
DEC-A35 selects Option A and this revision aligns DEM Processing; former conflicts
are not presented as still unresolved PRE priorities. Scientific definitions remain open.


Sources: [FR catalogue](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md),
[DEM Processing §3](../03_ALGORITHMS/DEM_PROCESSING.md),
[Phase Breakdown](../11_DEVELOPMENT/PHASE_BREAKDOWN.md),
[Roadmap](../11_DEVELOPMENT/DEVELOPMENT_ROADMAP.md).

| Method | Current FR wording / priority | Other source wording / priority | Consequence | Alternatives / required Owner decision |
|---|---|---|---|---|
| Hillshade | PRE-001: «Система ДОЛЖНА строить Hillshade», P0 | DEM §3: Hillshade P0 | No priority conflict; implemented slice is not complete scientific acceptance | Retain P0; decide remaining scientific/product gates |
| Multidirectional | PRE-002: «Система ДОЛЖНА строить Multi-directional Hillshade», P1 | DEM §3: Multi-directional Hillshade P0 | MVP and v1.0 schedules differ | A: keep FR P1 and later align derivative doc; B: formally approve changing FR priority to P0 |
| Slope | PRE-003: «Система ДОЛЖНА поддерживать Slope, Curvature, TPI и LRM согласно приоритетам Roadmap», P1 | DEM §3: Slope P0 | Bundled FR conflicts with slope-specific MVP scope | A: retain PRE-003 P1; B: approve atomic requirement decomposition/priority decision before editing catalogue |
| Curvature | Same PRE-003 P1 | DEM §3: Curvature P1 | Priority agrees, mathematical definition absent | Retain priority; select curvature type, sign, scale and units |
| TPI | Same PRE-003 P1 | DEM §3: TPI P1 | Priority agrees, neighborhood/normalization absent | Retain priority; choose raw/standardized TPI and footprint |
| LRM | Same PRE-003 P1 | DEM §3: LRM P1 | Priority agrees, background estimator absent | Retain priority; choose local residual definition |
| Gaussian | No standalone FR ID or normative catalogue priority | DEM §3: Gaussian smoothing P0 | Untraceable mandatory MVP claim; arbitrary FR assignment would be unauthorized | A: await separate registration/scope; B: formally register requirement with approved priority |
| Median | No standalone FR ID or normative catalogue priority | DEM §3: Median filtering P1 | Same registration gap for v1.0 | Register explicitly or explicitly exclude from authorized implementation scope, without silently deleting DEM requirement |
| Phase scope | Phase Breakdown: Hillshade, slope, curvature/TPI/LRM «по приоритетам» | Roadmap: DEM Preprocessing; MVP says preprocessing generically | Neither resolves method-level contradiction or defines Gaussian/Median acceptance | Owner selects authoritative crosswalk; preserve phase numbering 0–14 |

ACR-004 is resolved for this PRE conflict by DEC-A35. OQ-30 remains OPEN for
other scope decisions. Existing FR priorities and OQ statuses remain untouched. Missing FR IDs are not invented here; method aliases below are
planning labels only.

## 4. P0/P1 Scope Options

**Option A selected by delegated Owner authorization.** Option B is retained only
as an unselected historical alternative; it does not authorize priority changes.


| Method | Option A — FR authority | Option B — DEM authority, requires formal reconciliation |
|---|---|---|
| Horn Hillshade | PRE-001 P0 | PRE-001 P0 |
| Multidirectional | PRE-002 P1 | Proposed P0; explicit Owner priority change required |
| Slope | PRE-003 P1 | Proposed P0; resolve bundled PRE-003 before catalogue changes |
| Curvature / TPI / LRM | PRE-003 P1 | P1; definition decisions still required |
| Gaussian | Unregistered; no assumed FR priority | Proposed P0 plus approved new FR registration |
| Median | Unregistered; no assumed FR priority | Proposed P1 plus approved new FR registration |

Option A preserves all catalogue priorities. This authorized revision aligns DEM
Processing and records the disposition of unregistered filters; the earlier conflict
matrix is retained as history. Option B requires a separate authorized catalogue change,
traceability and acceptance review. Option A is selected; Option B is not authorized.

Optional scheduling proposal: a small vertical sequence of Slope, multidirectional
and Gaussian after hardening integration. This older scheduling proposal is superseded: only Slope is authorized first;
Gaussian is excluded. No partial sequence completes PRE-003 or waives Curvature/TPI/LRM.
Owner must explicitly authorize each method and missing requirement registration.

## 5. Algorithm Technical Specifications

Slope §5.3 is the authorized engineering contract. Other cards are **candidates**,
not approved scientific definitions or implementation scope. Gaussian/Median remain
unregistered and excluded. The Slope analytic-plane tolerance is the explicit exception
to new tolerances remaining TBD.
Every card inherits the common input/output, safety, provenance and acceptance
requirements here. Method-specific deviations and unresolved choices are explicit.
All new numerical tolerances, cutoff choices and acceptance performance thresholds
are **TBD — OQ-20/OQ-14/OQ-31**, not inferred from Hillshade's tolerance.

### 5.1 Common contract inherited by every card

Input: selected band of a verified, self-contained local GeoTIFF snapshot, with
asset ID, immutable source-version ID and SHA-256. Validate dtype, shape, band,
active mask plus raw NoData, NaN/Inf, finite positive scale, finite offset,
transform, CRS, horizontal/vertical units and memory/disk admission before processing.
Do not mutate the source. Do not silently assign CRS, reproject or resample.

For derivative methods, propose known projected linear CRS with finite nonsingular
2×2 affine matrix A; geographic/missing/unknown CRS is rejected. Convert vertical
units to metres and horizontal units consistently. Raw differences times scale
avoid adding a constant offset that cancels mathematically. Detail already lost in
input floating representation cannot be restored. Check finite intermediate/output
values and document supported numeric range before acceptance.

Grid-preserving pixel filters may support geographic CRS only as explicit
pixel-space operators, never as metric radii; proposed first profile stays projected
for consistent project preflight. This profile restriction needs Owner approval.

Output: a new GeoTIFF on exactly the input grid/CRS; proposed single-band float32
for dimensionless/degree derivatives, float64 for elevation residuals/filters until
error analysis justifies float32. NoData must be documented and distinct from valid
values: -1 is suitable for [0,1] intensity or nonnegative slope, not signed elevation,
curvature or residuals. Proposed signed outputs use an internal validity mask and
an explicitly approved representable sentinel or NaN policy. No external sidecars;
validate mask behavior within the self-contained TIFF profile. Dtype/NoData decisions
are blockers, not silently chosen implementation details.

Per-result provenance: algorithm ID and independent version, provenance schema
compatibility, asset/version/digest, band and calibration, normalized parameters,
CRS/affine/bounds/resolution, horizontal/vertical/output units, mask/edge policy,
output dtype/NoData/checksum, software/dependency versions and explicit UTC date.
Record kernel/radius/halo/direction weights where applicable. Existing validator
only permits Hillshade, so generalization needs reviewed compatibility design;
no arbitrary caller-supplied output publication bypass is proposed.

Tiles read a method-sized halo, compute only their central ownership area, and
never pad at internal tile boundaries. Output mask must match the full-array oracle.
Proposed derivative policy invalidates any stencil containing masked/nonfinite cells
and outside-raster cells. Filter-specific normalized/masked alternatives are stated
below and require approval. Cancellation occurs between bounded reads/tiles and
before PREPARED_COMMITTED; late cancellation cannot misreport committed publication.
Progress is monotonic, completion notification follows actual result publication,
observer failures do not change the publication outcome. Existing committed results
survive failure/cancellation; uncertain publication uses existing reopen/recovery.

Dependency candidate for all cards: existing NumPy (BSD-3-Clause) and Rasterio
(BSD-3-Clause); transitive native licenses need separate verification. No dependency
is added here. Optional SciPy (BSD-3-Clause) would require measured benefit,
Python 3.11/Windows compatibility, size and license review before a separate change.
No default kernel/sigma/radius or numerical tolerance is invented.

### 5.2 Multidirectional Hillshade — PRE-002

Purpose: reduce directional shading bias, without assigning geological confidence.
Candidate mathematical contract: derive physical Horn gradient once; for each
azimuth alpha_i and altitude beta compute
`I_i=max(0, n dot l_i)` with normalized `n=(-gx,-gy,1)` and
`l_i=(cos(beta)*sin(alpha_i), cos(beta)*cos(alpha_i), sin(beta))`.
Then `I=sum(w_i*I_i)/sum(w_i)`. **Weighted Lambertian averaging is a proposal, not a
claim of equivalence to GDAL multidirectional illumination.** Owner must choose this
or a specifically cited GDAL/QGIS method and version before implementation.

- Inputs/CRS/units: common derivative contract; azimuth clockwise from projected grid north.
- Parameters/defaults: band, ordered directions, weights, altitude, vertical metres/unit,
  z-factor, tile/budget. Candidate eight azimuths at 45° spacing per DEC-A10 and altitude
  45° per DEC-A11 are starting settings; weights require explicit choice (uniform is
  a proposal). No hidden normalization or silently reordered directions.
- Bounds: nonempty finite azimuths [0,360), matching nonnegative finite weights with
  positive finite sum, altitude (0,90], positive finite scales. Define duplicate-angle
  policy; reject or normalize explicitly. Exaggeration must be provenance-visible.
- NoData/edge/output: common full-stencil policy, intensity [0,1], float32, NoData -1.
- Tiles/halo/memory: one pixel for Horn; stream directional accumulation, O(tile area)
  working memory rather than holding N complete rasters. Validate accumulation overflow.
- Version/provenance: proposed ID `multidirectional_hillshade`, initial version TBD;
  persist method definition, directions, weights, conventions, altitude and scales.
- Analytical fixtures: flat surface yields sin(beta); one direction equals the matching
  single Hillshade; inclined plane and independent scalar weighted-light oracle;
  unequal weights expose normalization errors. Masks, rotations and offsets mandatory.
- Numerical acceptance: range and exact mask invariants; max/mean/relative errors TBD
  OQ-20, including accumulation order and cross-engine method/encoding differences.
- Performance acceptance: direction-count scaling, peak RAM, halo/tile overhead and
  full benchmark sizes in §10; approved thresholds TBD OQ-14/OQ-31.
- Dependencies: common existing stack; no full GDAL Python binding required by this proposal.

### 5.3 Slope — PRE-003 contribution, authorized v1.0.0

Purpose: physical local inclination, no artificial vertical exaggeration.
Rasterio Affine(a,b,c,d,e,f) maps pixel increments `(column,row)` to CRS `(x,y)`
using `A=[[a,b],[d,e]]`. For Horn 3×3 raw partials `p_raw,q_raw`, positive band
scale s, vertical metres/unit v and horizontal metres/unit h:

```text
# Raw elevations at pixel centres, from the top row down
z1 z2 z3
z4 z5 z6
z7 z8 z9

p_raw = ((z3-z1) + 2*(z6-z4) + (z9-z7)) / 8
q_raw = ((z7-z1) + 2*(z8-z2) + (z9-z3)) / 8
p_m = p_raw * s * v
q_m = q_raw * s * v
A_m = h * A
g = inverse(transpose(A_m)) @ [p_m,q_m]
slope_deg = atan(hypot(gx,gy)) * 180/pi
```

Positive p points along increasing raster column (right), positive q along increasing
raster row (down). The affine maps these axes to world coordinates, including the
row sign on north-up grids. Applying another row sign flip would corrupt rotated grids.

Constant band offset cancels before differencing; retain original offset/scale in
provenance. Horizontal and vertical conversion are separate. Validate finite
positive scales/conversions, known compatible units and projected CRS; reject
missing/unknown/geographic CRS and singular/nonfinite affine. No implicit reprojection
or CRS assignment. Affine rotation/skew and anisotropic pixels are required cases.
No z-factor/exaggeration parameter for Slope v1.0.0.

Inputs: verified selected DEM band, strict common preflight/snapshot profile.
Algorithm ID `slope`, version `1.0.0`, method Horn 3×3, output degrees. Single-band
float32 GeoTIFF, NoData -1 with **internal validity mask**; grid/CRS exactly retained.
Any masked/nonfinite/NoData cell or outside-raster cell invalidates the full stencil.
Small rasters may produce no valid interior; report this explicitly, never invent slopes.

Initial tile 1024×1024, halo one pixel, CPU-only and bounded memory; budget 6 GB is
a starting Worker profile, not proven memory use. Admission includes native blocks,
intermediates, output mask and GDAL cache. Check cancellation between bounded IO,
preflight and tiles and immediately before publication; isolate callback exceptions.

Strict provenance includes source asset/version/checksum, band, algorithm/version,
Horn method, scale/offset, vertical and horizontal conversions, CRS/affine/output
grid, dtype/NoData/mask policy, parameters, output checksum, dependencies and UTC.
Publish only through existing Project Storage; propose CCR for method dispatch and
provenance adaptation, obtain architecture review before changing implementation.
No Manifest 1.1/SQLite 2 or public Wire change is authorized by this contract.

Analytical fixtures: flat zero, world planes in multiple directions, rotated/skewed
and anisotropic affine, metre/foot units, calibrated integer versus equivalent float,
large constant offsets, mask/NaN/Inf/borders/small rasters/partial tiles. **Maximum
absolute plane error <=1e-5 degrees**; no relative error criterion near zero.
This is the authorized float32 analytical fixture tolerance, not full scientific
acceptance; OQ-20/OQ-31 remain OPEN. Independent scalar Horn and analytic oracles
must distinguish finite-difference error from floating error.

Require tile/full equivalence, cancellation/callback regressions, import → processing
→ publication → fresh-process reopen and unchanged input digest. Benchmarks 1k/5k/10k/
20k squared must measure runtime, peak RSS, temporary disk and cancellation. Results
are **NOT RUN**; performance thresholds remain subject to evidence/OQ-14. Dependencies:
existing Python 3.11/NumPy 2.4.6/Rasterio 1.4.4 only, no SciPy/OpenCV/Qt.

For future curvature review, the same physical convention gives
`H_world=A_m^(-T) @ (s*v*H_raw) @ A_m^(-1)` when H_raw is the pixel Hessian.
This clarifies units/axes without selecting or authorizing a curvature estimator.

### 5.4 Curvature — PRE-003

Purpose: characterize local terrain bending. **Definition selection required.**
Candidate A: Laplacian `z_xx+z_yy` (units inverse metres for metre elevation/coordinates).
Candidate B: profile/plan curvature with explicitly cited formulas and sign conventions.
These are not interchangeable outputs; no implementation may label one as another.
A preliminary quadratic fit candidate is `z=c+ax+by+(r*x*x+2*s*x*y+t*y*y)/2` in
physical local coordinates; Hessian is [[r,s],[s,t]]. Transform a pixel-coordinate
Hessian by `A^(-T) H A^(-1)`; choosing fit/window versus finite-difference stencil
is another explicit method decision, not an approved algorithm.

- Inputs/CRS/units: common derivative contract with physical coordinates and vertical units.
- Parameters/defaults: curvature kind, estimator, neighborhood/support radius, edge/mask,
  scaling/sign, tile/budget. Kind/radius/defaults all TBD; dimensionless normalization
  cannot silently replace raw physical curvature.
- Bounds: finite nonsingular affine, sufficient samples and well-conditioned support;
  reject singular fits. Gradient-dependent profile/plan formulas need a documented
  zero-gradient rule; do not divide by zero on flat terrain.
- NoData/edge/output: propose invalidating incomplete support initially; signed float64
  candidate with approved internal mask/NoData; output units depend on selected definition.
- Tiles/halo/memory: radius of the selected finite stencil/fit, TBD; memory depends on
  fit buffers and neighborhood shape, admit before allocation.
- Version/provenance: proposed ID `curvature`, explicit kind/estimator/sign/window/version;
  initial version TBD. Changing definition requires a new version and historical validator.
- Fixtures: plane→zero Hessian; quadratic bowl/ridge with known Hessian; sinusoidal second
  derivative, rotated grids; compare discretization at several physical resolutions.
- Numerical acceptance: max/mean error against quadratic Hessian and independent chosen
  curvature formula; separate condition-number rejection limits and tolerances TBD OQ-20.
- Performance acceptance: fit/window-size scaling and §10 measurements, thresholds TBD.
- Dependencies: NumPy candidate (BSD-3-Clause); stable local fits need research before
  choosing optional numerical dependencies. Method citation and terrain validation TBD OQ-31.

### 5.5 Topographic Position Index — PRE-003

Purpose: elevation relative to its neighborhood. Candidate raw definition
`TPI=z_center-mean(z_neighbors)`; standardized TPI divides by neighborhood standard
 deviation and is a different mode requiring explicit zero-variance behavior.
Constant offset cancels; center raw samples before scaled accumulation.

- Inputs/CRS/units: common projected profile; radius proposed in physical metres, not pixels;
  neighborhood membership uses full affine offsets, including anisotropy/skew.
- Parameters/defaults: radius, disk/annulus/box shape, include/exclude center, minimum support,
  raw/standardized mode, edge/mask policy, tile/budget. Defaults all TBD.
- Bounds: finite positive radius, valid annulus inner<outer radii if selected, support count
  sufficient; cap kernel memory before allocation. Standardized zero variance needs a decision.
- NoData/edge/output: propose raw valid-neighbor mean only when center valid and approved
  minimum support satisfied; otherwise invalid. Outside-edge support and denominator
  changes must be explicit. Raw units metres, standardized dimensionless; float64 candidate.
- Tiles/halo/memory: maximum pixel offsets satisfying physical footprint; derive halo from
  affine inverse, not radius/pixel-X alone. Mask/count/sum buffers are budgeted.
- Version/provenance: proposed ID `tpi`, initial version TBD; footprint, radii, center inclusion,
  support threshold and normalization stored with common metadata.
- Fixtures: constant→0 raw, symmetric interior plane→0, impulse/step and quadratic feature
  with hand-enumerated neighbor means; masked neighborhoods and zero variance.
- Numerical acceptance: independent discrete footprint oracle, tile/mask invariants and
  raw/standardized tolerances TBD OQ-20; scientific radius choice TBD OQ-31.
- Performance acceptance: footprint-size scaling, running-sum optimization only for a
  mathematically matching box footprint; §10 thresholds TBD. Existing stack candidate.

### 5.6 Local Relief Model — PRE-003

Purpose: isolate local elevation residual. Candidate A: `LRM=z-B(z)` where B is an
explicit low-pass/background estimator. Candidate B: detrending surface from a
specified local fit. LRM is not silently defined as standardized TPI or a generic
high-pass raster. If B equals the TPI neighborhood mean, equivalence must be disclosed;
shared primitives are appropriate, duplicate subsystem creation is not.

- Inputs/CRS/units: common projected calibrated DEM; physical residual units metres.
- Parameters/defaults: background family, kernel/radius/sigma, fit order if relevant,
  mask/edge/minimum support, tile/budget; all definition defaults TBD.
- Bounds: validate selected estimator's parameters and conditioning. Constant-offset
  cancellation occurs on centered samples; detect reconstruction/float range loss.
- NoData/edge/output: residual only with valid center and valid background estimate;
  signed float64 candidate, approved internal mask/NoData; source grid unchanged.
- Tiles/halo/memory: background estimator's entire support; composed filters add required
  halos rather than taking an unjustified maximum. Fit/global methods may not admit
  bounded tiles; exclude them from first profile unless equivalence is established.
- Version/provenance: proposed ID `local_relief`, initial version TBD; background method,
  support, physical scale and numerical policy stored explicitly.
- Fixtures: constant→0; plane→0 for symmetric linear-preserving background away from edges;
  sinusoid attenuation residual, Gaussian-like hill and impulse/step with discrete oracle.
- Numerical acceptance: verify B independently and subtract centered data; method-specific
  errors/tolerance TBD OQ-20, terrain interpretation validation TBD OQ-31.
- Performance acceptance: bounded background working set and §10 benchmarks, thresholds TBD.
- Dependencies: existing stack candidate; choice depends on approved background method.

### 5.7 Gaussian smoothing — unregistered requirement

Purpose: a derived smoothed DEM, not source modification. Proposed initial contract
is **pixel-space** finite discrete Gaussian, not metric-radius smoothing:
`K(i,j)=exp(-i²/(2*sigma_x²)-j²/(2*sigma_y²))/sum(exp(...))` over explicitly chosen
integer radii. `out=sum(K*M*(z-c))/sum(K*M)+c`, with valid mask M and stable center c.
This normalized convolution excludes invalid samples; zero valid weight yields invalid.
Reconstruction of huge absolute elevations may still exceed output precision; do not
claim recoverable detail where input/output dtype cannot represent it.

- Inputs/CRS/units: common projected first profile; sigma in pixels, physical X/Y footprints
  reported using full affine. Elevation units preserved or explicitly converted to metres.
- Parameters/defaults: sigma_x/y, truncation and rounding rule producing integer radius,
  edge extension, preserve-invalid-center versus fill policy, minimum support, tile/budget.
  All defaults/cutoff values TBD; no borrowed library defaults without decision.
- Bounds: finite positive sigmas/truncation, finite computed radius, memory admission;
  radius-zero/identity behavior must be chosen explicitly rather than underflowing silently.
- NoData/edge/output: candidate truncated/renormalized valid support with invalid centers
  preserved; Owner may select another explicit rule. Outside-image and masked-cell behavior
  differ from padding a tile. Output float64 candidate and internal validity policy TBD.
- Tiles/halo/memory: per-axis radius halo; normalized convolution needs numerator and weight
  buffers. Separable kernels are allowed only if numerator and denominator match the 2D
  normalized oracle; never renormalize each pass in a way that changes the chosen method.
- Version/provenance: proposed ID `gaussian_smoothing`, initial version TBD; actual discrete
  radii, sigma units, truncation/normalization, support/edge/center policy recorded.
- Fixtures: constant preservation, discrete impulse kernel, step cumulative kernel response,
  Gaussian-like feature, negatives and large offsets, kernel larger than raster, masked holes.
- Numerical acceptance: independent enumerated discrete kernel (not just another call to
  the same filter library); max/mean/relative and reconstruction precision tolerances TBD OQ-20.
- Performance acceptance: sigma/radius sweep, separable versus full reference, RAM/halo
  overhead in §10; thresholds TBD. Existing NumPy implementation is a candidate; optional
  SciPy requires a separate justified dependency review. FR registration is mandatory first.

### 5.8 Median filtering — unregistered requirement

Purpose: suppress isolated elevation outliers while preserving some edges. Candidate
`median(valid samples in explicit footprint)`; for even valid counts the proposed
median is the mean of the two central order statistics, subject to Owner approval.
Positive affine calibration commutes with the median, but even-count arithmetic and
restoring offsets still need range/precision checks.

- Inputs/CRS/units: common projected first profile; explicit pixel footprint initially,
  not an implied physical radius. Output elevation units preserved/converted explicitly.
- Parameters/defaults: odd footprint dimensions or physical footprint alternative, shape,
  center preservation, minimum support, edge rule, tile/budget; defaults TBD.
- Bounds: positive integral dimensions for pixel mode, finite radius for metric mode,
  approved even-count behavior after masking, bounded neighborhood allocation.
- NoData/edge/output: proposed valid-neighbor median with invalid centers preserved;
  empty/insufficient support invalid. Edge policy TBD; signed float64 candidate with
  approved internal mask/NoData; int preservation cannot be assumed for even support.
- Tiles/halo/memory: footprint radius; avoid materializing (tile pixels × kernel pixels)
  arrays without admission. Bounded row/chunk selection may be needed.
- Version/provenance: proposed ID `median_filter`, initial version TBD; footprint,
  rank/even-count definition, support and mask/edge policy stored.
- Fixtures: constant and monotonic plane interior, isolated impulse removal for a selected
  majority-valid footprint, step edge, enumerated odd/even/masked support, negative elevations.
- Numerical acceptance: exact rank for representable odd counts; even-average/calibrated
  output precision tolerances TBD OQ-20. No noise-removal claim from visual similarity.
- Performance acceptance: footprint-size sweep and §10 benchmarks, thresholds TBD.
- Dependencies: existing NumPy/Rasterio candidate; optional SciPy has the same separate
  approval gate and must not silently select its edge/NoData semantics. FR registration pending.

## 6. Scientific Test Matrix

Planning aliases: H=existing Horn Hillshade, M=multidirectional, S=Slope,
C=Curvature, T=TPI, L=LRM, G=Gaussian, D=Median. These are not FR IDs.
All future tests are **PROPOSED / NOT RUN**. Every row applies to each listed method;
variant-specific oracles must be approved before executable acceptance is possible.

| Fixture / scenario | Methods | Why / independent expectation |
|---|---|---|
| Flat surface | H M S C T L G D | Constant gradients/curvature/residual zero; illumination sin(altitude); filters preserve constants |
| Inclined world plane | H M S C T L G D | Known gradient, zero Hessian; symmetric interior mean/median/filter behavior; reveals unit mistakes |
| Rotated/skewed affine | H M S C T L G D | Derivative/Hessian transformation and physical footprint correctness; pixel filters retain grid |
| Sinusoidal surface | H M S C T L G D | First/second derivative or discrete filter frequency response; median uses enumerated order statistics |
| Gaussian-like terrain feature | H M S C T L G D | Symmetry, locality, scale response, terrain residual; do not substitute continuous for discrete oracle |
| Impulse | H M S C T L G D | Stencil localization, explicit kernel/rank/background response |
| Step | H M S C T L G D | Discontinuity, ringing/edge policy, kernel cumulative response and rank behavior |
| NoData mask / hole | H M S C T L G D | Exact valid support and output mask; no sentinel contamination |
| NaN/Inf | H M S C T L G D | Treat as invalid input samples, reject invalid calibration/intermediates; output never silently corrupts |
| Different physical resolutions | H M S C T L G D | Unit-aware derivatives and metric supports; expose pixel-filter footprint changes |
| Integer/float32/float64 dtypes | H M S C T L G D | Calibration equivalence and representational limits, selected band checks |
| Large positive/negative calibration offset | H M S C T L G D | Offset invariance for differences/residuals; filters reconstruct offsets only within proven precision |
| Small rasters / smaller than kernel | H M S C T L G D | Full-stencil invalid output versus explicitly partial normalized support |
| Partial tiles | H M S C T L G D | No omitted/duplicated central pixels and correct clipped reads |
| Halo boundaries / seam-crossing features | H M S C T L G D | Same support as full reference across every tile edge |
| Unicode paths | H M S C T L G D | Real TIFF IO and reopened project identity |
| Long Windows paths | H M S C T L G D | Actual configured Windows long-path profile; fail explicitly where unsupported |
| Corrupted/truncated input | H M S C T L G D | Preflight/read errors preserve source and old results |
| Empty/zero-size raster or unreadable header | H M S C T L G D | Reject before processing; distinguish invalid container from all-NoData raster |
| All-NoData but positive dimensions | H M S C T L G D | Explicit empty-data behavior; never divide by zero or publish a plausible valid surface |
| Constant raster incl. negative elevation | H M S C T L G D | No spurious gradients; signed filter range and zero-variance policy |
| Foot/metre vertical and horizontal units | H M S C T L G D | Physical derivative equivalence; explicit units for filter/residual outputs |
| Invalid parameters / memory shortage | H M S C T L G D | Deterministic rejection before oversized allocation or publication |

For all methods, compare one-window output to multiple tile sizes including
nondivisors and kernel-larger-than-tile cases. Require identical grid and mask,
no seams, and approved numerical equivalence on valid pixels. Bitwise equality is
required only if the approved operation ordering guarantees it; otherwise use the
method-specific OQ-20 tolerance, including a documented seam error metric.

Record input SHA-256 before/after, output metadata/digest, deterministic parameter
normalization and repeated-run scientific equality. A different TIFF byte encoding
must not be confused with different pixel values; artifact identity and numerical
reproducibility are separate checks. Cancellation before the commit boundary must
leave no new result and preserve old results; after committed intent it must retain
recovery inputs and report the actual outcome. Callback exceptions are observations,
not cancellation. Corrupted recovery data must fail closed under the supported profile.
Progress must stay bounded/monotonic; an exception cannot create a second publication.

## 7. Given/When/Then Acceptance Criteria

The following are proposed exact future test references, **not existing tests**.
No PASS is assigned. The method tokens are `multidirectional`, `slope`, `curvature`,
`tpi`, `lrm`, `gaussian`, `median`. Parametrized references below expand once for
each of these seven tokens (for example `[slope]`). This defines six acceptance
layers for every method, rather than accepting numerical functions without storage.

### 7.1 Common per-method acceptance layers

| Layer / future reference | Given | When | Then |
|---|---|---|---|
| Unit: `tests/science/test_preprocessing_contracts.py::test_parameters[method]` | Valid parameter set and one altered invalid field, approved defaults | Normalize and validate parameters | Canonical units/defaults preserved; invalid fields rejected without allocating kernel/output |
| Scientific: method-specific references in §7.2 | Analytic/discrete fixture with independently defined oracle | Run selected operator on full window and tiles | Formula, masks, signs and approved error bounds hold; no seams |
| GIS: `tests/gis/test_preprocessing.py::test_grid_and_calibration[method]` | Equivalent physical float/calibrated integer TIFFs with rotated/skewed affine | Process real files | Correct physical result; CRS/affine/resolution unchanged; source digest unchanged |
| Storage: `tests/data/test_preprocessing_publication.py::test_roundtrip_provenance[method]` | Project with earlier result and verified source version | Publish, close and reopen from a fresh process | Correct algorithm/version/units/parameters/digest preserved; historical results remain available |
| Performance: `tests/performance/test_preprocessing.py::test_budget_and_scaling[method]` | Approved target machine, workload and memory budget | Run sizes/kernel sweeps and rejected budget case | Peak memory/runtime meet approved thresholds; refusal occurs before oversized allocation |
| Windows runtime: `tests/integration/test_preprocessing_windows.py::test_native_runtime[method]` | CPython 3.11 candidate Windows stack and real Unicode/long paths | Compute and reopen offline | Correct driver/resource use, numerical/grid equivalence and documented path behavior; no bundle claim |

Additional per-method fault references:
`tests/data/test_preprocessing_publication.py::test_cancel_and_recover[method]`:
Given prior committed output and a deterministic copy/checksum/preflight/tile/staging/
precommit interruption, when cancellation or process death occurs, then old artifacts
and checksums remain, precommit rollback cleanup and committed/uncertain retention
match accepted storage semantics, recovery is idempotent, and terminal status is
consistent where a separately approved Worker integration exists.

`tests/data/test_preprocessing_publication.py::test_callback_failure[method]`:
Given a progress observer that raises, when computing/publishing, then diagnostic
notification does not alter actual publication or cause duplicate results.

### 7.2 Method-specific scientific Given/When/Then

All future paths below are proposals. Each needs an independently implemented scalar
or analytic oracle and a frozen fixture manifest, never a self-comparison alone.

| Method / future reference | Given | When | Then / blocker |
|---|---|---|---|
| M: `tests/science/test_multidirectional.py::test_weighted_plane_oracle` | Plane with known physical gradient, explicit directions/unequal weights | Evaluate approved illumination combination | Matches weighted scalar light-normal dots; one direction equals H; zero-weight list rejected; tolerance TBD OQ-20 |
| S: `tests/science/test_slope.py::test_world_plane_oracle` | z=ax+by+c, transformed/anisotropic grid, known units | Apply Horn/world gradient | Degrees equal atan(hypot(a,b)); flat zero; offset changes do not change slope; max absolute plane error <=1e-5 degrees |
| C: `tests/science/test_curvature.py::test_quadratic_hessian_oracle` | World quadratic with known Hessian, approved curvature definition | Compute chosen estimator | Matches Hessian and chosen sign/units/formula; singular/flat profile special cases explicit; definition/tolerance TBD |
| T: `tests/science/test_tpi.py::test_discrete_neighborhood_oracle` | Explicit footprint and enumerated valid neighbors | Compute approved raw/standardized TPI | Center-minus-mean or approved standardization matches oracle; zero variance/support rule enforced; tolerance TBD |
| L: `tests/science/test_lrm.py::test_background_residual_oracle` | Known discrete background B and sinusoidal/feature DEM | Compute centered residual | z-B(z) matches independent B oracle and units; no invented detrending; definition/tolerance TBD |
| G: `tests/science/test_gaussian.py::test_discrete_masked_kernel_oracle` | Normalized finite Gaussian kernel, impulse/step and masked hole | Apply centered normalized convolution | Weights, support, edge/center rules and response match enumerated oracle; output precision/tolerance TBD |
| D: `tests/science/test_median.py::test_masked_rank_oracle` | Enumerated odd/even valid samples, outlier/step/negative fixtures | Select approved median | Correct order statistic/even policy and support mask; calibration equivariance within approved precision; tolerance TBD |

All seven also need `test_tile_equivalence`, `test_invalid_inputs` and
`test_large_offset` in their corresponding proposed science module. Test acceptance
requires method-specific max absolute, mean absolute and relative errors, with a
chosen near-zero rule so relative error is not divided by zero. Definitions,
thresholds and representative terrain corpus remain subject to OQ-20/OQ-31,
except the authorized Slope analytical-plane threshold <=1e-5 degrees.
Existing PRE-001 test tolerances are historical evidence only; they are not defaults
for slope degrees, curvature inverse-length or elevation filters.

## 8. Proposed Preprocessing Architecture

Existing [application.py](../src/lineament_core/application.py) contains
`AlgorithmRegistry`, `AlgorithmDescriptor`, `Algorithm` and `CancellationToken`.
Reuse these contracts; no second registry is proposed. Existing science code has
no Qt dependency; preserve Core independence from Desktop/QGIS UI.

Proposed flow after separate authorization:

1. Registry resolves explicit algorithm ID/version and validated canonical parameters.
2. Existing Project Storage owns source lookup, verified snapshot, source-version
   verification and publication. Existing GIS adapter owns TIFF IO/preflight.
3. Internal method adapter uses bounded tiles/halo and shared tested physical-gradient
   or neighborhood primitives, without a new generic processing framework.
4. Method-specific result validator checks grid, units, dtype/mask, output checksum
   and provenance before the last cancellation gate.
5. Existing PREPARED_COMMITTED/recovery/receipt protocol publishes checked bytes and
   actual result ID. No direct external-result registration bypass is allowed.
6. Historical validators remain separate from executable availability; adding a new
   version must not make prior supported outputs unreadable.

Potential future source layout (proposal only): `src/lineament_core/science/` method
modules alongside existing Hillshade, minimal internal shared kernels if justified,
and adapters inside existing `infrastructure/data/` and `infrastructure/gis/`.
Existing `Project.register_result` and strict provenance validator are Hillshade-
specific. They currently validate fixed Illumination and output fields; existing
provenance schema must not be weakened to arbitrary dictionaries. A reviewed
algorithm-specific dispatch/validation extension will be needed before real project
publication of another method. Whether that entails a public Core application port
change must be determined in a CCR, not assumed away or implemented in this package.

No public signatures, event fields or Worker protocol states are proposed as
approved changes. Use existing JobLifecycle COMMITTING semantics and cancellation
contracts; production Worker integration is a separate gate. Manifest 1.1 and SQLite
2 remain unchanged. If new provenance payloads cannot fit reviewed compatibility
rules without a schema change, stop and request explicit architecture/schema approval.
Do not use OQ-25–28's open status as permission for unilateral changes.

## 9. Implementation Sequence

Every row is a separate reviewable vertical task/PR or small commit sequence after
Owner authorization. The sequence is a proposal, not a priority change. Do not put
all methods into one large commit.

| Stage | Scope / IDs | Proposed modules and tests | Exit artifacts / acceptance | Risk and Owner prerequisite |
|---|---|---|---|---|
| 0 | Scope reconciliation; PRE-001/002/003, unregistered filters | This package; no production code | Option A selected, PRE-003 bundled, Gaussian/Median excluded, Slope engineering contract fixed; fresh documentation review pending | Remaining OQ-30/20/31 gates; no implicit FR closure |
| 1 | Integrated hardening baseline and method contracts; NFR-REL-002, NFR-REPRO-001 | Existing storage/registry/provenance; historical/cancel suites | Exact Owner-published merged SHA, Windows/Linux CI, reviewed adapter/CCR proposal | Post-merge CI and baseline publication pending; no algorithms on f7a52f7 |
| 2 | Slope first vertical slice if selected; PRE-003 contribution | science/slope candidate, existing GIS/storage validation, six test layers §7 | Real TIFF publication, fresh-process reopen, analytic errors, performance evidence | Units/exaggeration/output tolerance decisions; PRE-003 not fully satisfied |
| 3 | Multidirectional vertical slice; PRE-002 | science/multidirectional candidate, registry/provenance dispatch; all layers | Versioned method, weighted oracle, publication/recovery and Windows evidence | Chosen method must distinguish GDAL formula from proposed weighted mean |
| 4 | Gaussian vertical slice only if registered | science/gaussian candidate; normalized convolution and all layers | Kernel manifest, masked oracle, precision/runtime report, published derived DEM | Sigma/truncation/center/edge/output decisions; dependency approval if any |
| 5 | TPI vertical slice; PRE-003 contribution | science/tpi candidate and shared validated neighborhood primitive | Discrete footprint oracle, physical-radius/grid validation, published result | Footprint, normalization/support/defaults and tolerance approval |
| 6 | Curvature vertical slice; PRE-003 contribution | science/curvature candidate, Hessian/fit validation and all layers | Named curvature definition, sign/units/conditioning report and real project output | Definition and estimator research precede code |
| 7 | LRM vertical slice; PRE-003 contribution | science/lrm candidate reusing approved background primitive | Background and residual oracles, publication/reopen, memory report | Background/detrending choice and relation to TPI clarified |
| 8 | Median vertical slice only if registered | science/median candidate and bounded rank implementation | Odd/even masked rank oracle, range/memory report, publication/reopen | Footprint/even policy, FR registration and selected priority |
| 9 | Selected Phase 3 integration acceptance | tests/integration proposed suite; existing project and all selected adapters | One project with H and selected methods, fresh process reopen, source unchanged, independent review | All selected scientific and platform gates pass; omitted methods remain pending |

At each stage produce implementation references, executed test IDs/commands, exact
base/head, numerical metrics, runtime/peak RAM, CI/JUnit and residual risks. A subset
of PRE-003 does not satisfy its bundled Slope/Curvature/TPI/LRM requirement.
A schedule choosing only M/S/G must explicitly retain the remaining Phase 3 scope.

## 10. Performance and Memory Considerations

Authoritative target: [Performance Requirements](../09_SCIENCE_AND_QA/PERFORMANCE_REQUIREMENTS.md),
16 GB RAM CPU laptop, integrated graphics. Worker 6 GB and tile 1024×1024 are starting
engineering settings, not proven acceptance thresholds. Current Hillshade developer
function uses its own smaller admission defaults; do not misrepresent those as the
final Worker policy. OQ-14 sets evidence needed for tile/halo choices.

For a Bx×By core tile and halos rx,ry, expanded sample count is
`N=(Bx+2*rx)*(By+2*ry)`. Halo overhead ratio is
`N/(Bx*By)-1`. Admission must include raw/native block buffers, validity masks,
float64 intermediates, kernel weights, output buffers, GDAL cache, concurrent arrays
and fixed process overhead. Disk admission includes snapshot, staging and final
artifacts on their actual volumes; no unsupported free-space guarantee.

| Family | Working memory / time considerations |
|---|---|
| Horn / Slope | O(N) memory, O(core pixels) kernel work; stencil intermediates and IO buffers counted |
| Multidirectional | O(N) if directions accumulated, O(directions × pixels) lighting work; avoid full raster per direction |
| Curvature | Depends on finite stencil or local-fit design; design-matrix/solver buffers may dominate |
| TPI / LRM | Naive O(pixels × footprint samples); box running sums valid only for equivalent chosen footprint/mask contract |
| Gaussian | Separable finite kernel O(pixels × (rx+ry)) versus 2D O(pixels × rx × ry); numerator/denominator buffers counted |
| Median | Naive O(pixels × footprint samples) selection and potentially excessive neighborhood copies; explicit admission/chunking |

Benchmark 1k×1k, 5k×5k, 10k×10k, 20k×20k and approved mosaics, including mask-heavy
and kernel-larger-than-tile cases. Measure wall time, peak process RSS, CPU, temporary
and output disk, kernel/direction/tile overhead, cancellation latency and IO cache
conditions; record hardware, OS, dependency versions and input checksums. Compare
small full-array reference and bounded production runs; never use an unbounded
full reference on the 20k fixture just to demonstrate equivalence.

All new runtime/peak-memory/latency pass thresholds **TBD**, requiring Owner-approved
benchmark gates and scientific tolerance before implementation acceptance. No
performance or large-raster PASS is asserted by this document.

## 11. Windows/GIS Compatibility Risks

Keep candidate Python 3.11/Rasterio 1.4.4/NumPy 2.4.6 until a separately justified
change. New SciPy/OpenCV/GDAL bindings are not authorized. Avoid mixing independently
bundled GDAL/PROJ DLL stacks. Verify self-contained TIFF/internal masks and codecs,
Unicode and long-path behavior, locked/read-only files, temporary disk exhaustion,
resource closure and offline PROJ resources on Windows and Linux.

Candidate CI does not establish standalone Windows Bundle isolation, redistributable
licenses, grid-dependent transforms, QGIS coexistence or native vulnerability review.
Keep OQ-28, LS-AUD-008 and broader release gates open. Algorithms requiring geographic
or metric-grid transformations need an explicit GIS profile, not an implicit unit guess.

Storage profile remains local cooperating writers with the accepted locking and
PREPARED_COMMITTED protocol. Hard links/atomic replacement and filesystem behavior
must be part of runtime evidence. Power-loss durability is NOT VERIFIED; no automatic
migration/rollback or generic orphan cleaner is implied by preprocessing expansion.

## 12. Open Questions

| Existing question / gate | Decision or evidence needed for this package |
|---|---|
| OQ-14 OPEN | Kernel/tile/halo policy and measured memory/performance, not a universal tile default |
| OQ-20 OPEN | Per-method numerical tolerances, supported ranges, near-zero relative-error policy, independent oracle approval |
| OQ-30 OPEN / ACR-004 | Option A selected, PRE-003 bundled; Gaussian/Median excluded pending registration; broader OQ-30 remains OPEN |
| OQ-31 OPEN | Representative terrain corpus, held-out sites, method/cross-engine comparison, scientific acceptance responsibility |
| OQ-25/26/27 | Storage/provenance ownership and compatibility for new result types; no unilateral schema decision |
| OQ-28 | Windows native runtime, bundle, licensing and coexistence evidence |
| LS-AUD-006–009 | Cleanup/untrusted-project/native/governance gates remain separate; no security closure from this plan |
| Production Worker | Terminal status/cancel integration must be tested separately from storage-adapter behavior |

Method-specific outstanding decisions are in every card. None of the listed OQ,
ADR or finding statuses is changed by this document; the table reports planning
context, including separate hardening limitations.

## 13. Owner Decision Checklist

- [x] Option A selected by TASK-AG01-10; source-document PRE priorities aligned.
- [x] PRE-003 stays bundled; one Slope slice cannot close it.
- [x] Gaussian/Median excluded from current implementation scope; registration remains separate.
- [x] Slope is the first authorized vertical slice after integration gates; other
      normative methods remain pending and Gaussian/Median excluded.
- [ ] Select multidirectional formula/version, direction set and weights; confirm defaults.
- [x] Slope physical unit contract approved; no exaggeration; plane tolerance <=1e-5 degrees.
- [ ] Select curvature type, estimator, sign/units and zero-gradient behavior.
- [ ] Select TPI footprint, physical radius, center inclusion, normalization/support.
- [ ] Select LRM background estimator and clarify overlap with TPI.
- [ ] Select Gaussian/Median pixel or metric scope, kernel/footprint, edge/mask/center
      rules, parameter defaults, output dtype and NoData representation.
- [ ] Approve method-specific OQ-20 error bounds, numeric-range diagnostics and OQ-31
      terrain/cross-engine corpus; new tolerances remain TBD except the authorized
      Slope analytic-plane engineering tolerance <=1e-5 degrees.
- [ ] Approve performance benchmarks/thresholds and OQ-14 admission policy.
- [ ] Review whether application/provenance extension requires CCR/ADR; preserve
      existing public Core/Wire and Manifest 1.1 / SQLite 2 absent separate approval.
- [ ] Complete independent CHAT02 review of this package.
- [ ] Publish the exact authorized integrated hardening baseline and issue a separate
      implementation TASK-AG01. This document branch is not that baseline.

## 14. References

Repository documents read for this planning task:

- [AGENTS.md](../AGENTS.md), [Master specification](../MASTER_TZ.md),
  [Master navigation](../README_MASTER.md).
- [Functional requirements](../01_REQUIREMENTS/FUNCTIONAL_REQUIREMENTS.md),
  [Acceptance criteria](../01_REQUIREMENTS/ACCEPTANCE_CRITERIA.md).
- [DEM Processing](../03_ALGORITHMS/DEM_PROCESSING.md),
  [Phase Breakdown](../11_DEVELOPMENT/PHASE_BREAKDOWN.md),
  [Roadmap](../11_DEVELOPMENT/DEVELOPMENT_ROADMAP.md).
- [Decision Register](../12_PROJECT_CONTROL/DECISION_REGISTER.md),
  [Open Questions](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md),
  [Traceability](../12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md),
  [ACR-004](parallel/CONTRACT_CHANGE_REQUESTS.md).
- [Scientific Validation](../09_SCIENCE_AND_QA/SCIENTIFIC_VALIDATION.md),
  [Performance Requirements](../09_SCIENCE_AND_QA/PERFORMANCE_REQUIREMENTS.md),
  [Vertical slice method/evidence](PHASE_2_3_VERTICAL_SLICE.md),
  [Skill Routing](SKILL_ROUTING.md).
- PR #10 hardening remediation plan pinned in §2; not assumed present at this base.

Six Skills manually read and applied:

- [Requirements Engineer](../.agents/skills/requirements-engineer/SKILL.md): conflicts,
  normative identity, scope options and measurable GWT.
- [Software Architect](../.agents/skills/software-architect/SKILL.md): existing registry,
  layer boundaries, potential CCR and provenance/publication ownership.
- [GIS Engineer](../.agents/skills/gis-geospatial-engineer/SKILL.md): CRS/units, affine,
  masks, real-file IO, metadata and Windows runtime limitations.
- [Scientific Computing](../.agents/skills/scientific-computing-engineer/SKILL.md):
  candidate formulas, independent oracles, precision and explicit TBD tolerances.
- [QA Engineer](../.agents/skills/qa-test-engineer/SKILL.md): six acceptance layers,
  actual versus proposed tests, failures/cancellation and evidence scope.
- [Code Reviewer](../.agents/skills/code-reviewer/SKILL.md): exact revision distinction,
  no unsupported completion claims and documentation-only change review.

Scientific basis status: Horn and Lambertian definitions follow the inspected
existing implementation and slice specification. Slope is derived from that physical
gradient definition. Curvature Hessian, raw TPI, background-residual LRM, discrete
Gaussian and order-statistic Median are explicit mathematical proposals, not claims
of a selected external standard. Before implementation, chosen variants must receive
reviewed method citations/version-specific GDAL/QGIS comparison where relevant and
Owner-approved criteria under OQ-20/OQ-31. No external benchmark or citation review
has been represented as completed in this documentation task.

### TASK-AG01-10 execution state

Stage A interpretation is superseded by Owner's manual Settings evidence: no
repository rulesets or displayed classic protection rules; zero collaborators,
Owner-only direct access. API 403 is an inspection limitation, not a merge blocker.
Automatic review/check enforcement is absent according to Owner's evidence and is
retained as a governance risk; this is not automatic compliance with the earlier
protection proposal. The current authorized process is independent CHAT02 review
and Owner-controlled merge. Do not create rules, add collaborators or alter settings.

CHAT01 exercises the authority delegated by Owner for DEC-A35 and the Slope
engineering contract. CHAT02 supplies independent review of each submitted HEAD.
Owner controls merge and scope changes outside the delegation. Product acceptance
and broader numerical/performance thresholds remain subject to Owner decision.

PR #10 was merged at `d958322bdc95e51001a6d6d037d736c0a391a272`.
Verification requires the merge SHA, both CI jobs and their JUnit artifacts
before publication of the hardening baseline. Review of this document at an
earlier SHA covers only that revision.

Automated Core CI records the wheel, lint and regression suites configured on
the tested ref. Local scientific verification requires separate evidence of the
fixture, reference calculation, units, measured error, environment and command.
No local Slope experiment or benchmark was run for this documentation change.
OQ-20 and OQ-31 remain OPEN.
