# `foundry.manifest.json` reference

The manifest is a small, optional file an application drops at its repo root.
It lets Foundry map raw Git activity to **features** and **security-sensitive
surfaces** without modifying the app.

## Minimal example

```json
{
  "app": "AxTask",
  "version": "0.1",
  "features": [
    {
      "name": "adherence-tracking",
      "description": "Measure whether users follow scheduled tasks.",
      "paths": ["server/adherence-*.ts", "client/src/features/adherence/**"],
      "signals": ["adherence.measured"]
    }
  ],
  "security": {
    "sensitiveRoutes": ["/api/auth"],
    "sensitiveStores": ["users"],
    "privilegedActions": ["account.backup.import"]
  }
}
```

## Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `app` | string | yes | Display name for the application |
| `version` | string | no | Manifest schema version. `0.1` is current |
| `features` | array | yes | At least one feature entry |
| `features[].name` | string | yes | Slug, used as a stable key |
| `features[].description` | string | no | Shown in UI tooltips |
| `features[].paths` | array\<string\> | yes | Globs against repo root |
| `features[].signals` | array\<string\> | no | Runtime signal names (future) |
| `security.sensitiveRoutes` | array\<string\> | no | URL paths |
| `security.sensitiveStores` | array\<string\> | no | Table/collection names |
| `security.privilegedActions` | array\<string\> | no | Domain-level action names |

The canonical JSON Schema lives at
`packages/foundry-hooks-sdk/schema/manifest.schema.json` and is embedded in both
loaders.

## Loaders

### Python

```python
from foundry_hooks_sdk import load_manifest_from_file

manifest = load_manifest_from_file("foundry.manifest.json")
for f in manifest.features:
    print(f.name, f.paths)
```

### TypeScript

```ts
import { loadManifest } from "@foundry/hooks-sdk";
import raw from "./foundry.manifest.json";

const manifest = loadManifest(raw); // throws ManifestValidationError on bad input
```

## Authoring tips

- **Feature paths are globs**, resolved from repo root. Prefer specific
  globs to `**`; specificity raises confidence.
- A single file can belong to multiple features. Overlaps are fine; Foundry
  scores by best match.
- `security.*` lists are free-form strings; use your actual route/collection
  names so GuardFoundry (future) can pattern-match them.
- Version your manifest when you change shape. v0.1 is loose by design.

## Integration example

See [`../examples/axtask-integration/`](../examples/axtask-integration/) for a
full working manifest against the AxTask app.
