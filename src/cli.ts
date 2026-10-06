#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { generate, verifyWordlist } from "./index.ts";
import type { PhraseOptions } from "./index.ts";

type Profile = "vi" | "vi-ascii" | "vi-short";
const profiles: readonly Profile[] = ["vi", "vi-ascii", "vi-short"];
const base = new URL("../data/", import.meta.url);

function record(value: unknown): Record<string, unknown> {
  if (typeof value !== "object" || value === null || Array.isArray(value))
    throw new Error("Invalid data manifest");
  return value as Record<string, unknown>;
}

async function load(profile: Profile) {
  const metadata: unknown = JSON.parse(
    await readFile(new URL("manifest.json", base), "utf8"),
  );
  const spec = record(record(record(metadata).profiles)[profile]);
  if (typeof spec.sha256 !== "string")
    throw new Error("Missing wordlist checksum");
  return verifyWordlist(
    await readFile(new URL("lists/" + profile + ".txt", base)),
    spec.sha256,
  );
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);
  if (command === undefined || command === "help" || command === "--help") {
    process.stdout.write(
      "Vietnamese Passphrase\n\nGenerate locally with an explicit bit target or word count\n  vietphrase generate --profile vi --bits 80\n  vietphrase generate --profile vi-ascii --words 8 --json\n\nInspect the wordlist without generating a secret\n  vietphrase info --profile vi\n  vietphrase verify\n\nProfiles are vi, vi-ascii and vi-short\nData is a research preview. Entropy assumes independent uniform draws.\n",
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
        throw new Error("Choose vi, vi-ascii or vi-short");
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
        profile + " PASS " + String(list.size) + " tokens\n",
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
          listPath: fileURLToPath(new URL("lists/" + selected + ".txt", base)),
          status: "research-preview",
        },
        null,
        2,
      ) + "\n",
    );
    return;
  }
  const options: PhraseOptions = {
    ...(bits === undefined ? {} : { bits }),
    ...(words === undefined ? {} : { words }),
    ...(separator === undefined ? {} : { separator }),
  };
  const result = generate(list, options);
  process.stdout.write(
    json
      ? JSON.stringify({ profile: selected, ...result }) + "\n"
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
