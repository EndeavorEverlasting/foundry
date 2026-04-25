"""Embedded JSON Schema so the Python loader has zero I/O dependencies."""

from __future__ import annotations

from importlib.resources import files


def _load_schema() -> dict[str, object]:
    import json

    # Schema is colocated with the SDK source via package data lookup.
    # At build time, hatchling includes src/foundry_hooks_sdk. The canonical
    # schema file lives at packages/foundry-hooks-sdk/schema/manifest.schema.json;
    # we inline it below so the SDK remains self-contained as a wheel.
    return _EMBEDDED


_EMBEDDED: dict[str, object] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "https://foundry.dev/schemas/manifest.schema.json",
    "title": "FoundryManifest",
    "type": "object",
    "required": ["app", "features"],
    "additionalProperties": False,
    "properties": {
        "app": {"type": "string", "minLength": 1, "maxLength": 160},
        "version": {"type": "string"},
        "features": {
            "type": "array",
            "minItems": 1,
            "items": {"$ref": "#/$defs/feature"},
        },
        "security": {"$ref": "#/$defs/security"},
    },
    "$defs": {
        "feature": {
            "type": "object",
            "required": ["name"],
            "additionalProperties": False,
            "properties": {
                "name": {
                    "type": "string",
                    "pattern": r"^[a-z][a-z0-9-]{1,79}$",
                },
                "description": {"type": "string"},
                "paths": {"type": "array", "items": {"type": "string"}},
                "signals": {"type": "array", "items": {"type": "string"}},
            },
        },
        "security": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "sensitiveRoutes": {"type": "array", "items": {"type": "string"}},
                "sensitiveStores": {"type": "array", "items": {"type": "string"}},
                "privilegedActions": {"type": "array", "items": {"type": "string"}},
            },
        },
    },
}


MANIFEST_SCHEMA: dict[str, object] = _EMBEDDED


def get_schema() -> dict[str, object]:
    """Return a copy of the canonical manifest schema."""

    import copy

    return copy.deepcopy(MANIFEST_SCHEMA)


__all__ = ["MANIFEST_SCHEMA", "get_schema"]


# Trigger access so 'files' is referenced for potential future loading.
_ = files
