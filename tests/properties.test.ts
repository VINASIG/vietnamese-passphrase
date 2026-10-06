import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import test from "node:test";
import {
  decodePhrase,
  fromDice,
  planPhrase,
  verifyWordlist,
  Wordlist,
} from "../src/index.ts";
import { uniformIndex } from "../src/internal.ts";

await test("BigInt oracle for uint32 rejection boundaries at every supported list size", () => {
  const range = 1n << 32n;
  for (let size = 2; size <= 65536; size++) {
    const n = BigInt(size);
    const accepted = (range / n) * n;
    for (const input of [0n, n - 1n, accepted - 1n]) {
      assert.equal(
        uniformIndex(size, () => Number(input)),
        Number(input % n),
      );
    }
    if (accepted < range) {
      let calls = 0;
      assert.equal(
        uniformIndex(size, () => Number(calls++ === 0 ? accepted : n - 1n)),
        size - 1,
      );
      assert.equal(calls, 2);
    }
  }
});

await test("exhaustive tuple encoding is injective and repeated draws remain possible", () => {
  const tokens = ["a", "aa", "bà", "ba", "bánh_mì", "cà_phê"];
  const list = new Wordlist(tokens);
  for (const separator of ["-", " ", ".", "/", ":", "+"]) {
    const outputs = new Set<string>();
    for (let a = 0; a < 6; a++)
      for (let b = 0; b < 6; b++)
        for (let c = 0; c < 6; c++) {
          const generated = fromDice(list, [a + 1, b + 1, c + 1], {
            words: 3,
            separator,
          });
          const expected = [tokens[a], tokens[b], tokens[c]];
          assert.deepEqual(
            decodePhrase(list, generated.passphrase, separator),
            expected,
          );
          assert.equal(generated.passphrase, expected.join(separator));
          outputs.add(generated.passphrase);
        }
    assert.equal(outputs.size, 216);
  }
});

await test("unexpected Unicode never silently expands the accepted vocabulary", async () => {
  const bad = [
    "b\u0301a",
    "ba\u200b",
    "\u202eba",
    "bа",
    "ｂａ",
    "ba\u00a0",
    "bá".normalize("NFD"),
    "b\u034fa",
    "\ud800",
    "ba\u0000",
  ];
  for (const token of bad) {
    assert.throws(() => new Wordlist(["mèo", token]));
    const bytes = new TextEncoder().encode(`mèo\n${token}\n`);
    const hash = createHash("sha256").update(bytes).digest("hex");
    await assert.rejects(verifyWordlist(bytes, hash));
  }
  const list = new Wordlist(["bán", "bàn", "ban"]);
  assert.equal(list.size, 3);
  assert.equal(planPhrase(list, { words: 2 }).entropyBits, 2 * Math.log2(3));
});
