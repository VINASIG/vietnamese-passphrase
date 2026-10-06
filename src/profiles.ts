import { readFile } from "node:fs/promises";

const dataProfiles = [
  "vi",
  "vi-ascii",
  "vi-short",
  "vi-display",
  "vi-fused",
  "vi-ascii-display",
  "vi-ascii-native",
  "vi-distinct",
] as const;
type DataProfile = (typeof dataProfiles)[number];

export interface Profile {
  readonly id: string;
  readonly dataProfile: DataProfile;
  readonly status: string;
  readonly purpose: string;
  readonly generation: boolean;
  readonly limitation: string;
}

export function record(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    throw new Error("Invalid metadata object");
  return value as Record<string, unknown>;
}

export async function readProfiles(): Promise<readonly Profile[]> {
  const raw: unknown = JSON.parse(
    await readFile(
      new URL("../research/profile-catalog.json", import.meta.url),
      "utf8",
    ),
  );
  const catalog = record(raw);
  if (catalog.schema !== 1 || catalog.noRecommendedDefault !== true)
    throw new Error("Invalid profile catalog");
  const seen = new Set<DataProfile>();
  const profiles = Object.entries(record(catalog.profiles)).map(
    ([id, value]) => {
      const fields = record(value);
      const dataProfile = dataProfiles.find((p) => p === fields.dataProfile);
      if (
        !/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(id) ||
        dataProfile === undefined ||
        seen.has(dataProfile)
      )
        throw new Error("Invalid or duplicate profile identity");
      seen.add(dataProfile);
      if (
        typeof fields.status !== "string" ||
        typeof fields.purpose !== "string" ||
        typeof fields.limitation !== "string" ||
        typeof fields.generation !== "boolean"
      )
        throw new Error("Missing profile evidence or usage policy");
      if (
        (dataProfile === "vi-short" || dataProfile === "vi-ascii-native") &&
        fields.generation
      )
        throw new Error(
          "Diagnostic and control profiles cannot enable CLI generation",
        );
      return Object.freeze({
        id,
        dataProfile,
        status: fields.status,
        purpose: fields.purpose,
        generation: fields.generation,
        limitation: fields.limitation,
      });
    },
  );
  if (seen.size !== dataProfiles.length)
    throw new Error("Incomplete profile catalog");
  return Object.freeze(profiles);
}

export function location(profile: Profile) {
  const legacy =
    profile.dataProfile === "vi" ||
    profile.dataProfile === "vi-ascii" ||
    profile.dataProfile === "vi-short";
  const base = new URL(
    legacy ? "../data/" : "../research/experimental/2026-10-06.agent-1/",
    import.meta.url,
  );
  return {
    manifest: new URL("manifest.json", base),
    list: new URL(
      (legacy ? "lists/" : "") + profile.dataProfile + ".txt",
      base,
    ),
  };
}
