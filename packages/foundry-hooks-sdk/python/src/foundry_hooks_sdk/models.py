"""Pydantic models mirroring the JSON schema."""

from __future__ import annotations

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


_FEATURE_NAME_RE = re.compile(r"^[a-z][a-z0-9-]{1,79}$")


class ManifestFeature(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str | None = None
    paths: list[str] = Field(default_factory=list)
    signals: list[str] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def _check_name(cls, v: str) -> str:
        if not _FEATURE_NAME_RE.match(v):
            raise ValueError(
                "feature name must be lower-kebab-case, 2-80 chars, starting with a letter"
            )
        return v


class ManifestSecurity(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    sensitive_routes: list[str] = Field(default_factory=list, alias="sensitiveRoutes")
    sensitive_stores: list[str] = Field(default_factory=list, alias="sensitiveStores")
    privileged_actions: list[str] = Field(default_factory=list, alias="privilegedActions")


class ManifestRelease(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    route_inventory_file: str | None = Field(default=None, alias="routeInventoryFile")
    env_template_file: str | None = Field(default=None, alias="envTemplateFile")
    schema_globs: list[str] = Field(default_factory=list, alias="schemaGlobs")
    migration_globs: list[str] = Field(default_factory=list, alias="migrationGlobs")
    release_doc_globs: list[str] = Field(default_factory=list, alias="releaseDocGlobs")


class FoundryManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    app: str = Field(min_length=1, max_length=160)
    version: str = "0.1"
    features: list[ManifestFeature]
    security: ManifestSecurity | None = None
    release: ManifestRelease | None = None
    tech_stacks: list[str] = Field(default_factory=list, alias="techStacks")

    def feature_path_map(self) -> dict[str, list[str]]:
        return {f.name: list(f.paths) for f in self.features}

    def feature_signal_map(self) -> dict[str, list[str]]:
        return {f.name: list(f.signals) for f in self.features}
