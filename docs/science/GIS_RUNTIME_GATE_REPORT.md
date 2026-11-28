# GIS Runtime Validation Gate — Phase 1 Evidence

**Status:** validation plan and partial static evidence; Windows runtime **NOT VERIFIED**
**Baseline:** `eab8396dc358ccf888b5ade00e5a76553c1fc602`
**Branch:** `feature/agent03-gis-runtime-gate`
**Scope:** autonomous Windows x64 bundle, CPython 3.11; no production runtime selection.

## Executive result

No Windows GIS runtime was available in this execution environment. Therefore no Windows wheel
was installed or loaded, no native library path was observed at runtime, and no geodata round-trip,
CRS/grid operation, clean-machine bundle, or QGIS isolation result is claimed. Existing
`DEPENDENCY_COMPATIBILITY.md` records Phase 0 Linux-host wheel resolution and archive inspection;
that evidence is useful for designing the gate but does not pass it. ADR-0004 remains **Proposed**;
OQ-03 remains **Open**; OQ-28 remains **Proposed** as instructed.

## Environment observed for this report

| Item | Observation |
|---|---|
| Host | Linux x86_64, glibc 2.41 |
| Python | CPython 3.12.14 (not target CPython 3.11 Windows) |
| SQLite module | 3.53.1 from host Python |
| PySide6, Rasterio, GDAL Python bindings, pyproj, Shapely, Pyogrio | Not installed; imports unavailable |
| Windows x64 / clean Windows VM | NOT VERIFIED / unavailable |
| Installed QGIS coexistence/isolation | NOT VERIFIED |

Commands actually run: `python -V`; Python imports/version probe for `rasterio`, `osgeo`,
`pyproj`, `shapely`, `pyogrio`, `PySide6`, `sqlite3`; `platform.platform()` and `sys.version`.
No GIS tests were run. No runtime DLL inventory was available from this host.

## Compatibility evidence matrix

The following candidate observations are transcribed from the existing Phase 0 dependency report;
they are not reproduced by this task and are not Windows execution evidence.

| Component/profile | Existing static evidence | Runtime gate status |
|---|---|---|
| CPython 3.11 x64 | Target line identified; exact security build not selected | NOT VERIFIED |
| PySide6 6.11.3 | `cp310-abi3-win_amd64` wheel reportedly resolved for target | NOT VERIFIED: import, Qt plugins, clean bundle |
| Rasterio 1.4.4 | CP311 Windows wheel; wheel archive reportedly contains GDAL 3.10.3 string and GIS data | NOT VERIFIED: GDAL load, drivers, IO, closure |
| GDAL / Rasterio-bundled | Archive inspection only; standalone GDAL wheel-only resolution reportedly failed | NOT VERIFIED |
| pyproj 3.7.2 / PROJ | Archive reportedly carries PROJ 9.5.1, data layout 1.4 | NOT VERIFIED: selected DB, grids, transformation |
| Pyogrio 0.13.0 | Separate archive inspection reportedly found GDAL 3.12.4, PROJ 9.8.1, GEOS and SQLite DLLs | NOT VERIFIED; not in reported 24-package resolution |
| Shapely 2.1.2 / GEOS | Archive reportedly bundles GEOS DLLs | NOT VERIFIED: load and interoperability |
| SQLite / RTree | Python SQLite is build dependent; archives reportedly contain SQLite DLLs | NOT VERIFIED: target module, GPKG, RTree, locking |
| GeoTIFF / BigTIFF / COG | Drivers must be tested from selected GDAL build | NOT VERIFIED |
| GeoPackage | GPKG driver and profile undecided | NOT VERIFIED |
| Single-channel build | conda-forge mentioned as candidate alternative, without runtime validation | NOT VERIFIED |

### DLL and data-directory risk inventory

| Native resource | Evidence/risk | Evidence required to close |
|---|---|---|
| GDAL DLLs | Rasterio and Pyogrio archive inventory reports different GDAL release strings. Loading precedence and ABI coexistence are unknown. | Capture loaded module paths after each import order and operation; correlate hashes, PE architecture and package ownership. |
| PROJ DLL and `proj.db` | Reported PROJ 9.6.0 / layout 1.5 / EPSG 12.004 (Rasterio), 9.5.1 / layout 1.4 / EPSG 11.022 (pyproj), and 9.8.1 / layout 1.6 / EPSG 12.029 (Pyogrio). A process-global `PROJ_DATA` may select incompatible data. | At runtime record each library path, effective search path and exact database path/metadata; test import orders, CRS transforms and offline grids. |
| PROJ grids | Presence, licensing, selected operation and network fallback not established. | Inventory shipped grids and checksums; run known transformations with network disabled and report chosen operation/accuracy. |
| GEOS DLLs | Shapely and GDAL-family wheels may load distinct copies. Cross-library native pointers must not be exchanged. | Record loaded paths; exchange geometry through a stable serialized format and test validity/round-trip. |
| SQLite DLLs | Python sqlite3 and GDAL-family packages may use separate SQLite builds. | Record module paths/versions; test DB and GPKG independently, RTree, locking and reopen. |
| `GDAL_DATA`, `PROJ_DATA`, `PATH` | Actual Windows discovery and precedence unknown. | Run with sanitized and deliberately modified PATH; log effective data dirs; prove bundle-local resources are selected. |
| QGIS isolation | No QGIS installed in this environment. | Repeat clean VM tests without QGIS, then with QGIS installed and PATH altered; ensure no external DLL capture. |

## Required Windows validation sequence

Run on a disposable clean Windows x64 VM using the nominated CPython 3.11 build and then the
packaged Onedir artifact. Record OS build, account type, architecture, package hashes, commands,
exit codes, loaded module paths, environment variables, driver lists, data directory inventory and
logs. Keep **wheel-profile** and **unified-channel profile** as separate experiments; do not mix
their site-packages or DLL directories.

1. Install/import Python, PySide6, Rasterio, `osgeo` if selected, pyproj, Pyogrio if selected,
   Shapely; record Python/Qt/GDAL/PROJ/GEOS/SQLite versions, module files and loaded DLL paths.
2. Record GDAL raster/vector drivers; verify GTiff, BigTIFF, COG and GPKG creation/open support.
3. Round-trip fixtures with CRS, affine transform including rotation, pixel resolution, dtype,
   nodata/mask, bounds and dimensions. Reopen after closing handles; repeat operations to detect
   file-lock/resource leaks.
4. Transform a documented control coordinate between geographic and projected CRS; check
   longitude/latitude axis order explicitly, compare against an independently sourced expected
   coordinate and record selected operation. Repeat offline with required grid files present and
   absent; record fallback/failure behavior.
5. Use paths containing Unicode, spaces and Windows long-path length; test non-admin account,
   read/write permissions, copy and reopen. Record Windows long-path policy used.
6. Test import orders for Rasterio, pyproj, Pyogrio, Shapely and SQLite. Repeat with hostile
   `PATH`, unset and explicit `GDAL_DATA`/`PROJ_DATA`, and a machine with QGIS installed. Confirm
   all resolved modules and resources belong to the intended isolated profile.
7. Build portable Onedir and installer; install/run on clean Windows with no Python, no QGIS and
   no internet, under a standard user, from Unicode/space-containing install and data paths.
   Repeat after PATH modification. Capture module/data inventory and verify offline raster/vector/
   transform cases.
8. Produce SBOM and license/notice inventory for the exact locked artifact; scan advisories and
   document redistributable VC runtime and update policy.

## Risks and decisions still open

- Conflicting GDAL/PROJ/GEOS/SQLite DLLs and PROJ databases are **credible archive-level risks**,
  not confirmed runtime conflicts. Coexistence has neither been confirmed nor disproved.
- One-channel/unified GIS build may reduce version skew but its Windows packaging, Qt coexistence,
  licensing and reproducibility remain unverified.
- Wheel resolution and embedded DLL metadata do not establish functional drivers, resource lookup,
  axis behavior, numerical transformation correctness or bundle independence.
- No dependency/version/runtime choice is made here. Send any shared dependency proposal to Agent01.
- OQ-03 closure requires successful locked Windows integration tests and owner review. OQ-28 remains
  Proposed per task instruction; no open-question document was modified. ADR-0004 stays Proposed.
- License statements must be generated from the eventual exact artifact/SBOM; candidate metadata is
  not a distribution license review.

## CHAT02-AG03 handoff evidence (2026-11-27)

- Initial checkout SHA was `b0425dd0671d1179b15e05572851cc677ebe502f`; confirmed branch
  `feature/agent03-gis-runtime-gate` and clean status at start of this continuation.
- Exact common base is `eab8396dc358ccf888b5ade00e5a76553c1fc602`; both referenced source documents
  (`DEPENDENCY_COMPATIBILITY.md`, ADR-0004) exist at that baseline. PR #7 targets
  `integration/phase-1-baseline`; Issue #5 is the existing assignment.
- Branch was originally created from the exact clean detached baseline in the prior task run. This
  continuation verified the existing branch and base relationship; it did not recreate the branch.
- Skills read in the repository: requirements-engineer, software-architect,
  data-architecture-engineer, qa-test-engineer, python-desktop-developer, code-reviewer,
  gis-geospatial-engineer, scientific-computing-engineer,
  geomorphology-structural-geology-expert, ui-ux-designer, release-engineer.
- Specifications/documents read for this task: `AGENTS.md`, `MASTER_TZ.md`, `README_MASTER.md`,
  `11_DEVELOPMENT/AI_AGENT_INSTRUCTIONS.md`, `docs/SKILL_ROUTING.md`,
  `docs/architecture/DEPENDENCY_COMPATIBILITY.md`,
  `docs/architecture/adr/ADR-0004-WINDOWS-GIS-RUNTIME.md`,
  `12_PROJECT_CONTROL/OPEN_QUESTIONS.md`, `12_PROJECT_CONTROL/DECISION_REGISTER.md`,
  `02_ARCHITECTURE/CORE_ARCHITECTURE.md`, `03_ALGORITHMS/DEM_PROCESSING.md`,
  `04_DATA/INPUT_OUTPUT_FORMATS.md`, `12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md`, and
  `docs/parallel/AGENT_HANDOFF_TEMPLATE.md`.
- Commands repeated/used: `git status --short --branch`, `git rev-parse HEAD`,
  `git diff --check eab8396dc358ccf888b5ade00e5a76553c1fc602..HEAD`,
  `python -V`, Python import/version probe for GIS modules and SQLite, document `cat`/`rg` checks.
- Host limits: Linux x86_64, CPython 3.12.14; Rasterio, GDAL bindings, pyproj, Shapely, Pyogrio,
  and PySide6 unavailable. Consequently no GIS runtime or algorithm execution evidence is available;
  Windows remains **NOT VERIFIED**. Core CI, even if passing, does not change this status.
