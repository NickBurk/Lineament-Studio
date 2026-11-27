# CHAT02 — Preliminary Integration Review (Stage A)

Status: **PRELIMINARY REVIEW COMPLETE — AWAITING WORKSTREAM RESULTS**. This is not the final integration verdict. Snapshot reviewed on 2026-11-27. Phase 2/3 implementation and merges remain blocked.

## 1. Git state and baseline verification

- Review branch: `feature/agent01-chat02-integration-review`, created in a clean separate worktree from exact `eab8396dc358ccf888b5ade00e5a76553c1fc602`.
- PR base: `integration/phase-1-baseline`; fetched remote ref resolves to the same SHA.
- Graph: `57e7cc7` master specification → `805c17f` repository foundation → `eb02478` Phase 1 merge (with LS-1-01/02 in its ancestry) → `eab8396` integration baseline. PR #3 (`904b376`) and PR #4 (`262795a`) are independent one-commit children of `eab8396`, not merged into this review branch.
- The earlier local checkout at `a8da025` was not used as the review base. No history was reset or rewritten.

## 2. Evidence and workstream state

| Workstream | Observed source and scope | Preliminary status | Evidence still required |
|---|---|---|---|
| Agent02, [PR #4](https://github.com/NickBurk/Lineament-Studio/pull/4) | `262795a0f7eee2878176b0d8130ed72b5ef02651`; two new `docs/data/` files, 257 additions, no shared contract/ADR/OQ edits. Proposal covers SQLite PREPARED, recovery and 32 planned fault cases. | **PENDING / REQUEST CHANGES** per [CHAT01 comment](https://github.com/NickBurk/Lineament-Studio/pull/4#issuecomment-7211950405). | Revised head addressing six comments; actual Windows durability/fault evidence later, after approved design. Current PR has no executable test evidence. |
| Agent03, [Issue #5](https://github.com/NickBurk/Lineament-Studio/issues/5) | Exact baseline assigned; no Agent03 PR found in repository PR search at this snapshot. | **PENDING** | PR and two science reports; Windows runtime/ABI, DLL/data isolation and scientific fixture evidence, with unverified items explicit. |
| Agent04, [PR #3](https://github.com/NickBurk/Lineament-Studio/pull/3) | `904b3765c79a8206f2584701cfb27696270666e6`; three new `docs/desktop/` files, 278 additions, no shared contract/ADR/OQ edits. | **PENDING** after [CHAT01 comment](https://github.com/NickBurk/Lineament-Studio/pull/3#pullrequestreview-6084545255): architectural ACCEPT was a comment, not merge approval. | Revised head for Undo, remove wording, benchmark samples, CSS/Qt pixels and project CRS. No application tests were claimed. |

Both PRs report document checks, but the current PR #3 diff has Markdown hard-break trailing spaces, so `git diff --check eab8396..904b376` reports four whitespace findings. This is a formatting gate, not an architectural rejection. PR #4's diff check returned clean. Push and proposed-merge CI must be checked on revised heads in Stage B; old CI cannot close the final gate.

## 3. Cross-workstream compatibility matrix (preliminary)

| Boundary | Current shared requirement | Preliminary dependency / risk | Final evidence |
|---|---|---|---|
| Storage ↔ Desktop | `project.lspx` entry point, SQLite catalog, user-selected Reference/Copy; missing source remains visible; relink requires explicit choice. | Desktop's reopen, remove-from-project and checksum-mismatch flow needs a defined Storage operation and publication state. UI must not imply physical deletion of DEM or a successful write before durable catalog publication. | Source identity, Copy/Reference, relink mismatch, missing DEM, reopen, remove and active-task scenarios against approved storage contract. |
| Storage ↔ Core | Core owns versioned `job_id`, algorithm/result refs and JSON/JSONL lifecycle. API Contracts say retry uses a new UUID. | PR #4 introduces storage `operation_id` and possible idempotency key/receipt. Mapping to `job_id`, cancellation, terminal event and recovery is unresolved (C02). | Contract review and positive/negative replay cases; no Core API or wire edit without approved CCR. |
| GIS ↔ Storage | DEM preflight must preserve CRS, transform, NoData, units and source bytes; catalog records metadata/checksum. | Runtime ownership and validation boundary are pending Agent03. PR #4 stages GeoTIFF/GPKG and records metadata but Windows driver/durability checks are plans. | Real synthetic GeoTIFF/GPKG reopen, metadata/digest and Reference-path cases under selected Windows runtime. |
| GIS ↔ Desktop | Map Canvas uses windowed raster reads and explicit view CRS; unknown/missing CRS cannot be guessed. | PR #3 proposes viewport, cache, overlay and p95 thresholds. No GIS adapter or representative Windows benchmark exists. Treat thresholds as proposed only. | Prototype measures cold/warm/reopen latency, UI/Worker RSS, handles, CRS rendering and large rasters. |

## 4. ADR, OQ and contract conflicts

ADR-0001 is Accepted as an architect-selected baseline. ADR-0002, ADR-0003 and ADR-0004 remain Proposed. OQ-23/25/26/28 are Proposed; OQ-24/27/01/03/29/31 are Open. No status is changed by this review.

| ID | Sources and requirements | Decision options / compatibility and risk | Acceptance checks and decision owner |
|---|---|---|---|
| C01 | PR #4 storage proposal §3.3 vs ADR-0003 P1 gate and OQ-26; PROJ-001–008, NFR-DATA-001/002, NFR-REL-002. | Specify one SQLite journal/synchronous profile and durability boundary; WAL+FULL versus rollback DELETE+EXTRA need distinct evidence. SQLite-only intent versus sidecar remains an owner choice. Wrong claim risks unobservable manifest/catalog divergence after power loss. | Positive: durable PREPARED precedes replacement and reopen converges after each fault. Negative: corrupt/missing SQLite at three stages fails closed without false publication. Owner: project owner after Data/QA/Architecture review. |
| C02 | PR #4 §3.2–3.3 idempotency receipt vs API Contracts Compatibility/retry and ADR-0002/OQ-24; NFR-REL-002. | Distinguish Worker `job_id` (new UUID on retry), storage operation ID and optional deduplication key. Do not redefine retry via storage document. Compatibility or migration requires CCR if public behavior changes. | Positive: repeated same storage request yields one result; new Worker retry UUID remains valid. Negative: same key/different payload conflicts; cancelled/failed job cannot be reported completed. Owner: project owner with Core/Data. |
| C03 | PR #4 §2.1 vs DATA_MODEL System of record, PROJECT_STORAGE §3–5 and ADR-0003/OQ-25; PROJ-003/004/008. | Define field ownership for source declaration, SQLite projection and derived asset separately. Manifest authority versus SQLite authority affects schema migration and recovery. | Positive: stale projection rebuild preserves source identity; negative: contradictory project ID/digest blocks writes. Owner: project owner with Data Architecture. |
| C04 | PR #4 §3–5 vs PROJECT_STORAGE §4–5 and OQ-27; PROJ-003/004/006/007/008. | Checksum optionality, relative Reference URI, schema versions and unknown fields need explicit owner choice; stricter rules may reject existing project fixtures. | Positive: Reference/Copy, Unicode, relink and supported versions round-trip. Negative: traversal, unsupported version and drift fail safely. Owner: project owner with Data/QA. |
| C05 | PR #3 blueprint §4, ACCESSIBILITY matrix and CHAT01 comment vs OQ-01/29, UI-001–004. | Benchmark sample count and CSS px vs Qt logical px require clarification. Proposed thresholds must not become NFR silently. Undo scope and remove wording need edits. | Positive: repeated cold/warm/reopen measures and accessible target checks; negative: missing layer or failed relink does not erase data or selection. Owner: Desktop/QA; product threshold approval by owner. |

Proposed CCRs: C01–C04 should be entered as Architecture/Contract Change Requests by Agent01 after revised PR #4 is available, with source passages, version/migration impact and affected owners. No shared contract change is proposed for C05 unless Desktop requires new Core/Storage fields. These IDs are review tracking IDs, not approved decisions.

## 5. Integration dependency graph and criteria

Recommended sequence: Storage Architecture → GIS Runtime Gate → Desktop UX → cross-workstream verification. Storage defines asset identity, publication and reopen rules consumed by GIS and Desktop; GIS determines preflight and viewport capabilities consumed by Desktop. Parallel documentation review may continue, but implementation waits for owner decisions.

Before any merge: revised heads must retain exact baseline ancestry and owned paths, address CHAT01 findings, document actual Skills read, preserve ADR/OQ status, pass `git diff --check`, and show required push and pull-request CI on those heads. PR #4 additionally needs approved C01–C04 decisions before Phase 2 implementation; PR Agent03 needs an actual PR and explicit verified/unverified Windows and scientific evidence; PR #3 must separate proposed performance numbers from accepted NFRs. After authorized integration, run affected cross-workstream scenarios and publish the actual resulting SHA before downstream branches.

## 6. Stage B gate and owner decisions

Stage B requires a separate chief-architect assignment and revised PR #4/#3 heads plus Agent03 PR. Recheck all diffs, comments, ownership, CI runs and artifacts, then issue separate ACCEPT/REQUEST CHANGES/BLOCKED verdicts. The owner must decide storage durability profile and journal carrier, identity/retry semantics, manifest field ownership/schema/paths, GIS runtime, and any product benchmark thresholds. No PR is approved for merge by this preliminary report.

## 7. Review method and limits

Read `AGENTS.md`, master specification, AI agent instructions, skill routing, handoff, ownership, workflow, contract process, API Contracts, data/storage/metadata, DEM and UI specifications, ADR-0001–0004, Decision Register, Open Questions and traceability. Read all 11 explicit `.agents/skills/*/SKILL.md` paths listed in `AGENT_HANDOFF_TEMPLATE.md`. Compared Git refs/diffs and published CHAT01 PR comments. No production tests, Windows runtime tests or fault-injection were run for this documentation review; their absence is an integration gate, not a pass.
