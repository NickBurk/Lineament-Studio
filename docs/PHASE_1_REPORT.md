# Phase 1 — Core Contracts and Domain Model

Phase 1 produces a storage-neutral CPython 3.11 Core and a four-agent integration charter. See the
[contract](../02_ARCHITECTURE/API_CONTRACTS.md), [planned acceptance checks](PHASE_1_CORE_CONTRACTS_PLAN.md)
and [integration workflow](parallel/INTEGRATION_WORKFLOW.md). The review record below is updated with
the exact candidate SHA and observed CI results.

The branch starts at PR #1 HEAD `805c17ffebb94e6e69ac43c18bb376e0348b68e8`. The minimal toolchain
commit `457ad39` precedes Domain and Wire. It was built and installed into an isolated CPython 3.11.18
environment on Linux before contract implementation. The initial import ran outside the checkout.

## Manual Skills

Read `AGENTS.md`, `MASTER_TZ.md` and these 11 explicit `SKILL.md` paths from the Phase 0 base.

- `.agents/skills/requirements-engineer/SKILL.md`
- `.agents/skills/software-architect/SKILL.md`
- `.agents/skills/data-architecture-engineer/SKILL.md`
- `.agents/skills/qa-test-engineer/SKILL.md`
- `.agents/skills/python-desktop-developer/SKILL.md`
- `.agents/skills/code-reviewer/SKILL.md`
- `.agents/skills/gis-geospatial-engineer/SKILL.md`
- `.agents/skills/scientific-computing-engineer/SKILL.md`
- `.agents/skills/geomorphology-structural-geology-expert/SKILL.md`
- `.agents/skills/ui-ux-designer/SKILL.md`
- `.agents/skills/release-engineer/SKILL.md`

Manual handoff is the authorized workaround. OQ-19 remains open for automatic discovery in Codex Web.

## Scope and review conditions

Phase 1 is compatible with the accepted Phase 0 architecture. It preserves Core independence,
uses explicit versioned JSON/JSONL over separate-process boundaries and keeps geometric rank
separate from expert classification. ADR-0002 and the initial wire choices are presented for
review in CCR-001/002. Traceability lists each of the 62 FR and 16 NFR IDs separately and
distinguishes contract evidence from product acceptance.

Tests exercise a test-only subprocess. Production Worker process ownership, GUI cancel/close
policies, persistent deduplication and cross-process result recovery remain future integrations.
Phase 1 covers in-memory replay, reference and result validation, framing, cancellation and version
selection. Scientific ranges and validations are owned by the future algorithm adapters.

OQ-25–28 remain unresolved and ADR-0003 is Proposed. Before Phase 2, the owner must accept a
durable PREPARED intent before manifest replacement, recovery ordering with a state machine and
fault-injection coverage at each persistence boundary. OQ-24 still covers cross-process deduplication.
OQ-30 retains the product scope and preprocessing priority conflict. No GIS, Qt or storage runtime
is required by the Core wheel. [Open questions](../12_PROJECT_CONTROL/OPEN_QUESTIONS.md) · [Change requests](parallel/CONTRACT_CHANGE_REQUESTS.md)

## Integration base

The common candidate for future parallel tasks is
`9b61abc99e6105325a67533905ca7a790aab7a4f` on `feature/phase-01-core-contracts`.
It contains the complete Core, the test suite and the workstream charter. Later report-only
commits record verification. Develop future work from that exact commit after the project owner
authorizes the common base and assignments. Integration through a history-rewriting merge mode
requires Agent01 to record the replacement SHA before any workstreams branch.
[Phase 1 review](https://github.com/NickBurk/Lineament-Studio/pull/2)

## Local verification

Linux x86_64, CPython 3.11.18 and uv 0.13.9. The initial skeleton build and isolated wheel install
passed before contract source files were added. The full wheel passed a second clean install
and import of all five Core modules. Its package metadata declared zero runtime requirements.
Hatchling is used at build time. Ruff and pytest are development tools. Versions and hashes
are recorded in `uv.lock`.

```sh
uv python install 3.11
uv lock --python 3.11
uv sync --locked --python 3.11
uv build --wheel --no-build-isolation
uv run --locked python scripts/check_wheel.py
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked pytest -ra --junitxml=core-junit.xml
git diff --check 805c17f...HEAD
```

The local JUnit was written to the workspace scratch directory. The final local run reported
47 passed, 0 failed, 0 skipped. Ruff lint and format passed. A repository check confirmed
all 62 FR and 16 NFR traceability rows, catalogue priorities, and 61 resolvable relative
links in the changed Markdown files before adding this evidence section.

| Acceptance check | Actual evidence |
|---|---|
| AC-CORE-001 | Wheel installed offline into an isolated venv and imported outside the checkout |
| AC-CORE-002 | UUID references, bounded UTF-8 JSONL and golden replay. Invalid UTF-8, repeated keys, missing sequences and wrong IDs are rejected |
| AC-CORE-003 | Separate subprocess preflight and exact version selection. Unknown fields, unadvertised minor and different major versions are rejected |
| AC-CORE-004 | Cancel twice, cancel vs. finalization, exit mismatch, subprocess crash, restart and 256 KiB stderr burst. Persistent recovery has its Phase 2 gate |
| AC-CORE-005 | Exact operation versions, duplicate/unknown entries, validated defaults, invalid parameters and result kinds |
| AC-CORE-006 | Unicode wire fixtures, fixed diagnostic messages and rejection of free-form diagnostic fields |

## Changed files

| Area | Files relative to repository root |
|---|---|
| Toolchain and CI | `.github/workflows/core.yml`, `.gitignore`, `pyproject.toml`, `uv.lock`, `scripts/check_wheel.py` |
| Core package | `src/lineament_core/__init__.py`, `src/lineament_core/application.py`, `src/lineament_core/diagnostics.py`, `src/lineament_core/domain.py`, `src/lineament_core/lifecycle.py`, `src/lineament_core/wire.py` |
| Tests and fixtures | `tests/conftest.py`, `tests/test_domain_application.py`, `tests/test_wire_lifecycle.py`, `tests/test_worker_exchange.py`, `tests/fixtures/job.jsonl`, `tests/fixtures/completed.jsonl`, `tests/fixtures/worker_probe.py` |
| Architecture and Phase 1 | `02_ARCHITECTURE/API_CONTRACTS.md`, `docs/PHASE_1_CORE_CONTRACTS_PLAN.md`, `docs/PHASE_1_REPORT.md`, `docs/REPOSITORY_STRUCTURE.md`, `docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md`, `docs/architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md` |
| Project control | `12_PROJECT_CONTROL/OPEN_QUESTIONS.md`, `12_PROJECT_CONTROL/REQUIREMENTS_TRACEABILITY.md` |
| Four workstreams | `docs/parallel/WORKSTREAM_OWNERSHIP.md`, `docs/parallel/CONTRACT_CHANGE_PROCESS.md`, `docs/parallel/CONTRACT_CHANGE_REQUESTS.md`, `docs/parallel/INTEGRATION_WORKFLOW.md`, `docs/parallel/AGENT_HANDOFF_TEMPLATE.md` |

## GitHub Actions evidence

Core CI built the wheel, installed it in a clean environment without package-index access, passed
Ruff and executed all 47 tests on each platform for the pinned common candidate.
[Core CI run 45938866568](https://github.com/NickBurk/Lineament-Studio/actions/runs/45938866568)

| Runner | CPython | Observed tests | Retained evidence |
|---|---|---|---|
| Ubuntu | 3.11.18 | 47 passed in 0.47 s | [JUnit](https://github.com/NickBurk/Lineament-Studio/actions/runs/45938866568/artifacts/15171697772) |
| Windows | 3.11.9 | 47 passed in 0.65 s | [JUnit](https://github.com/NickBurk/Lineament-Studio/actions/runs/45938866568/artifacts/15172245635) |

The first Windows run hit the 32,767-character Windows environment variable limit when pytest
included the 64 KiB payload in `PYTEST_CURRENT_TEST`. The corrected test uses a short case ID and
retains the same payload and assertions. Both environments passed on the next run.
[First run and failure evidence](https://github.com/NickBurk/Lineament-Studio/actions/runs/45938769481)

## LS-1-01 snapshot integrity correction

The initial `Job.parameters` constructor copied only the outer dictionary. Nested dictionaries
and lists still pointed to caller-owned mutable objects. `AlgorithmRegistry.validate()` returned
a mutable dictionary containing those values. `JobResult.artifacts` accepted an unvalidated
collection, so a caller could alter a result through its original list.

The correction recursively copies JSON parameters into read-only mappings and tuples, rejecting
invalid scalars, non-string keys, cycles and nesting beyond 64 levels. Registry validation returns
a read-only mapping over the immutable job values. `JobResult` validates artifact types and unique
IDs and snapshots list or tuple input as a tuple. The command encoder converts the internal values
back to JSON objects and arrays. The wire schema, API version, ADRs and runtime dependencies are
unchanged.

New regression tests in `test_domain_application.py` cover nested source mutation, direct nested
mutation attempts, invalid JSON numbers and types, cycles, depth, registry stability and descriptor
isolation, and result collection normalization and validation. A test in `test_wire_lifecycle.py`
covers nested Unicode command round-trip, JSON container types and decoded snapshot independence.
The original 47 tests and 18 new tests passed locally on CPython 3.11.18 (65 passed, 0 failed,
0 skipped, 0.30 s). `uv sync --locked --python 3.11`, wheel build, clean wheel install and import,
Ruff lint, Ruff format check and `git diff --check` passed. `uv` used the workspace cache because
the default home cache is read-only in this execution environment.

The correction commit is `a278516dcc316ca2fd29ada5ba1e684325559c89`.
[Core CI run 45943712233](https://github.com/NickBurk/Lineament-Studio/actions/runs/45943712233)
completed successfully on that commit. The Ubuntu and Windows CPython 3.11 jobs both completed
wheel build and clean install, lint, formatting and contract tests, with retained
[Ubuntu JUnit](https://github.com/NickBurk/Lineament-Studio/actions/runs/45943712233/artifacts/15173672208)
and [Windows JUnit](https://github.com/NickBurk/Lineament-Studio/actions/runs/45943712233/artifacts/15174315157).
The previous CI run above verifies the original Phase 1 candidate only and is not evidence for
LS-1-01. The documentation evidence commit after `a278516` also requires new-head CI before
independent review.
