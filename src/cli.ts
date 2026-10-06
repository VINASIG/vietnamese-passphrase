#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { generate, verifyWordlist } from "./index.ts";
import type { PhraseOptions } from "./index.ts";

const profiles = [
  "vi",
  "vi-ascii",
  "vi-short",
  "vi-display",
  "vi-fused",
  "vi-ascii-display",
  "vi-ascii-native",
  "vi-distinct",
] as const;
type Profile = (typeof profiles)[number];
const base = new URL("../data/", import.meta.url);
const experimental = new URL(
  "../research/experimental/2026-10-06.agent-1/",
  import.meta.url,
);
const entropyScope =
  "independent uniform draws from pinned unique tokens with injective encoding; not measured memorability or downstream security";

function location(profile: Profile) {
  const legacy =
    profile === "vi" || profile === "vi-ascii" || profile === "vi-short";
  return {
    manifest: new URL("manifest.json", legacy ? base : experimental),
    list: new URL(
      (legacy ? "lists/" : "") + profile + ".txt",
      legacy ? base : experimental,
    ),
    status: legacy
      ? "historical-research-preview"
      : "experimental-agent-assessment",
  };
}

function record(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    throw new Error("Invalid data manifest");
  return value as Record<string, unknown>;
}

async function load(profile: Profile) {
  const path = location(profile);
  const metadata: unknown = JSON.parse(await readFile(path.manifest, "utf8"));
  const spec = record(record(record(metadata).profiles)[profile]);
  if (typeof spec.sha256 !== "string")
    throw new Error("Missing wordlist checksum");
  return verifyWordlist(await readFile(path.list), spec.sha256);
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);
  if (command === undefined || command === "help" || command === "--help") {
    process.stdout.write(
      "Vietnamese Passphrase\n\nGenerate locally with an explicit profile and explicit bit target or word count\n  vietphrase generate --profile vi --bits 80\n  vietphrase generate --profile vi-fused --words 8 --json\n\nInspect the wordlist without generating a secret\n  vietphrase info --profile vi\n  vietphrase verify\n\nHistorical profiles: vi, vi-ascii, vi-short\nExperimental profiles: vi-display, vi-fused, vi-ascii-display, vi-ascii-native, vi-distinct\nNo vocabulary is a recommended universal default. Verification checks bytes and format.\nEntropy assumes independent uniform draws, not measured memorability or downstream security.\n",
    );
    return;
  }
  if (!["generate", "info", "verify"].includes(command))
    throw new Error("Unknown command. Run vietphrase help");
  let selected: Profile = "vi";
  let bits: number | undefined;
  let words: number | undefined;
  let separator: string | undefined;
  let json = false;
  const seen = new Set<string>();
  for (let i = 0; i < args.length; i++) {
    const flag = args[i];
    if (flag === undefined || seen.has(flag))
      throw new Error("Invalid or repeated option");
    seen.add(flag);
    if (flag === "--json") {
      json = true;
      continue;
    }
    const value = args[++i];
    if (value === undefined) throw new Error("An option value is required");
    if (flag === "--profile") {
      const profile = profiles.find((p) => p === value);
      if (profile === undefined)
        throw new Error("Choose a listed profile. Run vietphrase help");
      selected = profile;
    } else if (flag === "--bits" || flag === "--words") {
      if (!/^\d+(?:\.\d+)?$/.test(value))
        throw new Error("Supply a positive number");
      if (flag === "--bits") bits = Number(value);
      else words = Number(value);
    } else if (flag === "--separator") separator = value;
    else throw new Error("Unknown option. Run vietphrase help");
  }
  if (
    command !== "generate" &&
    (bits !== undefined ||
      words !== undefined ||
      separator !== undefined ||
      json)
  )
    throw new Error("Generation options require the generate command");
  if (command === "verify") {
    if (args.length !== 0)
      throw new Error("The verify command takes no options");
    for (const profile of profiles) {
      const list = await load(profile);
      process.stdout.write(
        profile +
          " INTEGRITY_PASS " +
          String(list.size) +
          " tokens (pinned bytes and format only)\n",
      );
    }
    return;
  }
  const list = await load(selected);
  if (command === "info") {
    process.stdout.write(
      JSON.stringify(
        {
          profile: selected,
          entries: list.size,
          bitsPerDraw: list.bitsPerDraw,
          listPath: fileURLToPath(location(selected).list),
          status: location(selected).status,
          entropyScope,
          humanValidation: "not-performed; SI-agent-only project",
          independentSecurityAudit: "not-performed",
        },
        null,
        2,
      ) + "\n",
    );
    return;
  }
  if (!seen.has("--profile"))
    throw new Error(
      "Generation requires an explicit --profile; there is no recommended default vocabulary",
    );
  const options: PhraseOptions = {
    ...(bits === undefined ? {} : { bits }),
    ...(words === undefined ? {} : { words }),
    ...(separator === undefined ? {} : { separator }),
  };
  const result = generate(list, options);
  process.stdout.write(
    json
      ? JSON.stringify({
          profile: selected,
          status: location(selected).status,
          entropyScope,
          ...result,
        }) + "\n"
      : result.passphrase + "\n",
  );
}

try {
  await main();
} catch (error) {
  process.stderr.write(
    (error instanceof Error ? error.message : "Operation failed") + "\n",
  );
  process.exitCode = 1;
}
