# `auragrid-api`

Canonical JSON Schemas, OpenAPI 3.1 specifications, wire protocol documentation, and golden test vectors shared by:
- **AuraGrid** (.NET 10)
- **auragrid-py** (Python MAS SDK)
- **AuraSprout** (User-Space App Distribution & Collaborative Runtime)

## Package API
```python
from auragrid_api import get_schema_path, get_openapi_path, load_schema, load_openapi

manifest_schema = load_schema("app.manifest.schema.json")
ipc_spec = load_openapi("ipc-bridge.openapi.json")
```

## Layout
- `schemas/` — `app.manifest.schema.json`, `service-descriptor.schema.json`, `catalog.schema.json`, `lease-collaboration.schema.json`
- `openapi/` — `ipc-bridge.openapi.json`, `aurasprout-management.openapi.json`
- `docs/` — `ipc-protocol.md`, `package-and-catalog-spec.md`, `collaborative-shared-processing.md`
- `fixtures/wire_vectors/` — Golden JSON payloads verified by `tests/test_schemas_and_vectors.py`
