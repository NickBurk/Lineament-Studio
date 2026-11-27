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
