# `auragrid-api`

Canonical JSON Schema (Draft-07) contracts, OpenAPI 3.1 specifications, wire protocol documentation, and golden test vectors shared by:
- **AuraGrid** (.NET 10)
- **auragrid-py** (Python MAS SDK)
- **AuraSprout** (User-Space App Distribution & Collaborative Runtime)

## Package API
```python
from auragrid_api import get_schema_path, get_openapi_path, load_schema, load_openapi

manifest_schema = load_schema("app.manifest.schema.json")
ops_telemetry_schema = load_schema("ops-telemetry.schema.json")
ipc_spec = load_openapi("ipc-bridge.openapi.json")
```

## Layout
- `schemas/` — 5 canonical JSON Schema (Draft-07) contracts, mirrored in `src/auragrid_api/schemas/` (10 JSON Schemas bundled across repo and wheel package):
  - `app.manifest.schema.json`
  - `service-descriptor.schema.json`
  - `catalog.schema.json`
  - `lease-collaboration.schema.json`
  - `ops-telemetry.schema.json`
- `openapi/` — 2 OpenAPI 3.1 specifications (`ipc-bridge.openapi.json`, `aurasprout-management.openapi.json`), mirrored in `src/auragrid_api/openapi/`
- `docs/` — `ipc-protocol.md`, `package-and-catalog-spec.md`, `collaborative-shared-processing.md`
- `fixtures/wire_vectors/` — 7 golden JSON payload files (`app_manifest.json`, `service_descriptor.json`, `catalog_manifest.json`, `lease_collaboration_vectors.json`, `ipc_bridge_vectors.json`, `management_vectors.json`, `ops_telemetry_vectors.json`) verified by `tests/test_schemas_and_vectors.py`
