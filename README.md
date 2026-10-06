# Vietnamese Passphrase

Experimental Vietnamese passphrase vocabularies with attributable SI-agent decisions, implementation-independent diagnostics and a uniform reference generator. Reuse the UTF-8 lists and evidence, or integrate the dependency-free TypeScript library.

[Đọc bằng tiếng Việt](README.vi.md) · [Research and comparisons](docs/research.md) · [Security model](docs/security.md) · [Data specification](docs/specification.md)

## Current research preview

**[v0.2.5](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.2.5)** is the current agent-assessed research preview. [Release identity](release.json) pins the exact notes and preview channel. There is no stable release and no recommended universal profile. GitHub's stable latest-release endpoint does not select prereleases, so use this explicit version rather than a latest URL.

[Delivered artifact evidence](docs/publication-v0.2.5.json) records the exact source, matching notes, downloaded bytes, all six attestation verifications and actual runner images/toolchains. [Verification observations](docs/verification-v0.2.5.md) keep those results separate from vocabulary evidence. The prior [v0.2.4 delivery](docs/publication-v0.2.4.json) retains its original scope.

The owner requires SI-agent execution and assessment. One agent screened headwords. Human linguistic validation, Vietnamese recall and entry performance, an independent security audit and production assurance are not established. Agent decisions and automated checks have separate scopes. This project does not claim a Vietnamese passphrase standard or a best vocabulary.

Read the [methodology findings](docs/adversarial-review.md), [assurance boundary](docs/assurance.md), [publication semantics](docs/publication-semantics.md) and [downstream guide](docs/downstream.md). The [research roadmap](docs/research-roadmap.md) separates further automated research from claims requiring actual Vietnamese participants. Report vulnerabilities privately through [SECURITY.md](SECURITY.md).

## Current experimental catalog

Names identify evidence and intended usage. Transformation-only data IDs remain immutable inside the [experimental data revision](research/experimental/2026-10-06.agent-1/), with digests, decisions and full comparisons. They are deprecated CLI aliases, not recommendations. No profile below has measured human memorability or entry performance.

| Canonical profile              | Entries | Experiment and limitation                                                                             |
| ------------------------------ | ------: | ----------------------------------------------------------------------------------------------------- |
| `experimental-agent-vi`        |   2,966 | Agent context-screened native candidate. Headword screening does not cover all senses or combinations |
| `experimental-agent-vi-fused`  |   2,966 | Removes internal underscores before sampling. Saves characters but hides syllable boundaries          |
| `experimental-agent-ascii`     |   2,389 | Uniform distinct folded strings. Semantic distinctions remain lost                                    |
| `experimental-agent-distance1` |   2,045 | Greedy distance-one constrained subset. Longer phrases and other similarities remain                  |

`control-paired-native` has 2,389 native representatives matched to ASCII indices. It is a comparison control, with CLI generation disabled. Historical baseline names begin with `historical-`. The retired `diagnostic-short-v1` has about 96% distance-one neighborhood involvement and cannot generate through the current CLI or Python example. Its data remains available only as a diagnostic/reproduction artifact. See [historical and diagnostic baselines](docs/historical-baselines.md).

The [machine-readable catalog](research/profile-catalog.json) records evidence, purpose and generation policy for all eight profiles. Renaming does not change data bytes or entropy. The generic library accepts caller-supplied vocabularies and does not enforce the CLI policy. Downstream applications must choose and enforce their own evidence and usage requirements.

An internal syllable space is encoded as `_` except in the explicit fused experiment. Preserve the chosen profile's tokens and supported outer separator. Stripping accents after sampling, dropping delimiters, choosing favorite words or reordering output changes the assumptions. Source and filtering decisions determine list sizes, not a quota imposed by Diceware or BIP-39. See [implementation-independent diagnostics](docs/research/adversarial/) and [policy decisions](research/content-policy.json). The diagnostic code reads list bytes without importing the selection pipeline, but was authored within this project. It is not an independent third-party review.

## Run locally

Use Node 24.21.0 and npm 12.2.0. The package has no runtime dependencies and is not published to npm. Clone the source and build it.

The Unicode and ASCII commands below are parallel API examples only. Neither profile, their order, nor the illustrative 80-bit target is a recommendation. Choose a profile and target after reviewing its evidence and your application's constraints.

```sh
git clone https://github.com/VINASIG/vietnamese-passphrase.git
cd vietnamese-passphrase
npm ci --ignore-scripts
npm run build
node dist/cli.js verify
node dist/cli.js profiles
node dist/cli.js info --profile experimental-agent-vi
node dist/cli.js info --profile experimental-agent-ascii
node dist/cli.js generate --profile experimental-agent-vi --bits 80
node dist/cli.js generate --profile experimental-agent-ascii --bits 80 --json
```

The final two commands print a newly generated secret to standard output. The library does not upload it, persist it or copy it to a clipboard. Terminal history, process capture and your surrounding application are outside that property. Never use the public examples or test vectors as real passwords.

## Integrate the library

This integration example demonstrates digest verification and explicit planning. Its selected list and bit target are illustrative, with the same evidence limits as the CLI examples.

```ts
import { readFile } from "node:fs/promises";
import { generate, planPhrase, verifyWordlist } from "./dist/index.js";

const bytes = await readFile(
  "research/experimental/2026-10-06.agent-1/vi-display.txt",
);
// Pin a reviewed list digest in your application.
const list = await verifyWordlist(
  bytes,
  "a027da36027ead2da0e80133b3bce6edca28fef01fae867551647767cf79331e",
);
const plan = planPhrase(list, { bits: 80 });
const result = generate(list, { bits: 80 });
// Handle result.passphrase as a secret. Do not log it.
```

The same ES module uses Web Crypto in modern browsers. Serve your own reviewed copy of the library and data. `verifyWordlist` checks pinned bytes before decoding UTF-8. A hash downloaded from the same untrusted location as the list does not authenticate either one.

Call `planPhrase` to inspect entropy and worst-case length before requesting randomness. `generate` and `fromDice` accept `maxCodepoints` and `maxUtf8Bytes`. These limits apply to the entire possible output space. A configuration that could exceed a limit fails before sampling. It never retries until a shorter phrase appears.

```ts
const result = generate(list, {
  bits: 80,
  maxCodepoints: 64,
});
```

Select the vocabulary profile and the bit target or word count explicitly. CLI info and generation have no implicit profile. Generation prints evidence limitations to standard error. The number of draws is `ceil(target / log2(N))`. Repeats are allowed. Deterministic separators and underscores contribute zero entropy. See [the specification](docs/specification.md) for API contracts and [Python reuse](examples/generate.py) for a separate standard-library example using the same catalog policy.

## Use physical dice

The library exposes `planDice`, `diceIndex` and `fromDice` for an explicitly reviewed list. Non-power-of-six sizes are supported without cutting off words. Reject an entire rejected dice group and retry. Each accepted token receives the same number of groups, assuming fair independent dice. The checked-in [v0.1 dice tables](data/dice/) are historical reproduction data, including the retired diagnostic list, and are not the current quick start.

## Reproduce and inspect

```sh
python scripts/build_data.py --out output/rebuilt
python tests/data_test.py
python scripts/research.py
python tests/vocabulary_test.py
python scripts/vocabulary_audit.py
python scripts/experiment_profiles.py
python scripts/compare_methodology.py
python tests/publication_test.py
python scripts/release_metadata.py
npm run verify
```

Python 3.12.14 runs the data pipeline with only the standard library. Portable evidence is included in [data/inputs](data/inputs/). The [source lock](data/source-lock.json) records upstream hashes, revisions, licenses and attribution. [Selected-word provenance](data/provenance.jsonl) includes dictionary labels, syllable frequency estimates and public sentence IDs. [The complete decision ledger](data/audit/decisions.jsonl) explains all 66,145 candidate records. Reasons overlap and must not be added as mutually exclusive counts.

[Reproduction instructions](docs/reproducibility.md) distinguish rebuilding from the included portable evidence, verifying its reduction from original snapshots, and rerunning benchmarks. [Contribution rules](CONTRIBUTING.md) require traceable evidence and scoped agent assessment.

The [release procedure](docs/release-security.md) checks exact-tag notes, distribution bytes rebuilt on two recorded environments and build-origin attestations. Historical [v0.2.3 delivery evidence](docs/publication-v0.2.json) and [v0.1 originals](docs/historical-baselines.md) retain their original scope. Neither an archive signature nor a renamed profile establishes vocabulary quality.

## Licensing

Original library, CLI, build scripts, tests and executable examples use **LGPL-3.0-or-later**. Data and original documentation use **CC-BY-SA-4.0**, with retained upstream notices. The library license was selected for broad integration. These are separate scopes. Redistributing or adapting the lists requires preserving their attribution and applicable data terms.

Wiktionary contributors, Kaikki.org / Tatu Ylonen, Robyn Speer and Tatoeba contributors supply the source evidence. Tatoeba's original CC BY 2.0 France grant and contributor credits are retained. EFF and Orchard Street are benchmark references. Ho Ngoc Duc's wordlists and TZUR are measured references and are not incorporated into production data.

Read [LICENSES.md](LICENSES.md), [NOTICE.md](NOTICE.md) and the [license review](docs/license-review.md). VINASIG marks follow the separate [Brand Usage Policy](BRAND_POLICY.md). A generated secret does not acquire a software license merely because this generator produced it.
