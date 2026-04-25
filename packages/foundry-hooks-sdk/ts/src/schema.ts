export const MANIFEST_SCHEMA = {
  $schema: "https://json-schema.org/draft/2020-12/schema",
  $id: "https://foundry.dev/schemas/manifest.schema.json",
  title: "FoundryManifest",
  type: "object",
  required: ["app", "features"],
  additionalProperties: false,
  properties: {
    app: { type: "string", minLength: 1, maxLength: 160 },
    version: { type: "string" },
    features: {
      type: "array",
      minItems: 1,
      items: { $ref: "#/$defs/feature" },
    },
    security: { $ref: "#/$defs/security" },
    release: { $ref: "#/$defs/release" },
  },
  $defs: {
    feature: {
      type: "object",
      required: ["name"],
      additionalProperties: false,
      properties: {
        name: { type: "string", pattern: "^[a-z][a-z0-9-]{1,79}$" },
        description: { type: "string" },
        paths: { type: "array", items: { type: "string" } },
        signals: { type: "array", items: { type: "string" } },
      },
    },
    security: {
      type: "object",
      additionalProperties: false,
      properties: {
        sensitiveRoutes: { type: "array", items: { type: "string" } },
        sensitiveStores: { type: "array", items: { type: "string" } },
        privilegedActions: { type: "array", items: { type: "string" } },
      },
    },
    release: {
      type: "object",
      additionalProperties: false,
      properties: {
        routeInventoryFile: { type: "string" },
        envTemplateFile: { type: "string" },
        schemaGlobs: { type: "array", items: { type: "string" } },
        migrationGlobs: { type: "array", items: { type: "string" } },
        releaseDocGlobs: { type: "array", items: { type: "string" } },
      },
    },
  },
} as const;
