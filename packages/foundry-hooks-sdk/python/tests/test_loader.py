import json

import pytest

from foundry_hooks_sdk import ManifestError, load_manifest, validate_manifest_dict


VALID = {
    "app": "AxTask",
    "version": "0.1",
    "features": [
        {
            "name": "task-creation",
            "paths": ["src/features/tasks/**"],
            "signals": ["task.created"],
        }
    ],
    "security": {
        "sensitiveRoutes": ["/admin"],
        "sensitiveStores": ["userTokens"],
        "privilegedActions": ["admin.override"],
    },
    "release": {
        "routeInventoryFile": "routes.ts",
        "schemaGlobs": ["shared/schema/**"],
    },
    "techStacks": ["typescript", "python"],
}


def test_valid_manifest_roundtrips() -> None:
    m = load_manifest(json.dumps(VALID))
    assert m.app == "AxTask"
    assert m.features[0].name == "task-creation"
    assert m.security is not None
    assert m.security.sensitive_routes == ["/admin"]
    assert m.release is not None
    assert m.release.route_inventory_file == "routes.ts"
    assert m.tech_stacks == ["typescript", "python"]


def test_missing_app_fails() -> None:
    bad = dict(VALID)
    bad.pop("app")
    with pytest.raises(ManifestError):
        validate_manifest_dict(bad)


def test_bad_feature_name_fails() -> None:
    bad = json.loads(json.dumps(VALID))
    bad["features"][0]["name"] = "Not-Kebab!"
    with pytest.raises(ManifestError):
        validate_manifest_dict(bad)


def test_feature_path_map() -> None:
    m = load_manifest(json.dumps(VALID))
    assert m.feature_path_map() == {"task-creation": ["src/features/tasks/**"]}


def test_manifest_without_optional_fields_roundtrips() -> None:
    minimal = {
        "app": "AxTask",
        "features": [{"name": "task-creation", "paths": ["src/**"]}],
    }
    m = load_manifest(json.dumps(minimal))
    assert m.release is None
    assert m.tech_stacks == []
