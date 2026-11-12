"""Contract and golden wire vector validation tests for ``auragrid-api``."""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import jsonschema
from jsonschema import Draft7Validator, FormatChecker

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import auragrid_api  # noqa: E402


def _collect_refs(node: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                refs.append(value)
            else:
                refs.extend(_collect_refs(value))
    elif isinstance(node, list):
        for item in node:
            refs.extend(_collect_refs(item))
    return refs


def _resolve_internal_pointer(root: dict[str, Any], ref: str) -> Any:
    if not ref.startswith("#/"):
        raise AssertionError(f"Unsupported external or relative $ref: {ref}")
    current: Any = root
    for token in ref[2:].split("/"):
        token = token.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, dict) or token not in current:
            raise AssertionError(f"Unresolved JSON pointer '{ref}' (missing '{token}')")
        current = current[token]
    return current


def _validate_against_definition(
    root_schema: dict[str, Any],
    definition_name: str,
    payload: Any,
    section: str = "definitions",
) -> None:
    if section == "components/schemas":
        subschema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$ref": f"#/components/schemas/{definition_name}",
            "components": {"schemas": root_schema["components"]["schemas"]},
        }
    else:
        subschema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "$ref": f"#/{section}/{definition_name}",
            section: root_schema[section],
        }
    validator = Draft7Validator(subschema, format_checker=FormatChecker())
    validator.validate(payload)


def test_package_contains_zero_runtime_implementation_logic() -> None:
    """Verify ``auragrid_api`` exposes only contract path and fixture loaders."""
    init_file = SRC_DIR / "auragrid_api" / "__init__.py"
    source = init_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)
        elif isinstance(node, ast.ClassDef):
            raise AssertionError(f"Unexpected runtime class '{node.name}' in auragrid_api")

    forbidden = {"http", "http.server", "socket", "sqlite3", "httpx", "urllib", "asyncio", "subprocess"}
    assert imported_modules.isdisjoint(forbidden), f"Forbidden runtime imports: {imported_modules & forbidden}"
    assert list((SRC_DIR / "auragrid_api").glob("*.py")) == [init_file]


def test_schema_files_valid_and_mode_enum_unified() -> None:
    """Validate every JSON Schema and confirm MasMode enum lockdown."""
    expected = {
        "app.manifest.schema.json",
        "service-descriptor.schema.json",
        "catalog.schema.json",
        "lease-collaboration.schema.json",
    }
    assert expected.issubset(set(auragrid_api.list_schemas()))

    for name in expected:
        schema_path = auragrid_api.get_schema_path(name)
        assert schema_path.is_file()
        schema = auragrid_api.load_schema(name)
        Draft7Validator.check_schema(schema)
        for ref in _collect_refs(schema):
            _resolve_internal_pointer(schema, ref)

    app_schema = auragrid_api.load_schema("app.manifest.schema.json")
    assert app_schema["definitions"]["masMode"]["enum"] == [
        "LocalOnly",
        "CellSingleton",
        "Distributed",
    ]
    lease_schema = auragrid_api.load_schema("lease-collaboration.schema.json")
    assert lease_schema["definitions"]["masMode"]["enum"] == [
        "LocalOnly",
        "CellSingleton",
        "Distributed",
    ]


def test_openapi_specs_have_zero_unresolved_refs() -> None:
    """Validate OpenAPI 3.1 specs exist, parse cleanly, and have 0 broken $refs."""
    expected_specs = {
        "ipc-bridge.openapi.json",
        "aurasprout-management.openapi.json",
    }
    assert expected_specs.issubset(set(auragrid_api.list_openapi_specs()))

    for spec_name in expected_specs:
        spec_path = auragrid_api.get_openapi_path(spec_name)
        assert spec_path.is_file()
        spec = auragrid_api.load_openapi(spec_name)
        assert spec["openapi"].startswith("3.1.")
        assert spec["paths"]
        assert spec["components"]["schemas"]
        for ref in _collect_refs(spec):
            _resolve_internal_pointer(spec, ref)

    ipc_spec = auragrid_api.load_openapi("ipc-bridge.openapi.json")
    for required_path in (
        "/health",
        "/api/health",
        "/ready",
        "/cell/config",
        "/cell/governance/audit",
        "/cell/events/topics",
        "/cell/lease/acquire",
        "/cell/collaboration/volunteer",
        "/cell/collaboration/batches/claim",
        "/cell/collaboration/conflicts",
        "/cell/storage/read",
        "/cell/storage/write",
        "/cell/storage/append",
        "/cell/storage/delete",
        "/cell/storage/exists",
        "/cell/registry/discover",
    ):
        assert required_path in ipc_spec["paths"], f"Missing route {required_path} in ipc-bridge.openapi.json"


def test_all_wire_vectors_match_schemas() -> None:
    """Named gate test verifying every golden JSON fixture validates against its schema."""
    app_schema = auragrid_api.load_schema("app.manifest.schema.json")
    Draft7Validator(app_schema, format_checker=FormatChecker()).validate(
        auragrid_api.load_wire_vector("app_manifest.json")
    )

    descriptor_schema = auragrid_api.load_schema("service-descriptor.schema.json")
    Draft7Validator(descriptor_schema, format_checker=FormatChecker()).validate(
        auragrid_api.load_wire_vector("service_descriptor.json")
    )

    catalog_schema = auragrid_api.load_schema("catalog.schema.json")
    Draft7Validator(catalog_schema, format_checker=FormatChecker()).validate(
        auragrid_api.load_wire_vector("catalog_manifest.json")
    )

    lease_schema = auragrid_api.load_schema("lease-collaboration.schema.json")
    lease_vectors = auragrid_api.load_wire_vector("lease_collaboration_vectors.json")
    for def_name in (
        "walMarker",
        "leaseInfo",
        "leaseRecordDto",
        "leaseAcquisitionResult",
        "workBatchClaimDto",
        "leaseConflictDto",
    ):
        assert def_name in lease_vectors
        _validate_against_definition(lease_schema, def_name, lease_vectors[def_name], section="definitions")

    ipc_spec = auragrid_api.load_openapi("ipc-bridge.openapi.json")
    ipc_vectors = auragrid_api.load_wire_vector("ipc_bridge_vectors.json")
    for schema_name, payload in ipc_vectors.items():
        _validate_against_definition(ipc_spec, schema_name, payload, section="components/schemas")

    mgmt_spec = auragrid_api.load_openapi("aurasprout-management.openapi.json")
    mgmt_vectors = auragrid_api.load_wire_vector("management_vectors.json")
    for schema_name, payload in mgmt_vectors.items():
        _validate_against_definition(mgmt_spec, schema_name, payload, section="components/schemas")
