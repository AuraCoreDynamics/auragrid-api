# AuraGrid & AuraSprout Loopback IPC Protocol

## Overview

Every Managed Application Service (MAS) launched by **AuraGrid** (`AuraGrid.ProxyWorker`) or **AuraSprout** (`SproutSupervisor`) communicates with its local host node over a loopback HTTP IPC bridge (`127.0.0.1` ephemeral port).

Canonical wire contracts are defined in [`../openapi/ipc-bridge.openapi.json`](../openapi/ipc-bridge.openapi.json) and [`../schemas/lease-collaboration.schema.json`](../schemas/lease-collaboration.schema.json).

---

## Authentication & Environment Bootstrap

1. **Token Delivery**:
   - **StdIn Injection (preferred)**: Host sets `AURAGRID_IPC_STDIN_ENABLED=true` and writes the single-use/per-MAS IPC secret token followed by newline to the child's stdin. Empty stdin tokens MUST fall back cleanly to environment or unauthenticated local emulation only when explicitly enabled.
   - **Header**: Clients send `X-AuraGrid-Ipc-Token: <token>` on every `/cell/*` request.
2. **Bridge Coordinates**:
   - `AURAGRID_IPC_PORT` / `AURAGRID_LOCAL_URL`: Loopback base URL (e.g., `http://127.0.0.1:<port>`).
   - `AURAGRID_MAS_ID`: Assigned MAS identifier.
   - `AURAGRID_NODE_ID`: Node identifier injected by the host.

---

## MAS Placement Modes (`services[].mode`)

`app.manifest.schema.json` defines three canonical placement modes shared across both AuraGrid and AuraSprout:

1. **`LocalOnly`**: Node-managed service lifecycle (`mvenv`, health checks, restart policy, local `/cell/*` IPC access) that is **unmanaged at the grid/cell level** (acquires no cell lease, publishes no external service endpoints, and writes zero `.sprout/nodes/` presence heartbeats).
2. **`CellSingleton`**: Cell-wide exclusive 1-of-N singleton protected by a cell lease and monotonic `fencingToken`.
3. **`Distributed`**: All-of-N multi-node workload running simultaneously across participating nodes (with optional micro-batch coordination via `/cell/collaboration/batches/*`).

---

## Endpoint Groups

### Health & Readiness
- `GET /health`
- `GET /api/health`
- `GET /ready`

### Cell Configuration
- `GET /cell/config` -> `{"config": {...}, "metadata": {...}}`
- `GET /cell/config/_metadata` -> `CellConfigMetadata`
- `GET /cell/config/{key}` -> `{"value": ...}` or `404`
- `PUT /cell/config/{key}` -> `{"value": ...}` -> `204`
- `DELETE /cell/config/{key}` -> `{"removed": true}` or `404`

### Cell Membership
- `GET /cell/local-node` -> `CellMember`
- `GET /cell/members?includeUnhealthy=false` -> `[CellMember, ...]` or `{"members": [...]}`
- `GET /cell/members/_healthy-count` -> `{"count": <int>}`
- `GET /cell/members/_metadata` -> `CellMembershipMetadata`
- `GET /cell/members/{nodeId}` -> `CellMember` or `404`

### Governance
- `POST /cell/governance/can-deploy` (`{"appId": ..., "userId": ...}`)
- `POST /cell/governance/can-remove` (`{"appId": ..., "userId": ...}`)
- `POST /cell/governance/can-reconfigure` (`{"resourceId": ..., "userId": ...}`)
- `GET /cell/governance/roles/{userId}` -> `{"roles": [...]}`
- `GET /cell/governance/audit?limit=100` -> `[AuditEntry, ...]`

### Eventing & WAL Markers
- `GET /cell/events/topics` -> `{"topics": [...]}`
- `GET /cell/events/topics/{topicId}/exists` -> `{"exists": <bool>}`
- `GET /cell/events/markers/{consumerId}/{topicId}` -> `WalMarker` (`sequenceNumber: null` when uncommitted)
- `PUT /cell/events/markers/{consumerId}/{topicId}` (`{"sequenceNumber": <int>}`) -> `204`
- `POST /cell/events/{topicId}` (`{"payload": "<base64>", "eventType": ...}`) -> `AuraEventDto`
- `GET /cell/events/{topicId}?afterSequence=0&count=100` -> `{"events": [AuraEventDto, ...]}`

### Leases & Collaborative Shared Processing
- `POST /cell/lease/acquire` -> `LeaseAcquisitionResult`
- `POST /cell/lease/renew` (`{"masId": ..., "fencingToken": ..., "marker": ...}`) -> `{"extended": bool, "conflict": LeaseConflictDto | null}`
- `POST /cell/lease/release` -> `204`
- `GET /cell/lease/marker/{masId}` -> `{"marker": WalMarker | null}`
- `GET /cell/lease/{masId}` -> `LeaseRecordDto | LeaseInfo` or `404` when unheld
- `GET /cell/collaboration/status/{masId}` -> `LeaseRecordDto` (`404` triggers enterprise fallback in SDK)
- `POST /cell/collaboration/volunteer` (`{"masId": ..., "enabled": bool, "user": ...}`) -> `LeaseRecordDto`
- `POST /cell/collaboration/batches/claim` -> `WorkBatchClaimDto`
- `POST /cell/collaboration/batches/{batchId}/commit` (`{"fencingToken": <int>, "checkpointMetadata": {...}}`) -> `WorkBatchClaimDto` or `409 LeaseConflictDto`
- `GET /cell/collaboration/conflicts?masId=...` -> `{"conflicts": [LeaseConflictDto, ...]}`
- `POST /cell/collaboration/conflicts/{conflictId}/resolve` (`{"action": ConflictResolutionAction}`) -> `LeaseRecordDto`

### Service Registry & Port Registration
- `GET /cell/registry/discover?serviceName=<name>` -> `{"endpoints": [ServiceEndpoint, ...]}`
- `GET/POST /cell/registry/services`
- `GET /cell/registry/services/{serviceName}`
- `POST /cell/service-port` -> `{"registered": true, "serviceName": ..., "port": ...}`

### Shared Storage & Fencing
Matches `IpcRouteConstants.cs` / `CellApiHandler.cs` / `auragrid.storage_client`:
- `GET /cell/storage/read?path=...` -> raw `application/octet-stream`
- `GET /cell/storage/range?path=...&offset=...&count=...` -> raw `application/octet-stream`
- `GET /cell/storage/exists?path=...` -> `{"exists": <bool>}`
- `GET /cell/storage/metadata?path=...` -> `{"isDirectory": bool, "size": int, "lastModified": iso8601}`
- `POST /cell/storage/write?path=...&fencingToken=...` -> raw body -> `204` (or `403` on fencing failure)
- `POST /cell/storage/append?path=...&fencingToken=...` -> raw body -> `{"length": <int>}`
- `DELETE /cell/storage/delete?path=...&recursive=false` -> `{"deleted": <bool>}`
- `GET /cell/storage/list?prefix=...` -> `{"files": [...]}` (AuraSprout extension)
