# Workstream ownership

| Agent | Responsibility | Writable scope after a task is authorized |
|---|---|---|
| Agent01 | Architecture, Core contracts, integration and QA coordination | Shared `src/lineament_core/` contract modules, `tests/test_*.py`, shared `tests/fixtures/`, `tests/integration/`, `scripts/`, CI, package configuration, locks, architecture, project control and governance docs |
| Agent02 | Data Engine and Project Storage | `src/lineament_core/infrastructure/data/`, `tests/data/`, `04_DATA/`, task docs under `docs/data/` |
| Agent03 | GIS and Scientific Computing | `src/lineament_core/infrastructure/gis/`, `src/lineament_core/science/`, `tests/gis/`, `tests/science/`, `03_ALGORITHMS/`, task docs under `docs/science/` |
| Agent04 | Desktop UI and UX | `src/lineament_desktop/`, `tests/desktop/`, `05_INTERFACE/`, task docs under `docs/desktop/` |

These paths reserve ownership. Each authorized task specifies its phase and writable files. Agent01 owns the shared contracts and cross-workstream changes, including root `pyproject.toml`, all shared lockfiles, `.github/`, `AGENTS.md` and integration tests. Internal adapter contracts belong to the implementation owner. A contract consumed by another workstream belongs to Agent01. Proposed new paths and changes affecting another owner go through a request before editing. Agents 02–04 identify needed dependencies, versions, platform and licence implications in the handoff. Agent01 updates shared metadata and locks.

Use Master Specification and the accepted decisions in the new repository as the requirements baseline. Read AGENTS.md and receive all 11 Skills by explicit path with every handoff. Report the files actually read. OQ-19 tracks verification of automatic discovery. [Handoff template](AGENT_HANDOFF_TEMPLATE.md)

Assignment, execution and shared base publication require the project owner's go-ahead after review of Phase 1. [Integration workflow](INTEGRATION_WORKFLOW.md)
