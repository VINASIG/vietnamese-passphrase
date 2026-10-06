"""Generate source-backed sensitivity and alternative-model measurements offline."""

import collections
import hashlib
import json
import math

from build_data import fold, merge_variants, metrics, orthography_key, read_inputs, reasons, token
from prepare_sources import ROOT, write_json


def main() -> None:
    records, frequency, corpus = read_inputs()
    rules = json.loads((ROOT / "data/rules.json").read_text(encoding="utf-8"))
    pools = {}
    for both in [True, False]:
        pools[both] = [
            r["word"]
            for r in records
            if not reasons(
                r,
                rules,
                frequency,
                corpus,
                both=both,
                maximum=3,
                minimum_zipf=0,
                minimum_sentences=0,
            )
        ]
    rows = []
    for both, pool in pools.items():
        for max_syllables in [1, 2, 3]:
            for minimum_zipf in [300, 350, 400, 450, 500]:
                for minimum_sentences in [1, 2, 3, 5, 10, 20]:
                    eligible = [
                        w
                        for w in pool
                        if w.count(" ") + 1 <= max_syllables
                        and min(frequency.get(s, 0) for s in w.split(" ")) >= minimum_zipf
                        and len(corpus.get(w, [])) >= minimum_sentences
                    ]
                    words, _ = merge_variants(eligible, frequency, corpus, orthography_key)
                    rows.append(
                        {
                            "bothEditions": both,
                            "maxSyllables": max_syllables,
                            "minSyllableZipf": minimum_zipf / 100,
                            "minSentences": minimum_sentences,
                            "native": metrics(token(w) for w in words),
                            "asciiEntries": len({fold(w) for w in words}),
                        }
                    )
    manifest = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    native = (ROOT / "data/lists/vi.txt").read_text(encoding="utf-8").splitlines()
    by_word = {r["word"]: r for r in records}
    grammar = {}
    for pos in ["noun", "adj", "verb"]:
        pool = [
            w
            for w in native
            if all(pos in by_word[w.replace("_", " ")][e]["pos"] for e in ["en", "vi"])
        ]
        grammar[pos] = metrics(pool)
    template = ["noun", "adj", "verb", "noun"]
    template_bits = sum(grammar[pos]["bitsPerDraw"] for pos in template)
    template_length = sum(grammar[pos]["meanCodepoints"] + 1 for pos in template) - 1
    grammar_result = {
        "pools": grammar,
        "template": template,
        "bitsForOneBlock": template_bits,
        "expectedCodepointsForOneBlock": template_length,
        "blockTargets": {
            str(target): {
                "blocks": math.ceil(target / template_bits),
                "draws": 4 * math.ceil(target / template_bits),
                "bits": math.ceil(target / template_bits) * template_bits,
                "expectedCodepoints": math.ceil(target / template_bits) * (template_length + 1) - 1,
            }
            for target in [80, 96, 128]
        },
        "limitation": "POS membership alone does not establish grammatical Vietnamese. No agreement filter or human memory result is assumed.",
    }
    histogram = collections.Counter(len(corpus[w.replace("_", " ")]) for w in native)
    train = {
        w: [
            sid
            for sid in ids
            if int.from_bytes(hashlib.sha256(str(sid).encode("ascii")).digest()[:4], "big") % 5 != 0
        ]
        for w, ids in corpus.items()
    }
    heldout = {w: set(ids) - set(train[w]) for w, ids in corpus.items()}
    train_words, _ = merge_variants(
        [r["word"] for r in records if not reasons(r, rules, frequency, train)],
        frequency,
        train,
        orthography_key,
    )
    heldout_result = {
        "split": "SHA-256 of decimal sentence ID, first 4 bytes as big-endian integer modulo 5. Bucket 0 is held out.",
        "trainSelectedEntries": len(train_words),
        "entriesInHeldoutSentences": sum(bool(heldout.get(w)) for w in train_words),
        "heldoutCoverage": sum(bool(heldout.get(w)) for w in train_words) / len(train_words),
        "limitation": "This separates sentence IDs, not authors, templates, or domains. It is not an external corpus or a memorability test.",
    }
    report = {
        "schema": 1,
        "rulesVersion": rules["version"],
        "experiments": rows,
        "grammarAlternative": grammar_result,
        "sentenceHoldout": heldout_result,
        "selected": manifest["profiles"],
        "nativeCorpusSentenceHistogram": dict(sorted(histogram.items())),
        "limitations": [
            "Two Wiktionary editions are overlapping editorial sources.",
            "Tatoeba is a small translated-sentence corpus.",
            "Exact n-gram presence is not tokenized word frequency.",
            "No human memorability study was performed.",
        ],
    }
    write_json(ROOT / "docs/research/sensitivity.json", report)
    print(
        json.dumps(
            {
                "status": "PASS",
                "parameterCombinations": len(rows),
                "grammarBitsPerFourDrawBlock": template_bits,
            }
        )
    )


if __name__ == "__main__":
    main()
