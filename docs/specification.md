# Data and generator specification

The data schema and encoding are versioned independently of software. This specification describes `schema 1` and data version `2026-10-06.1`.

## List bytes

Each `.txt` file is UTF-8 without a byte-order mark, with one token per LF line and a final LF. Tokens use lowercase ASCII letters, `đ`, Vietnamese precomposed vowels and single internal `_` characters. They are NFC. There are no digits, whitespace, controls, directional overrides, zero-width characters, punctuation inside syllables, empty tokens or duplicates. The list order is Unicode codepoint order, not locale-dependent dictionary collation.

In each token, `_` represents an original lexical space. Supported outer separators are `-`, space, `.`, `/`, `:` and `+`. They do not appear inside tokens. Nonempty separators preserve the sequence unambiguously even when one token is a prefix of another. The project does not claim that the vocabulary is uniquely decodable without separators, free of homophones, or identifiable by its first four letters.

`data/manifest.json` records entry counts, entropy per draw, codepoint and UTF-8 length statistics, list hashes, rules and validation limits. `data/checksums.json` covers all lists, dice tables, selected provenance, the complete decision ledger and generated metadata. The input manifest separately pins the portable source evidence.

`data/provenance.jsonl` contains one record for each `vi` token. It keeps the original spelling, source-edition facts, Zipf estimates per syllable, distinct Tatoeba sentence IDs, folded ASCII token, ASCII representative and all related native spellings. ASCII evidence groups can be recovered without inventing a reverse translation. `data/audit/decisions.jsonl` gives exclusion reasons for all candidate records. A record can have several reasons. The sum of reason counts is not the number of rejected candidates.

## Sampling

For a list of `N` unique tokens, independently sample with replacement. With `k` draws and injective formatting, every output sequence has probability `N^-k` and entropy `k log2(N)` bits. `Math.random`, timestamp seeds, seeded pseudo-random generators and popularity-weighted choices are not used.

The reference generator obtains a uint32 from Web Crypto `getRandomValues`. Let `R = 2^32` and `L = R - (R mod N)`. Reject `x >= L`. For accepted values, select `x mod N`. Each index has exactly `L/N` preimages. A failure or unavailable provider throws. After 128 rejected uint32 values in one draw, throw rather than substituting a source. Conditional on acceptance, the draw remains uniform. The limit bounds work and is not a randomness test.

No production API accepts an injected random function. The internal sampler is exposed only to source tests, not package exports. A compromised runtime can compromise Web Crypto and all secrets. This implementation cannot repair that trust boundary.

## Dice

For arbitrary `N`, take the smallest `r` with `6^r >= N`. Convert ordered rolls 1 through 6 to a zero-based base-six integer. With `L = 6^r - (6^r mod N)`, reject values at least `L`, otherwise return `value mod N`. Each accepted token has exactly `L/N` possible groups. Roll a new entire group after rejection. Never retain only favorable dice.

`data/dice/*.tsv` enumerates every group, with zero-based index and token, or `REJECT`. The library's independent tests exhaustively enumerate all groups for every current profile. A valid group can map to the same token as another valid group. This is intentional and uniform.

## API

`new Wordlist(tokens)` copies, validates and freezes a list of 2 to 65,536 tokens. Tokens are at most 128 codepoints. It rejects NFD input instead of silently normalizing custom lists. Normalize and deduplicate an imported list deliberately before constructing it. That transformation changes the vocabulary and its version.

`parseWordlist(text)` validates canonical line framing. `verifyWordlist(bytes, expectedSha256)` copies bytes, verifies a pinned SHA-256 using Web Crypto, decodes UTF-8 with fatal error handling and then validates tokens. The byte limit is 16 MiB. Copying closes the hash/parse mutation window.

`planPhrase(list, options)` requires exactly one of positive `bits` or integral `words`. It returns the draw count, entropy, separator and worst-case codepoint and UTF-8 lengths. One to 4,096 draws are supported. `generate` uses the same plan and returns `passphrase`, `draws`, `entropyBits`, `codepoints` and `utf8Bytes`.

`maxCodepoints` and `maxUtf8Bytes` are positive integer constraints on the **entire** possible output space. A request whose worst-case length exceeds either limit throws before sampling. They are not conditional filters on generated results. The result is never truncated.

`decodePhrase` performs exact membership and separator checks without accent folding, normalization, trimming or typo correction. `planDice`, `diceIndex` and `fromDice` implement physical dice mapping. `diceIndex` returns null for a rejected group. `fromDice` requires complete valid groups and reports consumed rolls and rejected groups. Unused complete groups do not contribute entropy to the result.

The public data is a vocabulary, not a BIP-39 index mapping, checksum scheme, KDF or mnemonic-to-seed definition. Never substitute it for a wallet's specified recovery wordlist.

## Stable revisions

Once a data version is publicly released, its token bytes and mappings remain immutable. Vocabulary changes need a new data version, new digests, regenerated evidence and a migration note. Pin a reviewed version or digest when an application depends on indices or recovery behavior. A checksum establishes byte integrity relative to a trusted digest, not linguistic correctness or authenticity of an untrusted manifest.
