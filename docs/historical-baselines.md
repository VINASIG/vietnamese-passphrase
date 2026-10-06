# Historical and diagnostic baselines

These files are preserved v0.1 data revision 2026-10-06.1. They support reproducible comparisons and are not the current vocabulary recommendation. Their sizes are outputs of historical selection heuristics. Read the [current catalog](../research/profile-catalog.json) before choosing an experiment.

| Canonical catalog identity | Immutable data identity                | Entries | Role                                           |
| -------------------------- | -------------------------------------- | ------: | ---------------------------------------------- |
| `historical-vi-v1`         | [vi](../data/lists/vi.txt)             |   3,057 | Native heuristic research baseline             |
| `historical-ascii-v1`      | [vi-ascii](../data/lists/vi-ascii.txt) |   2,464 | Folded heuristic research baseline             |
| `diagnostic-short-v1`      | [vi-short](../data/lists/vi-short.txt) |   1,293 | Retired high-confusability diagnostic baseline |

About 96.0% of the short list's tokens have another token at NFC codepoint Levenshtein distance one. This is a structural count, not an observed human error probability or a cryptographic entropy loss by itself. Its earlier presentation as an ordinary shorter alternative overemphasized output length and underemphasized potential entry confusion. The current CLI and Python example reject generation from both `diagnostic-short-v1` and its `vi-short` alias before sampling. Integrity verification and `info` remain available.

The generic library still accepts any caller-reviewed wordlist. Raw historical data and dice tables remain readable for independent reproduction. The CLI restriction is a product usage policy, not a revocation of data access or proof that downstream applications enforce it. Applications vendoring old bytes must implement their own usage policy. This project does not recommend deploying the retired short profile.

The two other historical baselines remain available for explicit research generation with a historical-status warning. No implicit profile selects them. Native baseline neighborhood involvement is 43.4%. ASCII folding combines 920 native entries into 327 collision classes before the distinct folded vocabulary is sampled. Distribution correctness does not establish usability.

[v0.1.0](https://github.com/VINASIG/vietnamese-passphrase/releases/tag/v0.1.0) retains its integration package and original production-input archive unchanged. Its [publication record](publication-plan.json), [verification](verification.md) and old source documentation describe that historical delivery. Current publication and usage semantics supersede the old recommendations, not the old artifact bytes.
