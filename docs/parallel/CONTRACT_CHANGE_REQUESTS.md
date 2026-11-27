# Architecture and Contract Change Requests

These requests are submitted with Phase 1 for owner review.

| ID | Finding | Candidate and review required |
|---|---|---|
| CCR-001 | The Phase 0 job example used path-shaped inputs and an output directory. The Phase 1 brief requires neutral domain references and reserves path policy for Phase 2. | In Phase 1 Job 1.0 use UUID references per input slot and return artifact UUIDs. Keep file resolution and destination policy within OQ-25–27. Review the wire representation with Agent01 and the project owner. |
| CCR-002 | The Phase 0 event list does not expose the finalization boundary needed to replay cancel vs. commit, or a sequence to detect missing/reordered events. | Add `commit_started` and per-job `sequence` to the initial protocol, with explicit replay cases. Review event ordering and exact version negotiation under OQ-21–24. |
| ACR-003 (P1, Phase 2 gate) | PR #1 identified a crash gap if the manifest is replaced before a durable PREPARED intent: a new manifest and old projection can survive without a recovery record. | Require durability of PREPARED before manifest replacement, and agree on state machine, recovery ordering and fault-injection evidence before Phase 2 implementation. The journal medium, lock and schema remain open. |
| ACR-004 | FR PRE-002 assigns multidirectional hillshade P1 while DEM Processing calls it P0. The material also lists slope in different priority contexts. | Product/Requirements to reconcile the sources in OQ-30 before Phase 3. Traceability uses the FR catalogue to display priorities and records the discrepancy. |

The candidate wire choices are implemented for review and do not approve storage design. [Contract change procedure](CONTRACT_CHANGE_PROCESS.md) · [ADR-0002](../architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md) · [ADR-0003](../architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md) · [Open Questions](../../12_PROJECT_CONTROL/OPEN_QUESTIONS.md)
