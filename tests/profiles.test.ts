import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { readProfiles } from "../src/profiles.ts";

const cli = fileURLToPath(new URL("../dist/cli.js", import.meta.url));
const run = (...args: string[]) =>
  spawnSync(process.execPath, [cli, ...args], { encoding: "utf8" });

await test("catalog names evidence and separates generation from controls and diagnostics", async () => {
  const catalog = await readProfiles();
  assert.equal(catalog.length, 8);
  assert.equal(catalog.filter((p) => !p.generation).length, 2);
  for (const profile of catalog) {
    assert.match(
      profile.id,
      /^(experimental-agent|historical|control|diagnostic)-/,
    );
    const info = run("info", "--profile", profile.id);
    assert.equal(info.status, 0, info.stderr);
    const value: unknown = JSON.parse(info.stdout);
    assert(
      typeof value === "object" &&
        value !== null &&
        "profile" in value &&
        "status" in value &&
        "cliGeneration" in value,
    );
    assert.equal(value.profile, profile.id);
    assert.equal(value.status, profile.status);
    assert.equal(value.cliGeneration, profile.generation);
  }
});

await test("diagnostic and control identities and aliases cannot produce a CLI secret", () => {
  for (const name of [
    "vi-short",
    "diagnostic-short-v1",
    "vi-ascii-native",
    "control-paired-native",
  ]) {
    const result = run("generate", "--profile", name, "--bits", "96", "--json");
    assert.equal(result.status, 1);
    assert.equal(result.stdout, "");
    assert.match(result.stderr, /unavailable for CLI generation/);
  }
});

await test("legacy alias resolves the same bytes and warns about its canonical evidence name", () => {
  const alias = run("info", "--profile", "vi-fused");
  const canonical = run("info", "--profile", "experimental-agent-vi-fused");
  assert.equal(alias.status, 0, alias.stderr);
  assert.equal(alias.stdout, canonical.stdout);
  assert.match(alias.stderr, /Deprecated profile alias vi-fused/);
  assert.equal(canonical.stderr, "");
});

await test("profile discovery and info never silently choose a historical default", () => {
  const missing = run("info");
  assert.equal(missing.status, 1);
  assert.equal(missing.stdout, "");
  assert.match(missing.stderr, /explicit --profile/);
  const discovery = run("profiles");
  assert.equal(discovery.status, 0, discovery.stderr);
  const value: unknown = JSON.parse(discovery.stdout);
  assert(Array.isArray(value));
  assert.equal(value.length, 8);
  assert.equal(run("profiles", "--profile", "vi").status, 1);
});
