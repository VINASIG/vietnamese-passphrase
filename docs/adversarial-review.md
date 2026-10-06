# Adversarial vocabulary review

6 October 2026. The owner supplied adversarial reviewer feedback. Reviewer identity, independence and inspected revision are not established by that quotation. This document treats it as competing hypotheses, not an audit certificate. All follow-up execution and assessment is by an SI agent under the owner's project rule.

## Methodology findings

The released 3,057-entry size is a heuristic output, not a demonstrated optimum. The two Wiktionary editions overlap; wordfreq estimates and Tatoeba n-gram counts are proxies. Determinism preserves a choice but cannot justify it linguistically. The root problem was a selection pipeline with insufficient comparison of the vocabulary it produced. We now publish structural neighborhoods, external lexical attestation, an explicit agent content policy, attributable variant decisions and competing experimental profiles. Released data remains the baseline.

The [independent audit](../scripts/vocabulary_audit.py) reads list bytes without importing the selection implementation. Deletion signatures generate candidates; codepoint Levenshtein verifies every pair. An exhaustive small-space full-matrix oracle checks distance and neighborhood completeness. [Diagnostic datasets](research/adversarial/) retain full pairs and collision classes, not an overall quality score.

| Baseline   | Entries | Tokens with a distance-one neighbor | Tokens in ASCII collision classes | External native lexical attestation |
| ---------- | ------: | ----------------------------------: | --------------------------------: | ----------------------------------: |
| `vi`       |   3,057 |                               43.4% |                             30.1% |                               60.4% |
| `vi-short` |   1,293 |                               96.0% |                             69.6% |                               68.2% |

The native list has 4,472 distance-one pairs, 66,126 pairs at distance at most two, 327 ASCII collision classes involving 920 tokens, and a largest ASCII class of eleven. These are properties of the representation, not probabilities of human error. Shorter words save characters while increasing modeled neighbors. Content screening alone slightly increases the neighbor fraction, from 43.4% to 43.6%; it does not fix confusability.

The external source is [UD Vietnamese VTB](https://universaldependencies.org/treebanks/vi_vtb/index.html), a news treebank derived from VLSP. [Pinned original bytes and notices](../research/inputs/ud-vtb/) retain CC-BY-SA-4.0. The inspected revision has 3,323 sentence IDs and 58,069 token rows; only 1,120 rows supply text metadata, so that metadata count is not evidence of duplicate sentences. Matching uses normalized, lowercased segmented FORM fields. 1,845 native entries are attested. Unmatched entries are not thereby bad words. News, segmentation and corpus size bias coverage. This is a different source from Tatoeba, not proof of statistical independence or familiarity. ASCII and fused comparisons explicitly project the external representation and do not imply semantic equivalence.

The [180-configuration comparison and four ablations](research/adversarial/methodology.json) minimize expected codepoints and distance-one neighbor fraction and maximize external attestation fraction. No weights manufacture a winner. At illustrative 80 bits the original configuration is on this engineering Pareto frontier. At 96 and 128 bits, configuration 81 dominates it: both editions, at most three syllables, syllable Zipf at least 4.5, and five Tatoeba sentences; 2,060 entries. Expected lengths are 61.9 versus 62.4 and 82.9 versus 83.5 codepoints, neighbor fractions 43.2% versus 43.4%, and attestation 68.3% versus 60.4%. At 80 bits that alternative is longer, 54.9 versus 48.3. Frontier membership is not a memorability result or proof of closeness to an unknown human optimum. No universal default follows.

## Content, variation and representation

The [agent content policy](../research/content-policy.json) screens all baseline headwords for an experimental unattended general-display context. It records 84 context exclusions and seven variant consolidations. Every token has a [decision record](../research/experimental/2026-10-06.agent-1/decisions.jsonl). Unflagged means no conspicuous headword flag in this single agent pass, not certification of all senses or combinations. Source reduction does not retain every definition, so this is not an exhaustive sense review. Ordinary negative emotions remain. Neutral identity, gender, anatomy, medical vocabulary, religion and political affiliation are not intrinsically offensive.

All five reviewer pairs are present in the released list: `bác_sĩ/bác_sỹ`, `kĩ_năng/kỹ_năng`, `lí_do/lý_do`, `gởi/gửi` and `công_ti/công_ty`. The experimental profile chooses one named spelling in each documented family, also consolidating `kỉ_niệm/kỷ_niệm` and `cám_ơn/cảm_ơn`. These are agent-assessed profile conventions, not a universal spelling reform or rejection of regional legitimacy. Blanket i/y replacement would merge distinct items such as `tai/tay`, `dài/dày` and `vai/vay`. Stress-key matches are never automatic semantic aliases.

| Experimental profile | Entries | Delivered generator bits at illustrative 80-bit target | Expected codepoints | Distance-one neighbor fraction |
| -------------------- | ------: | -----------------------------------------------------: | ------------------: | -----------------------------: |
| `vi-display`         |   2,966 |                                                   80.7 |                48.1 |                          43.6% |
| `vi-fused`           |   2,966 |                                                   80.7 |                44.1 |                          44.2% |
| `vi-ascii-display`   |   2,389 |                                                   89.8 |                60.2 |                          46.1% |
| `vi-ascii-native`    |   2,389 |                                                   89.8 |                60.2 |                          28.9% |
| `vi-distinct`        |   2,045 |                                                   88.0 |                64.2 |                           0.0% |

All five are in [a separate experimental revision](../research/experimental/2026-10-06.agent-1/). None replaces the published lists. `vi-distinct` uses a deterministic greedy maximal independent set of the distance-one graph, not a proven maximum. Longer entries and an extra draw increase expected length. Distance-two, Telex and phonetic neighbors remain. It is not called error-proof or more secure for people.

`vi-fused` removes internal `_` before sampling. This is one-to-one on the exact native vocabulary, saves approximately four characters per seven-draw phrase, and still requires an outer delimiter. It loses displayed syllable boundaries and changes neighbors. No recall advantage has been observed. On the released ASCII vocabulary, dropping `_` creates three collision pairs, so applying it after generation would break the distribution. A future ASCII fused profile would need separate deduplication and evidence.

ASCII sampling uses distinct folded strings uniformly. Its paired native profile shares indices and publishes the representative of each class, selected by codepoint order without a familiarity claim. This isolates representation without comparing unequal vocabularies. Meanings still collapse; correct distribution does not repair semantic loss.

Diagnostics include tone-only groups, hypothetical i/y and onset-substitution groups, common four-character prefixes/suffixes, proper affix relations, coarse visual-mark groups, adjacent transpositions, QWERTY same-row substitutions and canonical Telex neighbors. Telex expands vowel shape keys and appends the tone key at syllable end; this covers one modeled input order, not an IME simulation or observed error rate. Stress keys are not a phonological analyzer. Actual homophone coverage, regional familiarity and font-dependent recognition remain unestablished. Variation exists within provinces as well as broad regions; [ViMD](https://arxiv.org/abs/2410.03458) is relevant primary evidence, not validation of our simplified keys. No profile is labelled Northern, Central or Southern without population evidence.

## Claims the critique overstated

The v0.1 documentation already called the product a research preview and stated that its sentence-ID holdout did not separate authors, templates or domains. It did not claim a Vietnamese standard or completed memory study. The holdout remains internal robustness. Existing tests included separate Python verification and cross-language vectors; the entire suite was not merely executing selection twice. Those checks still cannot validate the UX specification.

Corpus ranking selects variant representatives; runtime selection is uniform with replacement. Existing ASCII deduplication already occurs before sampling. No frequency weights, grammar filters, favorite-word selection or typo correction enter runtime generation.

The critique is right about presentation: broad `PASS` labels and entropy precision can imply vocabulary approval. CLI output now says `INTEGRITY_PASS` with its scope; generation requires an explicit profile. Human-facing model figures are rounded. Machine arithmetic retains precision and a scope statement. It describes independent uniform draws and injective encoding, not downstream distribution, user edits, recall or account security.

## Assurance and adoption

[Assurance](assurance.md) separates automated invariants, agent assessment, supplied critique, independent review, human validation, user testing and production evidence. Under the agent-only rule, human studies are not deliverables; their absence limits claims without blocking agent work. Simulations cannot become observations of people. The unanswered comparison with ordinary Vietnamese users remains unanswered.

[Downstream guidance](downstream.md) distinguishes data vendoring, adaptation, format conversion, binary embedding and LGPL JavaScript bundling. Commercial reuse is possible under the stated terms; attribution, adaptation and replaceability obligations remain. Existing upstream-derived data cannot simply become MIT-licensed. An independently sourced permissive vocabulary would be a separate future direction.

[Release verification](release-security.md) adds reproducible distribution comparison and keyless build provenance. Hashes need a trusted reference; attestations identify a workflow and source context, not vocabulary quality or trusted maintainer behavior. v0.1.0 is preserved and is not retrospectively described as attested.

Continue as an agent-assessed research and integration project with versioned contextual profiles, independent diagnostics and narrow claims. Do not promote a canonical standard or superiority over hand-curated or translated baselines without the needed evidence. The engineering results reveal tradeoffs and reproducible alternatives; they do not settle human memorability.
