export const UINT32_RANGE = 0x1_0000_0000;
export const MAX_DRAWS = 4096;
export const MAX_LIST_SIZE = 65536;
export const MAX_INPUT_BYTES = 16 * 1024 * 1024;
export const SEPARATORS = ["-", " ", ".", "/", ":", "+"] as const;

export function checkSize(size: number): void {
  if (!Number.isSafeInteger(size) || size < 2 || size > MAX_LIST_SIZE) {
    throw new RangeError("A wordlist needs 2 to 65536 unique tokens");
  }
}

export function checkSeparator(separator: string): void {
  if (!SEPARATORS.some((value) => value === separator)) {
    throw new RangeError(
      "Choose a supported separator that preserves word boundaries",
    );
  }
}

export function uniformIndex(size: number, next: () => number): number {
  checkSize(size);
  const limit = UINT32_RANGE - (UINT32_RANGE % size);
  for (let attempt = 0; attempt < 128; attempt++) {
    const value = next();
    if (!Number.isSafeInteger(value) || value < 0 || value >= UINT32_RANGE) {
      throw new Error("Invalid random source output");
    }
    if (value < limit) return value % size;
  }
  throw new Error("Random source exceeded the rejection limit");
}

export function secureUint32(): number {
  const provider = (globalThis as { crypto?: Crypto }).crypto;
  if (typeof provider?.getRandomValues !== "function") {
    throw new Error("A cryptographically secure random source is required");
  }
  const value = new Uint32Array(1);
  provider.getRandomValues(value);
  const result = value[0];
  if (result === undefined) throw new Error("Random source failed");
  return result;
}
