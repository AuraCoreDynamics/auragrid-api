# CLAUDE.md — `auragrid-api`

## Role & Scope
`C:\projects\auracore\auragrid-api` is the **canonical contract repository** for the AuraCore ecosystem (`auragrid`, `auragrid-py`, `auraseed`, `aurasprout`).

This repository contains **ZERO runtime business logic, HTTP servers, network clients, or database code**. It holds only:
- `schemas/` — 5 canonical JSON Schema (Draft-07) contract files, mirrored in `src/auragrid_api/schemas/` (10 JSON Schemas bundled across repo and wheel package):
  - `app.manifest.schema.json`
  - `service-descriptor.schema.json`
  - `catalog.schema.json`
  - `lease-collaboration.schema.json`
  - `ops-telemetry.schema.json`
- `openapi/` — 2 OpenAPI 3.1 specifications (`ipc-bridge.openapi.json`, `aurasprout-management.openapi.json`), mirrored in `src/auragrid_api/openapi/`.
- `docs/` — Canonical wire & packaging protocol specifications.
- `fixtures/wire_vectors/` — 7 golden JSON test vector files (`app_manifest.json`, `service_descriptor.json`, `catalog_manifest.json`, `lease_collaboration_vectors.json`, `ipc_bridge_vectors.json`, `management_vectors.json`, `ops_telemetry_vectors.json`), mirrored in `src/auragrid_api/fixtures/wire_vectors/` and validated by `tests/test_schemas_and_vectors.py`.
- `src/auragrid_api/__init__.py` — Read-only path and JSON loader helpers (`get_schema_path`, `get_openapi_path`, `get_fixture_path`).

## Invariants
1. All wire property names across schemas, OpenAPI specs, and golden vectors use `camelCase`.
2. `services[].mode` enum is strictly `["LocalOnly", "CellSingleton", "Distributed"]`.
3. `LeaseRecordDto` extends `LeaseInfo` (`masId`, `holderNodeId`, `fencingToken`, `acquiredAt`, `expiresAt`, `lastKnownMarker`).
4. DevSecOps telemetry payloads published over `/cell/events/{topicId}` conform to `ops-telemetry.schema.json` (`ops.logs.error`, `ops.lifecycle.crash`, `ops.perf.anomaly`, `ops.audit.security`) across both `aurasprout` and `auragrid` runtime tiers.
5. Run `pytest tests/test_schemas_and_vectors.py` after any contract review.
