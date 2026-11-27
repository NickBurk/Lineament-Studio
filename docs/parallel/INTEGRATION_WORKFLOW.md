# Integration workflow

## Baselines and branches

Phase 1 starts at PR #1 HEAD `805c17ffebb94e6e69ac43c18bb376e0348b68e8`. Its branch is `feature/phase-01-core-contracts`. The stacked PR targets `bootstrap/repository-foundation`.

The [Phase 1 report](../PHASE_1_REPORT.md) pins the common Phase 1 commit for future parallel tasks. After review and authorization, Agent01 publishes a common integration ref containing that commit and communicates one exact base SHA to all three agents. If the owner chooses integration by squash or rebase, publish and confirm the resulting SHA before any agent branches. Never substitute a moving branch tip for the agreed commit.

Each agent creates one branch per authorized task from the communicated SHA, using `feature/agent02-<task>`, `feature/agent03-<task>` or `feature/agent04-<task>`. Each PR names the authorized integration base. Agent01 coordinates integration. The project owner authorizes each merge. `main` advances through reviewed PRs.

## Pull requests and checks

- State the base SHA, author, owned scope, requirement and request IDs, contract versions used, changed files, exact commands, test results, CI artifact links, known risks and remaining tasks. Include scientific fixtures, benchmark evidence, migration notes or UX evidence when the change affects those areas.
- Require Core CI on Windows and Linux CPython 3.11, isolated wheel checks, lint and tests, workstream-specific checks and contract compatibility fixtures. Include negative and recovery cases when applicable. The CI workflow retains JUnit artifacts on both platforms. Record required check status for the exact proposed head before merge.
- Agent01 reviews path ownership, changes to dependencies, and contract compatibility. After each authorized integration, rerun the common suite and cross-workstream scenarios affected by the merge. Cross-module integration tests live under `tests/integration/` with shared fixtures maintained by Agent01. Add real adapters and test data only when their phases are authorized.

## Conflicts and integration order

Integrate approved contract changes before consumers. Agent01 identifies the shared base and gives the owners a new SHA and dependency order. Each agent refreshes its own branch and resolves conflicts within its assigned paths. Raise a request if the resolution changes public behavior, shared dependencies or files owned by another agent. Agent01 coordinates a separate shared change when needed and coordinates re-verification after the conflict is resolved. If changes cannot be reconciled under the agreed contract, pause the affected PR for owner review.

Phase 2 requires the OQ-25–28 review and the P1 durable recovery gate. [Phase 2 gate](../architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) · [Git workflow](../../11_DEVELOPMENT/GIT_WORKFLOW.md)
