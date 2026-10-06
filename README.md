# Vietnamese Passphrase

Vietnamese passphrase wordlists with source evidence, reproducible selection and a reference generator. Reuse the plain UTF-8 lists, inspect every inclusion and exclusion, or integrate the dependency-free TypeScript library.

[Đọc bằng tiếng Việt](README.vi.md) · [Research and comparisons](docs/research.md) · [Security model](docs/security.md) · [Data specification](docs/specification.md)

Version 0.2.0 is an **agent-assessed research preview**. The owner requires SI-agent execution and assessment. Human linguistic validation, a Vietnamese memorability study, an independent security audit and production assurance are not established. Agent decisions and automated checks have separate scopes. This project does not claim a Vietnamese passphrase standard or a best vocabulary.

Read the [adversarial findings and methodology changes](docs/adversarial-review.md), [assurance boundary](docs/assurance.md) and [downstream redistribution guide](docs/downstream.md). The three v0.1 lists below are immutable historical baselines; their sizes are heuristic outputs rather than proven optima. The [v0.2 release procedure](docs/release-security.md) compares distribution bytes across environments and verifies build-origin attestations separately from vocabulary quality.

The [v0.1.0 prerelease](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.1.0) supplies a local integration package, preserved original production inputs and SHA-256 checksums. The [publication record](docs/publication-plan.json) identifies the source revision, downloaded asset verification and related public listings.

## Wordlists

Sizes result from documented source and filtering decisions. They are not quotas imposed by Diceware or BIP-39.

| Profile                             | Entries | Bits per independent uniform draw | Draws for at least 80 bits | Expected codepoints with `-` |
| ----------------------------------- | ------: | --------------------------------: | -------------------------: | ---------------------------: |
| [vi](data/lists/vi.txt)             |   3,057 |                              11.6 |                          7 |                         48.3 |
| [vi-ascii](data/lists/vi-ascii.txt) |   2,464 |                              11.3 |                          8 |                         60.4 |
| [vi-short](data/lists/vi-short.txt) |   1,293 |                              10.3 |                          8 |                         34.7 |

`vi` keeps Vietnamese spelling and includes dictionary-attested words of one or two syllables. `vi-ascii` merges collisions **before** uniform sampling for systems that do not handle Vietnamese reliably. `vi-short` is a shorter single-syllable alternative. Expected length is not a maximum and is not evidence of easier memorization. An 80-bit target is an example, not a universal recommendation.

Internal syllable spaces become `_`, so `bánh mì` is encoded as `bánh_mì`. The outer separator is different, for example `-`. Preserve both. Removing separators, stripping accents after sampling, choosing favorite words or reordering the result changes the security assumptions.

## Experimental contextual profiles

The [separate experimental revision](research/experimental/2026-10-06.agent-1/) adds five alternatives, with digests, full diagnostics, agent decisions and ASCII/native index pairs. No profile is a recommended universal default.

| Profile            | Entries | Purpose and tradeoff                                                                                                     |
| ------------------ | ------: | ------------------------------------------------------------------------------------------------------------------------ |
| `vi-display`       |   2,966 | Agent headword context screening and seven explicit variant consolidations; unflagged does not mean harmless             |
| `vi-fused`         |   2,966 | Same native vocabulary with internal underscores removed before sampling; saves characters but hides syllable boundaries |
| `vi-ascii-display` |   2,389 | Distinct folded strings sampled uniformly; meaning loss remains                                                          |
| `vi-ascii-native`  |   2,389 | Native representatives paired with identical ASCII indices for representation comparisons                                |
| `vi-distinct`      |   2,045 | Greedy subset with no NFC distance-one neighbors; longer phrases and other similarity risks remain                       |

The native baseline has 43.4% of tokens with a distance-one neighbor; the short baseline has 96.0%. These are structural counts, not human mistake rates. A pinned external news corpus attests 60.4% of native baseline tokens; it is not a familiarity score. See [independent diagnostics](docs/research/adversarial/) and [policy decisions](research/content-policy.json).

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

Select the vocabulary profile and the bit target or word count explicitly. CLI generation has no implicit profile in v0.2.0. The number of draws is `ceil(target / log2(N))`. Repeats are allowed. Deterministic separators and underscores contribute zero entropy. See [the specification](docs/specification.md) for API contracts and [Python reuse](examples/generate.py) for a separate standard-library example.

## Use physical dice

The [dice tables](data/dice/) cover every possible group, including rejected groups. For `vi`, roll five fair six-sided dice in order and look up the five digits. If the row says `REJECT`, discard that entire group and roll five new dice. Otherwise record the full token. Repeat for the desired number of accepted draws. Join tokens with a supported outer separator.

For `vi-ascii`, use five dice per group. For `vi-short`, use four. Each accepted token has the same number of corresponding dice groups. Non-power-of-six list sizes are supported without cutting off words. Fair independent dice are an assumption. The library exposes `planDice`, `diceIndex` and `fromDice` for checking this mapping.

## Reproduce and inspect

```sh
python scripts/build_data.py --out output/rebuilt
python tests/data_test.py
python scripts/research.py
python tests/vocabulary_test.py
python scripts/vocabulary_audit.py
python scripts/experiment_profiles.py
python scripts/compare_methodology.py
npm run verify
```

Python 3.12.14 runs the data pipeline with only the standard library. Portable evidence is included in [data/inputs](data/inputs/). The [source lock](data/source-lock.json) records upstream hashes, revisions, licenses and attribution. [Selected-word provenance](data/provenance.jsonl) includes dictionary labels, syllable frequency estimates and public sentence IDs. [The complete decision ledger](data/audit/decisions.jsonl) explains all 66,145 candidate records. Reasons overlap and must not be added as mutually exclusive counts.

[Reproduction instructions](docs/reproducibility.md) distinguish rebuilding from the included portable evidence, verifying its reduction from original snapshots, and rerunning benchmarks. [Contribution rules](CONTRIBUTING.md) require traceable evidence and scoped agent assessment.

## Licensing

Original library, CLI, build scripts, tests and executable examples use **LGPL-3.0-or-later**. Data and original documentation use **CC-BY-SA-4.0**, with retained upstream notices. The library license was selected for broad integration. These are separate scopes. Redistributing or adapting the lists requires preserving their attribution and applicable data terms.

Wiktionary contributors, Kaikki.org / Tatu Ylonen, Robyn Speer and Tatoeba contributors supply the source evidence. Tatoeba's original CC BY 2.0 France grant and contributor credits are retained. EFF and Orchard Street are benchmark references. Ho Ngoc Duc's wordlists and TZUR are measured references and are not incorporated into production data.

Read [LICENSES.md](LICENSES.md), [NOTICE.md](NOTICE.md) and the [license review](docs/license-review.md). VINASIG marks follow the separate [Brand Usage Policy](BRAND_POLICY.md). A generated secret does not acquire a software license merely because this generator produced it.
