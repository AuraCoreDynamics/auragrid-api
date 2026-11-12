# Collaborative Shared Processing Specification

## 1. Opt-In Volunteering over Shared Filesystems

In **AuraSprout**, multi-user/multi-node coordination uses the exact same three placement modes as **AuraGrid** (`LocalOnly`, `CellSingleton`, `Distributed`) defined in [`../schemas/app.manifest.schema.json`](../schemas/app.manifest.schema.json). Collaboration is controlled at runtime by a per-service opt-in toggle (`volunteerEnabled`, defaulting to `false`):

- When `volunteerEnabled = false`:
  - Only `LocalOnly` services and `guiEntryPoints` execute locally.
  - No `.sprout/leases/`, `.sprout/claims/`, `.sprout/registry/`, or `.sprout/nodes/` records are created.
- When `volunteerEnabled = true`:
  - **`LocalOnly`**: Remains strictly node-local (`mvenv`, health supervision, local `/cell/*` IPC); never acquires leases or registers endpoints.
  - **`CellSingleton`**: Acquires an exclusive fenced lease under `.sprout/leases/<masId>.lease.json` coordinated via `SproutMutex` atomic directory creation (`mkdir` / `os.mkdir`). Only the holder with the active monotonic `fencingToken` may commit fenced storage writes or checkpoints.
  - **`Distributed`**: Multiple participating nodes run concurrently and atomically claim micro-batches (`WorkBatchClaimDto`) under `.sprout/claims/<masId>/<batchId>.claim.json`.

---

## 2. Fencing Tokens & Staged Batch Commits

1. Every lease acquisition or takeover increments `fencingToken` monotonically inside `.sprout/leases/<masId>.lease.json`.
2. Storage writes (`POST /cell/storage/write?fencingToken=...`) and batch commits (`POST /cell/collaboration/batches/{batchId}/commit`) MUST present a `fencingToken` equal to the active lease's token (or active claim owner).
3. Staged output is written to `.sprout/staging/<masId>/<token>/` and moved atomically into shared storage only after fencing validation passes.
4. Presenting a stale `fencingToken` fails fast with HTTP `409 Conflict` (or `403` on raw storage writes), emits a `LeaseConflictDto`, and transitions the conflicting state to `"ConflictPending"`.

---

## 3. Human-in-the-Loop Deconfliction (`LeaseConflictDto`)

When a lease renewal or batch commit detects a conflict (`stale fencing token` or divergent remote holder), `AuraSprout` surfaces a `LeaseConflictDto` via both `/cell/collaboration/conflicts` (IPC) and `/api/v1/conflicts` (Management UI/CLI) with explicit user resolutions:

- **`DiscardLocalAndSync`**: Discard staged local edits and synchronize with the remote holder's checkpoint.
- **`KeepLocalAndStageMerge`**: Move local work to `.sprout/staging/` for manual review/merge and release contested lock.
- **`TakeOverStaleLock`**: Reclaim an expired/abandoned lock with a newly incremented `fencingToken`.
- **`YieldToPeer`**: Voluntarily yield execution to the active peer without mutating shared outputs.

---

## 4. SMB-Safe Event Store

Because Windows SMB / CIFS and many network filesystems corrupt SQLite WAL (`-wal` / `-shm`) shared-memory mappings across hosts, the shared `.sprout/events/events.sqlite` store MUST configure:
- `PRAGMA journal_mode=TRUNCATE;`
- `PRAGMA synchronous=FULL;`
- `PRAGMA busy_timeout=5000;`
- All multi-writer mutations serialized by `SproutMutex`.
