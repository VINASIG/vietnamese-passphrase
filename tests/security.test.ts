import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { execFileSync, spawnSync } from "node:child_process";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import {
  Wordlist,
  decodePhrase,
  diceIndex,
  fromDice,
  generate,
  parseWordlist,
  planDice,
  planPhrase,
  verifyWordlist,
} from "../src/index.ts";
import { secureUint32, uniformIndex, UINT32_RANGE } from "../src/internal.ts";

await test("reject malformed Unicode, controls, invisible characters and duplicate tokens", () => {
  for (const value of [
    "á".normalize("NFD"),
    "Ba",
    "bà\u200b",
    "a\u202e",
    "а",
    "a b",
    "_a",
    "a_",
    "a__b",
    "",
    "a-b",
    "a\n",
    "a\u0000",
    "a".repeat(129),
  ]) {
    assert.throws(() => new Wordlist(["mèo", value]));
  }
  assert.throws(() => new Wordlist(["bà", "bà"]));
  assert.throws(() => new Wordlist(["ba"]));
  assert.throws(() => new Wordlist(Array.from({ length: 65537 }, () => "a")));
});

await test("copy and freeze tokens so callers cannot alter the sample space", () => {
  const tokens = ["bà", "ba"];
  const list = new Wordlist(tokens);
  tokens[0] = "mèo";
  assert.equal(list.at(0), "bà");
  assert(Object.isFrozen(list) && Object.isFrozen(list.tokens));
  for (const index of [-1, 2, 0.5, NaN, Infinity])
    assert.throws(() => list.at(index));
});

await test("enforce canonical wordlist wire format", () => {
  assert.equal(parseWordlist("bà\nba\n").size, 2);
  for (const text of [
    "bà\nba",
    "bà\r\nba\r\n",
    "\uFEFFbà\nba\n",
    "bà\n\nba\n",
    "bà\nba\n\n",
  ]) {
    assert.throws(() => parseWordlist(text));
  }
});

await test("verify bytes before parsing and detect corruption and invalid UTF-8", async () => {
  const bytes = new TextEncoder().encode("bà\nba\n");
  const hash = createHash("sha256").update(bytes).digest("hex");
  assert.equal((await verifyWordlist(bytes, hash)).size, 2);
  await assert.rejects(verifyWordlist(bytes, "0".repeat(64)), /checksum/);
  await assert.rejects(verifyWordlist(bytes, "../invalid"), /integrity/);
  const invalid = new Uint8Array([0xc0, 0xaf, 0x0a]);
  await assert.rejects(
    verifyWordlist(invalid, createHash("sha256").update(invalid).digest("hex")),
  );
  const promise = verifyWordlist(bytes, hash);
  bytes.fill(0);
  assert.equal((await promise).at(0), "bà");
});

await test("require an explicit entropy target or count and bound resource usage", () => {
  const list = new Wordlist(["ba", "bà", "bá"]);
  assert.throws(() => planPhrase(list, {}));
  assert.throws(() => planPhrase(list, { bits: 80, words: 7 }));
  for (const bits of [0, -1, NaN, Infinity, 65537])
    assert.throws(() => planPhrase(list, { bits }));
  for (const words of [0, -1, 0.5, NaN, Infinity, 4097])
    assert.throws(() => planPhrase(list, { words }));
  assert.throws(() => planPhrase(new Wordlist(["ba", "bà"]), { bits: 5000 }));
  const plan = planPhrase(list, { bits: 80 });
  assert.equal(plan.draws, 51);
  assert(plan.entropyBits >= 80 && (plan.draws - 1) * list.bitsPerDraw < 80);
});

await test("reject separators that would collapse or confuse token boundaries", () => {
  const list = new Wordlist(["a", "aa", "bánh_mì"]);
  for (const separator of ["", "_", "a", "💡", "--", "\n", "\u200b"])
    assert.throws(() => planPhrase(list, { words: 2, separator }));
  for (const separator of ["-", " ", ".", "/", ":", "+"]) {
    assert.deepEqual(
      decodePhrase(list, ["bánh_mì", "a", "a"].join(separator), separator),
      ["bánh_mì", "a", "a"],
    );
  }
  for (const value of ["bánh-mì-a", "A-aa", " a", "a-", "a--aa", "á"])
    assert.throws(() => decodePhrase(list, value));
});

await test("enforce optional length limits before sampling without bias or truncation", (context) => {
  context.mock.method(globalThis.crypto, "getRandomValues", () => {
    throw new Error("must not sample");
  });
  const list = new Wordlist(["bà", "bánh_mì"]);
  const plan = planPhrase(list, { words: 3 });
  assert.equal(plan.maxCodepoints, 23);
  assert.equal(plan.maxUtf8Bytes, 29);
  assert.throws(
    () => generate(list, { words: 3, maxUtf8Bytes: 28 }),
    /sample space/,
  );
  assert.throws(
    () => generate(list, { words: 3, maxCodepoints: 22 }),
    /sample space/,
  );
  for (const limit of [NaN, Infinity, -1, 0, 0.5])
    assert.throws(() => planPhrase(list, { words: 3, maxCodepoints: limit }));
  assert.equal(
    planPhrase(list, { words: 3, maxCodepoints: 23, maxUtf8Bytes: 29 }).draws,
    3,
  );
});

await test("rejection sampling preserves the incomplete uint32 tail", () => {
  let calls = 0;
  const result = uniformIndex(3057, () => {
    calls++;
    return calls === 1 ? UINT32_RANGE - 1 : 3058;
  });
  assert.equal(result, 1);
  assert.equal(calls, 2);
  assert.equal(
    uniformIndex(65536, () => UINT32_RANGE - 1),
    65535,
  );
  const limit = UINT32_RANGE - (UINT32_RANGE % 3057);
  assert.equal(
    uniformIndex(3057, () => limit - 1),
    3056,
  );
  let afterTail = false;
  assert.equal(
    uniformIndex(3057, () => {
      if (!afterTail) {
        afterTail = true;
        return limit;
      }
      return 0;
    }),
    0,
  );
  assert.throws(
    () => uniformIndex(3057, () => UINT32_RANGE - 1),
    /rejection limit/,
  );
  for (const value of [-1, 1.5, NaN, Infinity, UINT32_RANGE])
    assert.throws(() => uniformIndex(3, () => value), /random source/);
});

await test("secure generation allows repeats and counts UTF-8 bytes independently", (context) => {
  context.mock.method(
    globalThis.crypto,
    "getRandomValues",
    (array: Uint32Array) => {
      array.fill(0);
      return array;
    },
  );
  const list = new Wordlist(["bánh_mì", "cà_phê"]);
  const output = generate(list, { words: 3 });
  assert.equal(output.passphrase, "bánh_mì-bánh_mì-bánh_mì");
  assert.equal(output.entropyBits, 3);
  assert.equal(output.codepoints, 23);
  assert.equal(output.utf8Bytes, 29);
  assert(Object.isFrozen(output));
});

await test("fail closed when Web Crypto is absent or throws", () => {
  const module = new URL("../src/internal.ts", import.meta.url).href;
  const missing = spawnSync(
    process.execPath,
    [
      "--input-type=module",
      "-e",
      `Object.defineProperty(globalThis, 'crypto', {value: undefined}); const {secureUint32} = await import(${JSON.stringify(module)}); secureUint32();`,
    ],
    { encoding: "utf8" },
  );
  assert.notEqual(missing.status, 0);
  assert.match(missing.stderr, /secure random source/);
  assert.equal(missing.stdout, "");
});

await test("preserve random provider failures without a fallback", (context) => {
  context.mock.method(globalThis.crypto, "getRandomValues", () => {
    throw new Error("provider failure");
  });
  assert.throws(() => secureUint32(), /provider failure/);
});

await test("exhaustively verify fair dice mapping including non-power list lengths", () => {
  for (const size of [2, 3, 7, 1293, 2464, 3057]) {
    const plan = planDice(size);
    const counts = new Uint32Array(size);
    let rejected = 0;
    for (let value = 0; value < plan.range; value++) {
      let rest = value;
      const rolls = new Array<number>(plan.rollsPerGroup);
      for (let i = rolls.length - 1; i >= 0; i--) {
        rolls[i] = (rest % 6) + 1;
        rest = Math.floor(rest / 6);
      }
      const index = diceIndex(size, rolls);
      if (index === null) rejected++;
      else counts[index] = (counts[index] ?? 0) + 1;
    }
    assert.equal(rejected, plan.range - plan.acceptedRange);
    assert(counts.every((count) => count === plan.acceptedRange / size));
  }
});

await test("manual dice rejects incomplete input and consumes rejected groups", () => {
  const list = new Wordlist(["a", "b", "c", "d", "e", "f", "g"]);
  assert.deepEqual(fromDice(list, [6, 6, 1, 1, 1, 2], { words: 2 }), {
    passphrase: "a-b",
    draws: 2,
    entropyBits: 2 * Math.log2(7),
    codepoints: 3,
    utf8Bytes: 3,
    consumedRolls: 6,
    rejectedGroups: 1,
  });
  for (const rolls of [[], [1], [0, 1], [1, 7], [NaN, 1], [1.5, 1]])
    assert.throws(() => fromDice(list, rolls, { words: 2 }));
  assert.throws(() => diceIndex(7, [1]));
});

await test("load all actual profiles and verify encode/decode integration", async () => {
  for (const profile of ["vi", "vi-ascii", "vi-short"]) {
    const bytes = await readFile(
      new URL("../data/lists/" + profile + ".txt", import.meta.url),
    );
    const list = await verifyWordlist(
      bytes,
      createHash("sha256").update(bytes).digest("hex"),
    );
    const output = generate(list, { bits: 96 });
    assert(output.entropyBits >= 96);
    assert.equal(decodePhrase(list, output.passphrase).length, output.draws);
    assert(list.tokens.every((token) => token === token.normalize("NFC")));
    if (profile === "vi-ascii")
      assert(list.tokens.every((token) => /^[a-z]+(?:_[a-z]+)*$/.test(token)));
  }
});

await test("CLI validates explicit generation and reports no secret on errors", () => {
  const cli = fileURLToPath(new URL("../dist/cli.js", import.meta.url));
  const run = (args: readonly string[]) =>
    spawnSync(process.execPath, [cli, ...args], { encoding: "utf8" });
  for (const args of [
    ["generate"],
    ["generate", "--bits", "80"],
    ["generate", "--bits", "80", "--words", "7"],
    ["generate", "--bits", "Infinity"],
    ["generate", "--profile", "../../invalid", "--bits", "80"],
    ["generate", "--words", "0"],
    ["generate", "--bits", "80", "--bits", "81"],
    ["info", "--words", "3"],
    ["verify", "--profile", "vi"],
  ]) {
    const result = run(args);
    assert.equal(result.status, 1);
    assert.equal(result.stdout, "");
    assert(result.stderr.length > 0);
  }
  const checked = run(["verify"]);
  assert.equal(checked.status, 0, checked.stderr);
  assert.match(checked.stdout, /historical-vi-v1 INTEGRITY_PASS 3057 tokens/);
  assert.match(
    checked.stdout,
    /experimental-agent-vi-fused INTEGRITY_PASS 2966 tokens/,
  );
  const generated = run([
    "generate",
    "--profile",
    "experimental-agent-vi",
    "--bits",
    "80",
    "--json",
  ]);
  assert.equal(generated.status, 0, generated.stderr);
  const parsed: unknown = JSON.parse(generated.stdout);
  assert(
    typeof parsed === "object" &&
      parsed !== null &&
      "entropyBits" in parsed &&
      typeof parsed.entropyBits === "number" &&
      parsed.entropyBits >= 80,
  );
  assert.match(
    generated.stderr,
    /experimental-single-agent-headword-assessment/,
  );
  assert.equal(
    execFileSync(process.execPath, [cli, "help"], {
      encoding: "utf8",
    }).includes("explicit bit target"),
    true,
  );
});
