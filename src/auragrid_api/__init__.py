"""Canonical wire contract path and fixture loaders for ``auragrid-api``.

This package contains zero runtime business logic, HTTP servers, or network
clients. It exposes read-only accessors to canonical JSON Schemas, OpenAPI 3.1
specifications, and golden wire vectors shared across AuraGrid (.NET 10),
``auragrid-py``, and ``aurasprout``.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

__version__ = "4.3.0"

_PACKAGE_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _PACKAGE_DIR.parent.parent


def _resolve_root_dir(subdir: str) -> Path:
    """Resolve a data directory from bundled package data or the repository root."""
    bundled = _PACKAGE_DIR / subdir
    if bundled.is_dir():
        return bundled
    repo_dir = _REPO_ROOT / subdir
    if repo_dir.is_dir():
        return repo_dir
    raise FileNotFoundError(
        f"Contract directory '{subdir}' not found in '{bundled}' or '{repo_dir}'."
    )


def _safe_child(base_dir: Path, name: str) -> Path:
    """Resolve a filename or relative subpath safely inside ``base_dir``."""
    candidate = (base_dir / name).resolve()
    resolved_base = base_dir.resolve()
    try:
        candidate.relative_to(resolved_base)
    except ValueError as exc:
        raise ValueError(f"Path '{name}' escapes contract directory '{resolved_base}'.") from exc
    if not candidate.is_file():
        raise FileNotFoundError(f"Contract file '{name}' not found under '{resolved_base}'.")
    return candidate


def get_schema_path(name: str) -> Path:
    """Return the absolute path to a JSON Schema file in ``schemas/``."""
    return _safe_child(_resolve_root_dir("schemas"), name)


def get_openapi_path(name: str) -> Path:
    """Return the absolute path to an OpenAPI specification file in ``openapi/``."""
    return _safe_child(_resolve_root_dir("openapi"), name)


def get_fixture_path(name: str) -> Path:
    """Return the absolute path to a golden fixture file in ``fixtures/wire_vectors/``."""
    return _safe_child(_resolve_root_dir("fixtures") / "wire_vectors", name)


def list_schemas() -> list[str]:
    """List all JSON Schema filenames shipped by ``auragrid-api``."""
    return sorted(p.name for p in _resolve_root_dir("schemas").glob("*.json"))


def list_openapi_specs() -> list[str]:
    """List all OpenAPI specification filenames shipped by ``auragrid-api``."""
    return sorted(p.name for p in _resolve_root_dir("openapi").glob("*.json"))


def list_wire_vectors() -> list[str]:
    """List all golden wire vector filenames shipped under ``fixtures/wire_vectors/``."""
    vectors_dir = _resolve_root_dir("fixtures") / "wire_vectors"
    return sorted(p.name for p in vectors_dir.glob("*.json"))


def load_schema(name: str) -> dict[str, Any]:
    """Load and parse a canonical JSON Schema dictionary."""
    return json.loads(get_schema_path(name).read_text(encoding="utf-8"))


def load_openapi(name: str) -> dict[str, Any]:
    """Load and parse a canonical OpenAPI 3.1 specification dictionary."""
    return json.loads(get_openapi_path(name).read_text(encoding="utf-8"))


def load_wire_vector(name: str) -> Any:
    """Load and parse a golden JSON wire vector."""
    return json.loads(get_fixture_path(name).read_text(encoding="utf-8"))


__all__ = [
    "__version__",
    "get_fixture_path",
    "get_openapi_path",
    "get_schema_path",
    "list_openapi_specs",
    "list_schemas",
    "list_wire_vectors",
    "load_openapi",
    "load_schema",
    "load_wire_vector",
]
