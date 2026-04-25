import Ajv2020 from "ajv/dist/2020";
import type { ErrorObject } from "ajv";
import { MANIFEST_SCHEMA } from "./schema";

export interface ManifestFeature {
  name: string;
  description?: string;
  paths?: string[];
  signals?: string[];
}

export interface ManifestSecurity {
  sensitiveRoutes?: string[];
  sensitiveStores?: string[];
  privilegedActions?: string[];
}

export interface ManifestRelease {
  routeInventoryFile?: string;
  envTemplateFile?: string;
  schemaGlobs?: string[];
  migrationGlobs?: string[];
  releaseDocGlobs?: string[];
}

export interface FoundryManifest {
  app: string;
  version?: string;
  features: ManifestFeature[];
  security?: ManifestSecurity;
  release?: ManifestRelease;
}

export class ManifestValidationError extends Error {
  readonly details: string[];
  constructor(details: string[]) {
    super(details.join("; ") || "invalid manifest");
    this.name = "ManifestValidationError";
    this.details = details;
  }
}

const ajv = new Ajv2020({ allErrors: true, strict: false });
const validator = ajv.compile(MANIFEST_SCHEMA);

export function validateManifest(data: unknown): FoundryManifest {
  if (!validator(data)) {
    const errors = (validator.errors ?? []).map(formatError);
    throw new ManifestValidationError(errors);
  }
  return data as FoundryManifest;
}

export function loadManifest(text: string): FoundryManifest {
  let parsed: unknown;
  try {
    parsed = JSON.parse(text);
  } catch (err) {
    throw new ManifestValidationError([`invalid JSON: ${(err as Error).message}`]);
  }
  return validateManifest(parsed);
}

function formatError(err: ErrorObject): string {
  const path = err.instancePath || err.schemaPath || "";
  return `${path} ${err.message ?? "invalid"}`.trim();
}

export { MANIFEST_SCHEMA };
