# Core API and Worker Contracts

Phase 1 candidate for PR review. The distribution is `lineament-core 0.1.0` for CPython 3.11. It uses the standard library at runtime. The Python import root is `lineament_core`. [Phase 1 plan](../docs/PHASE_1_CORE_CONTRACTS_PLAN.md) · [ADR-0002](../docs/architecture/adr/ADR-0002-IPC-AND-JOB-LIFECYCLE.md)

## Domain and application

- `domain.ProjectRef` and `domain.SourceAssetRef` wrap non-nil UUIDs. Input keys identify slots declared by an algorithm. Adapters resolve references in their own context.
- `domain.SpatialReference` distinguishes `known`, `unknown` and `absent`. A known CRS has a definition and horizontal unit. The vertical unit is independent and may be unknown. CRS declarations are passed through without inference.
- `domain.GeometricRank` has G1/G2/G3. `domain.GeologicalOrder` carries an independently supplied expert label.
- `application.AlgorithmRegistry` is explicit and instance-scoped. Register a descriptor per exact algorithm ID and version. A duplicate pair fails. A known ID with an unavailable version has a distinct error from an unknown ID.
- `application.Algorithm` exposes a descriptor and typed `run(job, parameters, cancellation, report_progress, report_warning)` port returning a `JobResult`. Descriptors declare input slots, allowed output kinds, parameters and defaults, resource profiles and support for progress/cancel. A scientific adapter supplies its CRS, units, numeric behavior, requirements and fixture specification through the descriptor.
- `Job` takes an independent recursive snapshot of its JSON object parameters at construction. Nested objects become read-only mappings and arrays become tuples; source dictionaries and lists cannot change the job. Invalid JSON values, non-string object keys, cycles, non-finite numbers and nesting deeper than 64 levels are rejected. The snapshot is independent of project persistence.
- `registry.validate(job)` requires every declared input slot and rejects extra slots, unknown parameters and resource profiles. It returns a read-only mapping of normalized values with scalar defaults. Nested values are the immutable job snapshot, with no mutable reference exposed to callers. Parameter types are boolean, integer, number, string, array and object. A boolean is distinct from an integer. Complex parameter structure and scientific ranges are validated by the algorithm adapter.
- `JobResult` accepts a list or tuple of `ArtifactRef` values, snapshots it as a tuple, and rejects other collections, invalid members and duplicate artifact UUIDs. `registry.validate_result(job, result)` verifies job ID, algorithm version and allowed artifact kinds. The result carries its independent schema version. Artifact references may carry declared spatial information.
- `diagnostics.ContractError.code` is a stable `ErrorCode`. Warnings use `WarningCode`; clients can map codes to localized text. `explanation(code)` returns a fixed English message. Receiver errors omit raw input and exception text.

```python
from uuid import UUID

from lineament_core.application import (
    AlgorithmDescriptor, AlgorithmRegistry, Job, Parameter, ParameterType,
)
from lineament_core.domain import AlgorithmRef, ProjectRef, SourceAssetRef

operation = AlgorithmRef("example.summary", "1.0.0")
job = Job(
    UUID("11111111-1111-4111-8111-111111111111"),
    ProjectRef(UUID("22222222-2222-4222-8222-222222222222")),
    operation,
    {"source": SourceAssetRef(UUID("33333333-3333-4333-8333-333333333333"))},
    {"title": "Рельеф"},
    "standard",
)
registry = AlgorithmRegistry()
registry.register(AlgorithmDescriptor(
    operation, frozenset({"source"}), frozenset({"summary"}),
    {"title": Parameter(ParameterType.STRING), "tiles": Parameter(ParameterType.INTEGER, 1)},
))
assert registry.validate(job) == {"title": "Рельеф", "tiles": 1}
```

For nested parameters, `job.parameters["options"]["cuts"]` is a tuple and the
enclosing `options` mapping is read-only. `registry.validate(job)` preserves those
immutable values. At `encode_command`, recursive conversion restores JSON objects
and arrays; decoding creates a new independent snapshot. The wire shape and version
are unchanged.

## JSON/JSONL framing and commands

Use raw binary pipes. Each record is one UTF-8 JSON object terminated by LF. A reader also accepts CRLF. Maximum size is 65,536 bytes including delimiter. `wire.read_frame` returns `None` on clean EOF and limits the read to 65,537 bytes. Discard the stream after an oversized or unterminated record. The codec rejects duplicate keys, invalid UTF-8, non-finite numbers, unpaired surrogates and nesting beyond 64 levels. Identifiers on the wire use canonical lowercase UUIDs.

One trusted child per active job. Invoke by argv with shell disabled. A separate preflight invocation returns a `hello` record. The worker-side probe is exercised by a fixture in Phase 1. A client uses `decode_version_offer` and `negotiate_version` before launching a job. A preflight launch error or invalid offer blocks the job.

```json
{"type":"hello","supported_versions":["1.0"]}
```

Send one `job` followed by zero or more `cancel` records for the same UUID. Keep stdin available for cancellation. The client drains stdout and stderr independently. External adapters own lifetime, timeout and termination of the child.

```json
{"type":"job","protocol_version":"1.0","job_id":"11111111-1111-4111-8111-111111111111","project_id":"22222222-2222-4222-8222-222222222222","operation":"example.summary","algorithm_version":"1.0.0","inputs":{"source":"33333333-3333-4333-8333-333333333333"},"parameters":{"title":"Рельеф"},"resource_profile":"standard"}
{"type":"cancel","protocol_version":"1.0","job_id":"11111111-1111-4111-8111-111111111111"}
```

Use `encode_command` and `decode_command` for these records. Every command field shown is required for its type. Paths, storage format and destination policy belong to later adapters. The contrast with the Phase 0 illustrative path-based job is recorded for review. [Contract change requests](../docs/parallel/CONTRACT_CHANGE_REQUESTS.md)

## Progress, lifecycle and results

Each stdout event has `type`, `protocol_version`, `job_id`, `sequence` and `timestamp`. Sequence starts at 1 and increases by 1. The timestamp is UTC with `Z` and up to six fractional digits. Sequence determines ordering even if the wall clock shifts. Events are serialized with `encode_event` and parsed with `decode_event`.

| Event | Additional field | Semantics |
|---|---|---|
| `started` | — | First event after accepting and validating the job |
| `stage_started`, `stage_completed` | `stage` | One active stage at a time. Stage ID is a lowercase ASCII token matching `[a-z][a-z0-9_.-]{0,63}` |
| `progress` | `percent` | Job-wide integer 0 to 100, nondecreasing. Absence means indeterminate progress |
| `warning` | `warning_code` | Known warning code while the job is active |
| `cancel_requested` | — | First accepted cancel, while running |
| `commit_started` | — | Finalization boundary after the active stage closes |
| `artifact_created` | `artifact` | Artifact announcement in finalization. The matching reference must be in a successful result |
| `cancelled` | — | Cooperative stop at a safe boundary after acknowledgement |
| `failed` | `error_code` | Terminal failure of an accepted job. Stable diagnostic code |
| `completed` | `result` | Terminal success after finalization. The result uses the same job ID and algorithm version |

A `CancellationToken` is a thread-safe cooperative signal inside the worker. Serialize state transitions in the job owner and call `JobLifecycle.can_acknowledge_cancel` before emitting an acknowledgement. Repeated requests are idempotent. A cancel acknowledged before finalization prevents `commit_started`. A request after `commit_started` leaves finalization in control. An error may end active execution, cancellation or finalization. An accepted job can produce exactly one terminal event. On shutdown the future client may request cancel, drain streams and wait for a terminal event and process exit. Forced termination after a deadline is a transport failure and may require recovery.

```json
{"type":"completed","protocol_version":"1.0","job_id":"11111111-1111-4111-8111-111111111111","sequence":8,"timestamp":"2026-11-27T06:00:00Z","result":{"result_version":"1.0","job_id":"11111111-1111-4111-8111-111111111111","operation":"example.summary","algorithm_version":"1.0.0","artifacts":[{"id":"44444444-4444-4444-8444-444444444444","kind":"summary","spatial":{"status":"known","crs":"EPSG:4326","horizontal_unit":"degree","vertical_unit":null}}]}}
```

An artifact requires `id` and `kind`. If `spatial` is supplied, all four spatial keys are present, with nullable definition and units subject to domain rules. `artifacts` may be empty. Warnings and errors carry codes only. A client can display the catalog message and use the job ID and sequence for diagnostics. Stderr is reserved for diagnostics outside this contract. Adapters must avoid transmitting secrets or logging command payloads and raw stderr indiscriminately.

Pass each record to `JobLifecycle.accept_frame`. On EOF call `finish(process_return_code)` only after the observed process exits and stdout is drained. The result is available after consistent termination. Malformed events, a wrong job ID or sequence, a second terminal event, premature EOF and a mismatched exit are transport failures. If the bounded reader itself rejects the stream, discard that replay. The in-memory state describes observed events. The Phase 2 recovery gate governs durable publication and retry. [Phase 2 gate](../docs/architecture/adr/ADR-0003-PROJECT-DATA-OWNERSHIP.md)

| Exit | Meaning |
|---|---|
| 0 | Completed with matching terminal event. Also successful preflight with a `hello` |
| 1 | Failed with matching terminal event |
| 2 | Request rejected before job acceptance, or invalid control. No successful result |
| 3 | Cancelled with matching terminal event |
| Other | Transport failure |

For retry use a new UUID. Cross-process duplicate protection and durable recovery remain open in OQ-24/26. [Complete successful replay](../tests/fixtures/completed.jsonl)

## Compatibility

| Version | Rule |
|---|---|
| Package `0.1.0` | Distribution version is independent of the protocol |
| Protocol `1.0` | Choose highest exact shared version during preflight. Both sides can advertise older versions. Same-major unadvertised versions and different-major versions are rejected before work |
| Result schema `1.0` | Validate independently of the envelope. Only 1.0 is supported |
| Algorithm `X.Y.Z` | Registry requires exact registered version. Math changes require a version change and scientific regression evidence |

Unknown fields, message types and codes are rejected within 1.0. Compatible future extensions require opt-in via a new advertised minor version, alongside fixtures for both versions. Breaking changes use a new major version. Project, persistence and GIS runtime versions have independent review gates.
