# CLAUDE.md — `auragrid-api`

## Role & Scope
`C:\projects\auracore\auragrid-api` is the **canonical contract repository** for the AuraCore ecosystem (`auragrid`, `auragrid-py`, `auraseed`, `aurasprout`).

This repository contains **ZERO runtime business logic, HTTP servers, network clients, or database code**. It holds only:
- `schemas/` — Draft-07 JSON Schemas (`app.manifest.schema.json`, `service-descriptor.schema.json`, `catalog.schema.json`, `lease-collaboration.schema.json`).
- `openapi/` — OpenAPI 3.1 specifications (`ipc-bridge.openapi.json`, `aurasprout-management.openapi.json`).
- `docs/` — Canonical wire & packaging protocol specifications.
- `fixtures/wire_vectors/` — Golden JSON test vectors validated by `tests/test_schemas_and_vectors.py`.
- `src/auragrid_api/__init__.py` — Read-only path and JSON loader helpers (`get_schema_path`, `get_openapi_path`, `get_fixture_path`).

## Invariants
1. All wire property names across schemas, OpenAPI specs, and golden vectors use `camelCase`.
2. `services[].mode` enum is strictly `["LocalOnly", "CellSingleton", "Distributed"]`.
3. `LeaseRecordDto` extends `LeaseInfo` (`masId`, `holderNodeId`, `fencingToken`, `acquiredAt`, `expiresAt`, `lastKnownMarker`).
4. Run `pytest tests/test_schemas_and_vectors.py` after any contract review.
