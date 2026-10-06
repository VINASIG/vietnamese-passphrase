import assert from "node:assert/strict";
import { test } from "node:test";
import vectors from "./vectors.json" with { type: "json" };
import { Wordlist, decodePhrase, diceIndex, generate } from "../src/index.ts";
import { uniformIndex } from "../src/internal.ts";

await test("cross-language conformance vectors", (context) => {
  for (const [i, value] of vectors.uniform.inputs.entries()) {
    const expected = vectors.uniform.outputs[i];
    if (expected === null)
      assert.throws(
        () => uniformIndex(vectors.uniform.size, () => value),
        /rejection limit/,
      );
    else
      assert.equal(
        uniformIndex(vectors.uniform.size, () => value),
        expected,
      );
  }
  for (const [i, rolls] of vectors.dice.rolls.entries())
    assert.equal(diceIndex(vectors.dice.size, rolls), vectors.dice.outputs[i]);
  let cursor = 0;
  context.mock.method(
    globalThis.crypto,
    "getRandomValues",
    (array: Uint32Array) => {
      const value = vectors.phrase.indices[cursor++];
      assert.notEqual(value, undefined);
      array[0] = value ?? 0;
      return array;
    },
  );
  const list = new Wordlist(vectors.phrase.tokens);
  const result = generate(list, {
    words: vectors.phrase.indices.length,
    separator: vectors.phrase.separator,
  });
  assert.equal(result.passphrase, vectors.phrase.output);
  assert.equal(result.codepoints, vectors.phrase.codepoints);
  assert.equal(result.utf8Bytes, vectors.phrase.utf8Bytes);
  assert.deepEqual(decodePhrase(list, result.passphrase), [
    "bà",
    "cà_phê",
    "bà",
  ]);
});
