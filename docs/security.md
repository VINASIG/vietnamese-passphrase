# Security model

This project supplies a public vocabulary and a reference random generator. The attacker is assumed to know the source code, lists, rules, separators and chosen profile. Keeping the list secret is not part of the model.

Entropy statements apply to independent uniform draws with replacement and an encoding that preserves the ordered tokens. They do not measure a user-invented phrase, a natural sentence, an LLM's output or a phrase modified after generation. A longer-looking string is not evidence of more randomness.

## Implemented controls

- A system cryptographic source with no weaker fallback.
- Integer rejection sampling for arbitrary list sizes.
- Deduplication of NFC spellings, selected tone-placement variants and ASCII collisions before sampling.
- Distinct internal and outer separators with exact decoding.
- Strict UTF-8, NFC and restricted-alphabet validation. Invisible and directional characters are rejected.
- A copied byte snapshot for hash-before-parse integrity checking.
- Explicit entropy target or draw count and bounded input size, draw count and rejection work.
- Optional worst-case length checks before sampling. No conditional length filtering or truncation.
- No runtime dependencies, network requests, telemetry, secret persistence or automatic clipboard operations in the reference library and CLI.

These controls are covered by implementation tests. Passing them is not an independent security audit. Development dependency audits are a separate check and do not prove runtime correctness.

## Operations that invalidate the simple entropy calculation

Selecting favorites, excluding repeats, sorting, rearranging, stripping accents after sampling, deleting separators, shortening words, taking initials, replacing words or retrying until a pleasant sentence appears changes the probability distribution or the encoding. Compute a new model before claiming the old bit count.

For the current `vi` list, stripping accents after uniform native sampling produces an ASCII class with 11 native preimages. Its probability is `11/3057`. Min-entropy per draw becomes `-log2(11/3057)`, about 8.1185 bits, instead of 11.5779. This is why `vi-ascii` is constructed and sampled separately. Shannon entropy and min-entropy are different quantities. We report the latter for the most likely transformed result.

Case conversion, compatibility normalization and receiving-server transformations also need review. If a server changes accepted Unicode strings into fewer distinct forms, the generated sample-space calculation no longer describes its stored passwords.

## Unicode and receiving systems

Unicode NFC combines canonically equivalent sequences. It does not remove accents, map `đ` to `d`, fix spelling or make different tone placements linguistically identical. NFKD has a specific role in BIP-39 seed derivation, which is outside this generator. [Unicode UAX #15](https://unicode.org/reports/tr15/) defines these normalization forms.

The final [NIST SP 800-63B-4 password guidance](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/) recommends NFC for Unicode password processing. Its requirements concern verifiers and authentication context. It does not establish an 80-bit passphrase target or a particular wordlist size. Codepoint limits and UTF-8 byte limits are different. Review the actual site's accepted characters, normalization, truncation and password storage behavior.

Use `planPhrase` to compare worst-case lengths and appropriate explicit targets. Fixed separators add no bits. Do not fit a receiving limit by silently cutting a phrase or regenerating until it happens to be short.

## Boundaries

This generator does not prevent phishing, malicious extensions, a compromised device, keylogging, clipboard monitoring, screen capture, endpoint leaks or password reuse. It does not implement authentication, password hashing, salt, a KDF, rate limiting, MFA or account recovery. The [Web Crypto specification](https://www.w3.org/TR/webcrypto/) supplies the random-source contract. Trust still depends on the executing platform.

The reference CLI prints a secret only for an explicit `generate` command. Do not capture that output in build logs or public reports. There is no API key or remote service. Package tools and research acquisition require network access, but ordinary generation and validation do not.

Public examples and conformance vectors are known fixtures. Never use them as real secrets. Independent cryptographic and linguistic review is welcome through the contribution process.
