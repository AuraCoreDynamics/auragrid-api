# AuraCore Package & Catalog Specification

## 1. Canonical Package Formats (`.apkg` / `.aurabundle`)

AuraSprout distributes user-space Python and hybrid applications using `.apkg` archives (ZIP or gzip-compressed tar archives verified strictly for path-traversal safety before extraction) conforming to [`../schemas/app.manifest.schema.json`](../schemas/app.manifest.schema.json).

### Internal Layout
```
<appId>-<version>.apkg
├── app.manifest.json        # Canonical AuraCore manifest (app.manifest.schema.json)
├── wheels/                  # Optional offline wheelhouse (for sovereign/air-gapped installs)
│   └── *.whl
├── src/                     # Application payload / entrypoints / icons / scripts
└── hooks/                   # Optional install/uninstall lifecycle scripts
```

Integrity rules:
- Every archive member path MUST normalize inside the extraction target root (rejecting `..`, rooted paths, and unsafe symlinks).
- Every cataloged package entry includes a 64-character hexadecimal SHA-256 checksum (`bundleSha256`) and exact byte count (`bundleSizeBytes`), verified prior to unpacking.

---

## 2. Shared Cell & Local Storage Topology (`SproutPaths`)

On local machines and shared SMB/NFS roots, **AuraSprout** uses a deterministic directory layout:

```
<cell_root>/
└── .sprout/
    ├── events/
    │   └── events.sqlite        # SMB-safe SQLite store (PRAGMA journal_mode=TRUNCATE)
    ├── leases/
    │   └── <masId>.lease.json   # CellSingleton LeaseRecordDto + fencing token counter
    ├── locks/
    │   └── <name>.lock/         # SproutMutex atomic O_CREAT/mkdir lock dirs
    ├── claims/
    │   └── <masId>/<batchId>.claim.json  # WorkBatchClaimDto records
    ├── nodes/
    │   └── <nodeId>.json        # Node presence heartbeats (never written by LocalOnly)
    ├── config/
    │   └── cell_config.json     # Shared cell configuration key/value state
    ├── registry/
    │   └── services.json        # Discovered CellSingleton/Distributed service endpoints
    ├── conflicts/
    │   └── <conflictId>.json    # Pending LeaseConflictDto records
    └── staging/
        └── <masId>/<token>/     # Fenced write staging directories before atomic swap
```

User-local application installs reside strictly under user-writable directories (`%LOCALAPPDATA%\AuraSprout` on Windows; `~/.local/share/aurasprout` or `~/.aurasprout` on POSIX) requiring zero OS administrator privileges.

---

## 3. Unified Application Catalog (`catalog.schema.json`)

The catalog unifies static web portals (`catalog.json` + generated static HTML), attached HTTP/REST AuraSeed/AuraSprout catalogs (`catalogs.json`), shared-filesystem channel folders (`<channel>/<appId>.manifest.json`), and AuraGrid `CatalogChannelReconciler` entries under [`../schemas/catalog.schema.json`](../schemas/catalog.schema.json).

Supported release channels: `stable`, `preview`, `canary`, `nightly`.
Supported delta optimizations: `wheelhousePath` and `deltaFromVersion` for incremental offline upgrades.
