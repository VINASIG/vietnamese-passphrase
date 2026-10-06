import {
  checkSeparator,
  checkSize,
  MAX_DRAWS,
  MAX_INPUT_BYTES,
  secureUint32,
  uniformIndex,
} from "./internal.ts";

const letters = new Set("abcdefghijklmnopqrstuvwxyzđ");
for (const vowel of "aăâeêioôơuưy") {
  for (const tone of ["", "\u0300", "\u0301", "\u0303", "\u0309", "\u0323"]) {
    letters.add((vowel + tone).normalize("NFC"));
  }
}

export class Wordlist {
  readonly #tokens: readonly string[];
  readonly #membership: ReadonlySet<string>;
  readonly maxTokenCodepoints: number;
  readonly maxTokenUtf8Bytes: number;

  constructor(tokens: readonly string[]) {
    checkSize(tokens.length);
    const values = Array.from(tokens);
    for (const value of values) {
      if (
        typeof value !== "string" ||
        value.length === 0 ||
        value.length > 128 ||
        value !== value.normalize("NFC") ||
        value.startsWith("_") ||
        value.endsWith("_") ||
        value.includes("__") ||
        !Array.from(value).every((char) => letters.has(char) || char === "_")
      ) {
        throw new TypeError(
          "Tokens must be lowercase NFC Vietnamese letters with single internal underscores",
        );
      }
    }
    const membership = new Set(values);
    if (membership.size !== values.length)
      throw new TypeError("Duplicate wordlist token");
    this.#tokens = Object.freeze(values);
    this.#membership = membership;
    this.maxTokenCodepoints = values.reduce(
      (maximum, value) => Math.max(maximum, Array.from(value).length),
      0,
    );
    const encoder = new TextEncoder();
    this.maxTokenUtf8Bytes = values.reduce(
      (maximum, value) => Math.max(maximum, encoder.encode(value).length),
      0,
    );
    Object.freeze(this);
  }

  get size(): number {
    return this.#tokens.length;
  }
  get bitsPerDraw(): number {
    return Math.log2(this.size);
  }
  get tokens(): readonly string[] {
    return this.#tokens;
  }
  has(token: string): boolean {
    return this.#membership.has(token);
  }
  at(index: number): string {
    if (!Number.isSafeInteger(index) || index < 0 || index >= this.size)
      throw new RangeError("Invalid word index");
    const token = this.#tokens[index];
    if (token === undefined) throw new RangeError("Invalid word index");
    return token;
  }
}

export function parseWordlist(text: string): Wordlist {
  if (
    new TextEncoder().encode(text).length > MAX_INPUT_BYTES ||
    !text.endsWith("\n") ||
    text.includes("\r") ||
    text.startsWith("\uFEFF")
  ) {
    throw new TypeError(
      "Use a UTF-8 wordlist with LF lines and a final newline",
    );
  }
  return new Wordlist(text.slice(0, -1).split("\n"));
}

export async function verifyWordlist(
  bytes: Uint8Array,
  expectedSha256: string,
): Promise<Wordlist> {
  if (
    bytes.byteLength > MAX_INPUT_BYTES ||
    !/^[a-f0-9]{64}$/.test(expectedSha256)
  )
    throw new TypeError("Invalid wordlist integrity input");
  const snapshot = Uint8Array.from(bytes);
  const digest = await globalThis.crypto.subtle.digest("SHA-256", snapshot);
  const actual = Array.from(new Uint8Array(digest), (value) =>
    value.toString(16).padStart(2, "0"),
  ).join("");
  if (actual !== expectedSha256) throw new Error("Wordlist checksum mismatch");
  return parseWordlist(
    new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(snapshot),
  );
}

export type PhraseOptions = {
  readonly bits?: number;
  readonly words?: number;
  readonly separator?: string;
  readonly maxCodepoints?: number;
  readonly maxUtf8Bytes?: number;
};

export type Phrase = {
  readonly passphrase: string;
  readonly draws: number;
  readonly entropyBits: number;
  readonly codepoints: number;
  readonly utf8Bytes: number;
};

export function planPhrase(
  list: Wordlist,
  options: PhraseOptions,
): {
  readonly draws: number;
  readonly entropyBits: number;
  readonly separator: string;
  readonly maxCodepoints: number;
  readonly maxUtf8Bytes: number;
} {
  const input: unknown = options;
  if (
    !(list instanceof Wordlist) ||
    input === null ||
    typeof input !== "object" ||
    (options.bits === undefined) === (options.words === undefined)
  ) {
    throw new TypeError("Choose exactly one of a bit target or a word count");
  }
  const separator = options.separator ?? "-";
  checkSeparator(separator);
  let draws: number;
  if (options.bits !== undefined) {
    if (
      !Number.isFinite(options.bits) ||
      options.bits <= 0 ||
      options.bits > 65536
    )
      throw new RangeError("Invalid bit target");
    draws = Math.ceil(options.bits / list.bitsPerDraw);
  } else {
    const words = options.words;
    if (words === undefined || !Number.isSafeInteger(words))
      throw new RangeError("Invalid word count");
    draws = words;
  }
  if (draws < 1 || draws > MAX_DRAWS)
    throw new RangeError("Choose 1 to 4096 draws");
  const maxCodepoints = draws * list.maxTokenCodepoints + draws - 1;
  const maxUtf8Bytes = draws * list.maxTokenUtf8Bytes + draws - 1;
  for (const [limit, maximum] of [
    [options.maxCodepoints, maxCodepoints],
    [options.maxUtf8Bytes, maxUtf8Bytes],
  ] as const) {
    if (
      limit !== undefined &&
      (!Number.isSafeInteger(limit) || limit < 1 || maximum > limit)
    )
      throw new RangeError(
        "The complete sample space exceeds the requested length limit",
      );
  }
  return Object.freeze({
    draws,
    entropyBits: draws * list.bitsPerDraw,
    separator,
    maxCodepoints,
    maxUtf8Bytes,
  });
}

function phrase(
  list: Wordlist,
  indices: readonly number[],
  separator: string,
): Phrase {
  const passphrase = indices.map((index) => list.at(index)).join(separator);
  return Object.freeze({
    passphrase,
    draws: indices.length,
    entropyBits: indices.length * list.bitsPerDraw,
    codepoints: Array.from(passphrase).length,
    utf8Bytes: new TextEncoder().encode(passphrase).length,
  });
}

export function generate(list: Wordlist, options: PhraseOptions): Phrase {
  const plan = planPhrase(list, options);
  const indices = Array.from({ length: plan.draws }, () =>
    uniformIndex(list.size, secureUint32),
  );
  return phrase(list, indices, plan.separator);
}

export function decodePhrase(
  list: Wordlist,
  passphrase: string,
  separator = "-",
): readonly string[] {
  checkSeparator(separator);
  if (passphrase.length > 1024 * 1024)
    throw new RangeError("Passphrase exceeds the supported length");
  const tokens = passphrase.split(separator);
  if (tokens.length > MAX_DRAWS || tokens.some((token) => !list.has(token)))
    throw new TypeError(
      "Passphrase does not match this wordlist and separator",
    );
  return Object.freeze(tokens);
}

export type DicePlan = {
  readonly rollsPerGroup: number;
  readonly range: number;
  readonly acceptedRange: number;
  readonly acceptance: number;
};

export function planDice(size: number): DicePlan {
  checkSize(size);
  let rollsPerGroup = 1;
  let range = 6;
  while (range < size) {
    rollsPerGroup++;
    range *= 6;
  }
  const acceptedRange = range - (range % size);
  return Object.freeze({
    rollsPerGroup,
    range,
    acceptedRange,
    acceptance: acceptedRange / range,
  });
}

export function diceIndex(
  size: number,
  rolls: readonly number[],
): number | null {
  const plan = planDice(size);
  if (rolls.length !== plan.rollsPerGroup)
    throw new RangeError("Incorrect dice group length");
  let value = 0;
  for (const roll of rolls) {
    if (!Number.isSafeInteger(roll) || roll < 1 || roll > 6)
      throw new RangeError("Each die must have a value from 1 to 6");
    value = value * 6 + roll - 1;
  }
  return value < plan.acceptedRange ? value % size : null;
}

export type DicePhrase = Phrase & {
  readonly consumedRolls: number;
  readonly rejectedGroups: number;
};

export function fromDice(
  list: Wordlist,
  rolls: readonly number[],
  options: PhraseOptions,
): DicePhrase {
  const plan = planPhrase(list, options);
  const dice = planDice(list.size);
  if (
    rolls.length > MAX_DRAWS * dice.rollsPerGroup * 128 ||
    rolls.length % dice.rollsPerGroup !== 0 ||
    rolls.some((roll) => !Number.isSafeInteger(roll) || roll < 1 || roll > 6)
  )
    throw new RangeError("Supply complete groups of valid dice rolls");
  const indices: number[] = [];
  let consumedRolls = 0;
  let rejectedGroups = 0;
  while (indices.length < plan.draws) {
    if (consumedRolls >= rolls.length)
      throw new RangeError("More complete dice groups are needed");
    const index = diceIndex(
      list.size,
      rolls.slice(consumedRolls, consumedRolls + dice.rollsPerGroup),
    );
    consumedRolls += dice.rollsPerGroup;
    if (index === null) rejectedGroups++;
    else indices.push(index);
  }
  return Object.freeze({
    ...phrase(list, indices, plan.separator),
    consumedRolls,
    rejectedGroups,
  });
}
