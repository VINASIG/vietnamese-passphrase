#!/usr/bin/env node
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { generate, verifyWordlist } from "./index.ts";
import type { PhraseOptions } from "./index.ts";
import { location, readProfiles, record } from "./profiles.ts";
import type { Profile } from "./profiles.ts";
const entropyScope =
  "independent uniform draws from pinned unique tokens with injective encoding; not measured memorability or downstream security";

async function load(profile: Profile) {
  const path = location(profile);
  const metadata: unknown = JSON.parse(await readFile(path.manifest, "utf8"));
  const spec = record(record(record(metadata).profiles)[profile.dataProfile]);
  if (typeof spec.sha256 !== "string")
    throw new Error("Missing wordlist checksum");
  return verifyWordlist(await readFile(path.list), spec.sha256);
}

async function main(): Promise<void> {
  const [command, ...args] = process.argv.slice(2);
  if (command === undefined || command === "help" || command === "--help") {
    process.stdout.write(
      "Vietnamese Passphrase\n\nGenerate locally with an explicit profile and explicit bit target or word count\nExamples only: neither these profiles, their order, nor 80 bits is a recommendation.\n  vietphrase generate --profile experimental-agent-vi --bits 80\n  vietphrase generate --profile experimental-agent-ascii --bits 80\n\nInspect evidence and usage policy without generating a secret\n  vietphrase profiles\n  vietphrase info --profile experimental-agent-vi\n  vietphrase info --profile experimental-agent-ascii\n  vietphrase verify\n\nProfile names identify experimental, historical, control or diagnostic evidence.\ndiagnostic-short-v1 and control-paired-native are unavailable for CLI generation.\nOld data identifiers remain deprecated aliases with the same usage restrictions.\nNo vocabulary is a recommended universal default. Verification checks bytes and format.\nEntropy assumes independent uniform draws, not measured memorability or downstream security.\n",
    );
    return;
  }
  const profiles = await readProfiles();
  if (command === "profiles") {
    if (args.length !== 0)
      throw new Error("The profiles command takes no options");
    process.stdout.write(JSON.stringify(profiles, null, 2) + "\n");
    return;
  }
  if (!["generate", "info", "verify"].includes(command))
    throw new Error("Unknown command. Run vietphrase help");
  let selected: Profile | undefined;
  let requested: string | undefined;
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
      const profile = profiles.find(
        (p) => p.id === value || p.dataProfile === value,
      );
      if (profile === undefined)
        throw new Error("Choose a listed profile. Run vietphrase help");
      selected = profile;
      requested = value;
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
        profile.id +
          " INTEGRITY_PASS " +
          String(list.size) +
          " tokens (pinned bytes and format only) " +
          profile.status +
          "\n",
      );
    }
    return;
  }
  if (selected === undefined)
    throw new Error(
      "An explicit --profile is required. Run vietphrase profiles. There is no default vocabulary",
    );
  if (command === "generate" && !selected.generation)
    throw new Error(
      selected.id +
        " is unavailable for CLI generation. " +
        selected.limitation,
    );
  if (requested !== undefined && requested !== selected.id)
    process.stderr.write(
      "Deprecated profile alias " + requested + ". Use " + selected.id + ".\n",
    );
  const list = await load(selected);
  if (command === "info") {
    process.stdout.write(
      JSON.stringify(
        {
          profile: selected.id,
          dataProfile: selected.dataProfile,
          entries: list.size,
          bitsPerDraw: list.bitsPerDraw,
          listPath: fileURLToPath(location(selected).list),
          status: selected.status,
          purpose: selected.purpose,
          cliGeneration: selected.generation,
          limitation: selected.limitation,
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
  const options: PhraseOptions = {
    ...(bits === undefined ? {} : { bits }),
    ...(words === undefined ? {} : { words }),
    ...(separator === undefined ? {} : { separator }),
  };
  const result = generate(list, options);
  process.stderr.write(selected.status + ". " + selected.limitation + "\n");
  process.stdout.write(
    json
      ? JSON.stringify({
          profile: selected.id,
          dataProfile: selected.dataProfile,
          status: selected.status,
          limitation: selected.limitation,
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
