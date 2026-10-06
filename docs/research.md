# Research, measurements and selection decision

Research date 6 October 2026. This report separates observations, mathematical consequences and design choices. Measured data is supplied alongside executable reproduction scripts. No user passwords were collected.

## Decision

Develop a data-first project with a native vocabulary, a separately sampled ASCII vocabulary and a shorter alternative. Publish source evidence, exclusion decisions, versioned token bytes and reference implementations. Use public dictionaries as lexical evidence, frequency data only as a syllable familiarity proxy, and exact sentence occurrences as an additional constraint. Do not translate an English Diceware list into the production vocabulary.

The current evidence supports this architecture better than a single arbitrary-sized file or a sentence-generating application. It does **not** establish a globally best Vietnamese vocabulary or prove memorability. A browser interface can consume the library later without becoming the definition of the data.

## Existing work

| Work                                                                          | Observed purpose and size                                         | Useful properties                                                | Difference from this project                                                                                                           |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| [Original Diceware](https://theworld.com/~reinhold/diceware.html)             | Physical dice passphrases, many language lists                    | Explicit uniform selection by ordered rolls                      | List licenses and linguistic selection vary by language                                                                                |
| [EFF](https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases) | 7,776 large entries, two 1,296-entry alternatives                 | Studies word length, recognition and typo-related tradeoffs      | English vocabulary and dice-friendly sizes are not Vietnamese requirements                                                             |
| [Orchard Street](https://github.com/sts10/orchard-street-wordlists)           | 8,192 medium and 17,576 long entries                              | Multiple sizes and verified unique decodability                  | An English selection objective. Its separator-free property cannot be assumed for another language                                     |
| [Ho Ngoc Duc / duyet](https://github.com/duyet/vietnamese-wordlist)           | Four Vietnamese dictionary lists                                  | Broad lexical coverage                                           | Sorted lexical lists, not measured frequency rankings or a passphrase-specific pipeline. GPL version 2 source excluded from production |
| [osem23 / TZUR](https://github.com/osem23/bip39-wordlists-tzur)               | 2,048 Vietnamese display entries paired to English BIP-39 indices | Published mapping, structural validation and translation reports | Wallet display/recovery purpose. Vietnamese native-speaker review is pending in the examined README                                    |

Repository searches for Vietnamese Diceware and passphrases and searches for Vietnamese wordlists found the sources above. This is a bounded discovery result, not proof that no other repository exists. All comparison sources are pinned in [source-lock.json](../data/source-lock.json). A competitor's limitations do not prove this project's linguistic quality.

TZUR's Vietnamese list has 2,048 distinct NFC and NFKD entries, 1,938 distinct accent-folded strings, a largest ASCII collision class of four and 425 excess entries sharing a four-codepoint prefix. These are local measurements, not allegations of wallet defects. Upstream documents prefix limitations and keeps derivation on its specified English form. After removing spaces from eligible dictionary headwords to match TZUR's concatenated encoding, 1,665 entries match. Unmatched entries are not automatically wrong translations. The purpose, spelling representation and selection rules differ. See [baselines.json](research/baselines.json).

[BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) specifies entropy/checksum encoding into 2,048 indices and NFKD for derivation. It is not a general requirement to make every passphrase list 2,048 entries. This project's lists define no wallet seed format.

## Source comparison

| Source                                                                                         | Data actually inspected                                                      | Use                                                        | Limits                                                                                           |
| ---------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| English Wiktionary through [Kaikki](https://kaikki.org/dictionary/Vietnamese/index.html)       | 51,896 Vietnamese records, 44,594 lowercase NFC forms                        | Lexical spelling, POS and usage labels                     | Community content, mixed senses and a deprecated postprocessed endpoint                          |
| Vietnamese Wiktionary through [Kaikki raw exports](https://kaikki.org/dictionary/rawdata.html) | 44,564 Vietnamese records out of 421,406 records, 41,277 lowercase NFC forms | Additional lexical evidence                                | Overlaps with English edition. Cross-edition presence is not independent validation              |
| [wordfreq](https://github.com/rspeer/wordfreq)                                                 | 10,719 Vietnamese entries, all without spaces                                | Minimum Zipf estimate across a candidate's syllables       | Estimates mainly reflect usage through about 2021. They are not direct compound-word frequencies |
| [Tatoeba](https://tatoeba.org/en/downloads)                                                    | 33,218 rows, 33,210 distinct lowercase NFC sentences                         | Exact contiguous one-, two- and three-syllable occurrences | Small, translation-oriented corpus. Repeated templates and homonyms can affect counts            |
| Leipzig Vietnamese corpora                                                                     | Download and usage pages requested                                           | Candidate alternative                                      | Access was blocked by an anti-abuse challenge. No corpus bytes were measured or included         |

The dictionary union has 66,145 normalized candidate records. The portable source reduction retains lexical facts and labels, not definitions, images or audio. Tatoeba sentence IDs and contributor credits identify evidence without bundling full sentences. Counts use distinct normalized sentence texts, not repeated appearances in the same sentence. Matching never crosses punctuation. Exact n-grams are not a full Vietnamese word segmentation algorithm.

Vietnamese written spaces separate syllables as well as words. [Vietnamese word-segmentation research](https://aclanthology.org/L18-1410/) explains why simply splitting on whitespace cannot define a lexical wordlist. `bánh mì` remains one candidate here, encoded as `bánh_mì`.

## Alternative constructions tested

The [sensitivity experiment](research/sensitivity.json) evaluates 180 combinations of source coverage, one to three syllables, minimum syllable Zipf 3.0 to 5.0 and one to twenty corpus sentences. Each combination uses the same structural and usage-label filters. Counts are taken after orthographic variant merging. No target size is imposed.

For the two-edition, two-syllable, minimum Zipf 4.0 condition, the following values illustrate the tradeoff.

| Minimum distinct sentences | Entries | Bits per draw | Expected codepoints at an 80-bit target |
| -------------------------: | ------: | ------------: | --------------------------------------: |
|                          1 |   5,018 |       12.2929 |                                   52.26 |
|                          2 |   3,704 |       11.8549 |                                   49.84 |
|                          3 |   3,057 |       11.5779 |                                   48.29 |
|                          5 |   2,310 |       11.1737 |                                   52.94 |
|                         10 |   1,546 |       10.5943 |                                   49.54 |
|                         20 |     970 |        9.9218 |                                   52.76 |

Three distinct sentences provide more than singleton evidence while retaining enough entries for seven draws at this illustrative target. This is a transparent heuristic, not a statistically optimized threshold. Allowing three syllables adds only 42 entries in this condition and increases expected length. Restricting to a single syllable gives the shorter profile, but individual short syllables can be less concrete and have more near spellings. Human testing is needed to assess that cost.

The production frequency threshold filters each syllable separately. It never presents the minimum score as the frequency of the entire word. Source agreement and corpus presence are constraints used for selection, so success on them is not a separate validation result. The report also includes a deterministic sentence holdout experiment that selects on an 80% ID partition and measures occurrences in the held-out 20%. It does not separate authors, templates or domains and is not an external corpus.

A direct translation pilot matched exact single-English-word dictionary glosses, chose the shortest Vietnamese lexical candidate and covered **1,090 of 7,776** EFF entries. It produced **1,032** distinct Vietnamese strings. This is partial coverage, not a translation of the complete EFF list. Uniformly sampling the covered English entries and mapping them without deduplication would yield a maximum multiplicity of three, Shannon entropy 9.9795 bits and min-entropy 8.5051 bits per output. Deduplicating first and resampling would restore uniformity but still leave a sparse, sense-dependent translated vocabulary. [Every pilot pair](research/translation-pilot.json) is published. This experiment supports choosing native evidence instead of relying on one-to-one translation.

A POS template experiment used noun, adjective, verb, noun pools from selected headwords. One four-draw block gives 40.5401 bits under independent uniform selection of each pool. Two blocks reach 81.0802 bits with eight draws and an expected 53.77 codepoints. The native unrestricted alternative needs seven draws and an expected 48.29 codepoints. POS labels alone do not generate grammatical Vietnamese. Agreement constraints, synonym substitutions and selection of nice sentences would require a new distribution model. The template is therefore measured but not shipped as the default generator.

An LLM could help explain ambiguous vocabulary during review, but its choice probabilities are not a basis for a secret's entropy. No translation API or model output supplies production entries in this revision.

## Unicode and spelling

All source spellings become lowercase NFC for candidate grouping. Original uppercase presence is retained and conservatively excluded. The restricted alphabet rejects other scripts, invisible characters, controls and malformed spaces. Lexical variants such as `hòa` and `hoà` are not canonically equivalent under Unicode. A separate documented comparison key preserves vowel shape and tone identity while ignoring tone placement within a syllable. The representative prefers more exact corpus sentences, then the minimum syllable frequency, then codepoint order. Two otherwise eligible variants merge in this revision. This rule is an orthographic heuristic subject to linguistic review, not an instruction to normalize a user's password.

ASCII folding decomposes characters, removes combining marks and maps `đ` to `d`. The resulting 2,464 strings are deduplicated before sampling. The representative and all related native words are retained. The largest fold class contains eleven native words. Sampling native words first and folding afterward lowers min-entropy to 8.1185 bits per draw. The [security model](security.md) gives the calculation.

The lists do not guarantee unique prefixes or edit distance. Tone differences can produce close spellings. Delimiters are mandatory and automatic correction is absent. A future tolerant verifier would need a separate analysis of acceptance classes and attack probabilities.

## Memorability and quality limits

[Shay et al., SOUPS 2012](https://www.blaseur.com/papers/shay2012correct.pdf) found no general usability advantage for their tested system-assigned English passphrases over comparable-entropy passwords, and entry took longer. [Bonneau and Schechter, USENIX Security 2014](https://www.usenix.org/conference/usenixsecurity14/technical-sessions/presentation/bonneau) studied learning through repeated retrieval. Neither study validates Vietnamese vocabulary or this wordlist.

Frequency, dictionary agreement and short length are measurable proxies. They cannot prove recall, dialect familiarity, pronunciation, pleasantness or lack of offensive unlabelled senses. Conservative all-sense exclusions can reject familiar polysemous words. Missing labels can admit unsuitable words. Loanwords with dictionary and corpus evidence can remain. Tatoeba and wordfreq are not a representative contemporary Vietnamese user panel.

[The proposed evaluation protocol](evaluation.md) calls for separate linguistic review and a consented human study with measured recall, entry errors, typing time and user ratings. It has not been executed. The defensible improvement offered today is inspectable provenance, reproducible alternatives and correct sampling/encoding contracts, not an unmeasured claim that other repositories cannot replace this one.

## Licensing decision

Use Wiktionary's CC-BY-SA-4.0 option, wordfreq's CC-BY-SA-4.0 data grant and retained Tatoeba CC BY 2.0 France attribution. Preserve upstream notices and credits. English lists and GPL version 2 Vietnamese dictionary files remain benchmark references outside the production vocabulary. The reusable software uses LGPL-3.0-or-later, and original documentation and adapted data use CC-BY-SA-4.0. [The scope map](../LICENSES.md) and [license review](license-review.md) record the actual paths and constraints.
