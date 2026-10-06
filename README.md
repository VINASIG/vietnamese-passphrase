# Vietnamese Passphrase

Vietnamese passphrase wordlists with source evidence, reproducible selection and a reference generator. Reuse the plain UTF-8 lists, inspect every inclusion and exclusion, or integrate the dependency-free TypeScript library.

[Đọc bằng tiếng Việt](README.vi.md) · [Research and comparisons](docs/research.md) · [Security model](docs/security.md) · [Data specification](docs/specification.md)

Version 0.1.0 is a **research preview**. Structural checks and implementation tests are available. Independent linguistic review, a Vietnamese memorability study and an independent security audit have not been performed. The project does not claim to be the most memorable wordlist or a wallet recovery format.

## Wordlists

Sizes result from documented source and filtering decisions. They are not quotas imposed by Diceware or BIP-39.

| Profile                             | Entries | Bits per independent uniform draw | Draws for at least 80 bits | Expected codepoints with `-` |
| ----------------------------------- | ------: | --------------------------------: | -------------------------: | ---------------------------: |
| [vi](data/lists/vi.txt)             |   3,057 |                           11.5779 |                          7 |                        48.29 |
| [vi-ascii](data/lists/vi-ascii.txt) |   2,464 |                           11.2668 |                          8 |                        60.44 |
| [vi-short](data/lists/vi-short.txt) |   1,293 |                           10.3365 |                          8 |                        34.75 |

`vi` keeps Vietnamese spelling and includes dictionary-attested words of one or two syllables. `vi-ascii` merges collisions **before** uniform sampling for systems that do not handle Vietnamese reliably. `vi-short` is a shorter single-syllable alternative. Expected length is not a maximum and is not evidence of easier memorization. An 80-bit target is an example, not a universal recommendation.

Internal syllable spaces become `_`, so `bánh mì` is encoded as `bánh_mì`. The outer separator is different, for example `-`. Preserve both. Removing separators, stripping accents after sampling, choosing favorite words or reordering the result changes the security assumptions.

## Run locally

Use Node 24.21.0 and npm 12.2.0. The package has no runtime dependencies and is not published to npm. Clone the source and build it.

```sh
git clone https://github.com/VINASIG/vietnamese-passphrase.git
cd vietnamese-passphrase
npm ci --ignore-scripts
npm run build
node dist/cli.js verify
node dist/cli.js info --profile vi
node dist/cli.js generate --profile vi --bits 80
node dist/cli.js generate --profile vi-ascii --words 8 --json
```

The final two commands print a newly generated secret to standard output. The library does not upload it, persist it or copy it to a clipboard. Terminal history, process capture and your surrounding application are outside that property. Never use the public examples or test vectors as real passwords.

## Integrate the library

```ts
import { readFile } from "node:fs/promises";
import { generate, planPhrase, verifyWordlist } from "./dist/index.js";

const bytes = await readFile("data/lists/vi.txt");
// Pin a reviewed list digest in your application.
const list = await verifyWordlist(
  bytes,
  "a7a8f17ddfffebbd3a15003e6f67fe360f5301814914753503735844b0b90240",
);
const plan = planPhrase(list, { bits: 80 });
const result = generate(list, { bits: 80 });
// Handle result.passphrase as a secret. Do not log it.
```

The same ES module uses Web Crypto in modern browsers. Serve your own reviewed copy of the library and data. `verifyWordlist` checks pinned bytes before decoding UTF-8. A hash downloaded from the same untrusted location as the list does not authenticate either one.

Call `planPhrase` to inspect entropy and worst-case length before requesting randomness. `generate` and `fromDice` accept `maxCodepoints` and `maxUtf8Bytes`. These limits apply to the entire possible output space. A configuration that could exceed a limit fails before sampling. It never retries until a shorter phrase appears.

```ts
const result = generate(shortList, {
  bits: 80,
  maxCodepoints: 64,
});
```

Select the bit target or word count explicitly. The number of draws is `ceil(target / log2(N))`. Repeats are allowed. Deterministic separators and underscores contribute zero entropy. See [the specification](docs/specification.md) for API contracts and [Python reuse](examples/generate.py) for a separate standard-library example.

## Use physical dice

The [dice tables](data/dice/) cover every possible group, including rejected groups. For `vi`, roll five fair six-sided dice in order and look up the five digits. If the row says `REJECT`, discard that entire group and roll five new dice. Otherwise record the full token. Repeat for the desired number of accepted draws. Join tokens with a supported outer separator.

For `vi-ascii`, use five dice per group. For `vi-short`, use four. Each accepted token has the same number of corresponding dice groups. Non-power-of-six list sizes are supported without cutting off words. Fair independent dice are an assumption. The library exposes `planDice`, `diceIndex` and `fromDice` for checking this mapping.

## Reproduce and inspect

```sh
python scripts/build_data.py --out output/rebuilt
python tests/data_test.py
python scripts/research.py
npm run verify
```

Python 3.12.14 runs the data pipeline with only the standard library. Portable evidence is included in [data/inputs](data/inputs/). The [source lock](data/source-lock.json) records upstream hashes, revisions, licenses and attribution. [Selected-word provenance](data/provenance.jsonl) includes dictionary labels, syllable frequency estimates and public sentence IDs. [The complete decision ledger](data/audit/decisions.jsonl) explains all 66,145 candidate records. Reasons overlap and must not be added as mutually exclusive counts.

[Reproduction instructions](docs/reproducibility.md) distinguish rebuilding from the included portable evidence, verifying its reduction from original snapshots, and rerunning benchmarks. [Contribution rules](CONTRIBUTING.md) require traceable evidence and separate linguistic review.

## Licensing

Original library, CLI, build scripts, tests and executable examples use **LGPL-3.0-or-later**. Data and original documentation use **CC-BY-SA-4.0**, with retained upstream notices. The library license was selected for broad integration. These are separate scopes. Redistributing or adapting the lists requires preserving their attribution and applicable data terms.

Wiktionary contributors, Kaikki.org / Tatu Ylonen, Robyn Speer and Tatoeba contributors supply the source evidence. Tatoeba's original CC BY 2.0 France grant and contributor credits are retained. EFF and Orchard Street are benchmark references. Ho Ngoc Duc's wordlists and TZUR are measured references and are not incorporated into production data.

Read [LICENSES.md](LICENSES.md), [NOTICE.md](NOTICE.md) and the [license review](docs/license-review.md). VINASIG marks follow the separate [Brand Usage Policy](BRAND_POLICY.md). A generated secret does not acquire a software license merely because this generator produced it.
