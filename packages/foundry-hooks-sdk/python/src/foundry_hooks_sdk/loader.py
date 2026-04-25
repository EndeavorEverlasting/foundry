"""Load and validate foundry.manifest.json files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from foundry_hooks_sdk.models import FoundryManifest
from foundry_hooks_sdk.schema import MANIFEST_SCHEMA


class ManifestError(ValueError):
    """Raised when a manifest fails schema or model validation."""

    def __init__(self, messages: list[str]):
        self.messages = messages
        super().__init__("; ".join(messages) or "invalid manifest")


_VALIDATOR = Draft202012Validator(MANIFEST_SCHEMA)


def validate_manifest_dict(data: dict[str, Any]) -> FoundryManifest:
    """Validate against JSON Schema + Pydantic, raising ManifestError on failure."""

    errors = sorted(_VALIDATOR.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        messages = [_format_jsonschema_error(e) for e in errors]
        raise ManifestError(messages)

    try:
        return FoundryManifest.model_validate(data)
    except Exception as exc:  # noqa: BLE001
        raise ManifestError([str(exc)]) from exc


def load_manifest(text: str) -> FoundryManifest:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ManifestError([f"invalid JSON: {exc}"]) from exc

    if not isinstance(data, dict):
        raise ManifestError(["manifest must be a JSON object"])

    return validate_manifest_dict(data)


def load_manifest_from_file(path: str | Path) -> FoundryManifest:
    p = Path(path)
    if not p.exists():
        raise ManifestError([f"manifest file not found: {p}"])
    return load_manifest(p.read_text(encoding="utf-8"))


def _format_jsonschema_error(err: object) -> str:
    # Use duck-typed access to keep the jsonschema import light.
    path = ".".join(str(p) for p in getattr(err, "absolute_path", []))
    msg = getattr(err, "message", str(err))
    return f"{path}: {msg}" if path else msg
