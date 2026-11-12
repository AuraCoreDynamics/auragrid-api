# Changelog

## 4.3.0
- Extracted canonical AuraCore wire contracts, JSON Schemas, OpenAPI 3.1 specifications (`ipc-bridge.openapi.json`, `aurasprout-management.openapi.json`), protocol documentation, and golden wire vectors into `auragrid-api`.
- Standardized `MasMode` (`services[].mode`) around `LocalOnly`, `CellSingleton`, and `Distributed`.
- Unified catalog contracts (`CatalogManifest`, `CatalogAppEntry`, `AppVersionEntry`, `.apkg`, SHA-256 verification) and collaboration contracts (`LeaseRecordDto`, `WorkBatchClaimDto`, `LeaseConflictDto`, `WalMarker`).
