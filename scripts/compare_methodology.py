"""Sensitivity and engineering tradeoffs, with no fitted human-utility score."""

import json
import math
from typing import Any

from build_data import merge_variants, orthography_key, read_inputs, reasons, token
from vocabulary_audit import ROOT, close_pairs, external_counts, fold, write_json


def measure(values: list[str], external: dict[str, int]) -> dict[str, Any]:
    edges = close_pairs(values, 1)
    return {
        "entries": len(values),
        "bitsPerDraw": round(math.log2(len(values)), 6),
        "meanCodepoints": round(sum(map(len, values)) / len(values), 6),
        "neighbor1Fraction": round(len({x for a, b, _ in edges for x in (a, b)}) / len(values), 6),
        "externalAttestedFraction": round(
            sum(external.get(x, 0) > 0 for x in values) / len(values), 6
        ),
        "asciiClasses": len({fold(x) for x in values}),
        "expectedCodepoints": {
            str(target): round(
                math.ceil(target / math.log2(len(values)))
                * (sum(map(len, values)) / len(values) + 1)
                - 1,
                6,
            )
            for target in [80, 96, 128]
        },
    }


def main() -> None:
    records, frequency, corpus = read_inputs()
    rules = json.loads((ROOT / "data/rules.json").read_text(encoding="utf-8"))
    external, _ = external_counts()
    pools = {
        both: [
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
        for both in [True, False]
    }
    rows: list[dict[str, Any]] = []
    for both, pool in pools.items():
        for syllables in [1, 2, 3]:
            for zipf in [300, 350, 400, 450, 500]:
                for sentences in [1, 2, 3, 5, 10, 20]:
                    eligible = [
                        w
                        for w in pool
                        if w.count(" ") + 1 <= syllables
                        and min(frequency.get(s, 0) for s in w.split(" ")) >= zipf
                        and len(corpus.get(w, [])) >= sentences
                    ]
                    words, _ = merge_variants(eligible, frequency, corpus, orthography_key)
                    values = sorted(token(w) for w in words)
                    rows.append(
                        {
                            "id": len(rows),
                            "bothEditions": both,
                            "maxSyllables": syllables,
                            "minSyllableZipfCentibels": zipf,
                            "minSentences": sentences,
                            **measure(values, external),
                        }
                    )
    baseline = next(
        r["id"]
        for r in rows
        if r["bothEditions"]
        and r["maxSyllables"] == 2
        and r["minSyllableZipfCentibels"] == 400
        and r["minSentences"] == 3
    )
    frontiers = {}
    dominators = {}
    for target in [80, 96, 128]:

        def dominates(a: dict[str, Any], b: dict[str, Any]) -> bool:
            costs_a = [
                a["expectedCodepoints"][str(target)],
                a["neighbor1Fraction"],
                -a["externalAttestedFraction"],
            ]
            costs_b = [
                b["expectedCodepoints"][str(target)],
                b["neighbor1Fraction"],
                -b["externalAttestedFraction"],
            ]
            return all(x <= y for x, y in zip(costs_a, costs_b)) and any(
                x < y for x, y in zip(costs_a, costs_b)
            )

        frontiers[str(target)] = [b["id"] for b in rows if not any(dominates(a, b) for a in rows)]
        dominators[str(target)] = [a["id"] for a in rows if dominates(a, rows[baseline])]
    ablations = []
    for both, minimum_zipf, minimum_sentences in [
        (True, 0, 3),
        (True, 400, 0),
        (True, 0, 0),
        (False, 400, 3),
    ]:
        eligible = [
            r["word"]
            for r in records
            if not reasons(
                r,
                rules,
                frequency,
                corpus,
                both=both,
                maximum=2,
                minimum_zipf=minimum_zipf,
                minimum_sentences=minimum_sentences,
            )
        ]
        words, _ = merge_variants(eligible, frequency, corpus, orthography_key)
        ablations.append(
            {
                "bothEditions": both,
                "minZipf": minimum_zipf,
                "minSentences": minimum_sentences,
                **measure(sorted(token(w) for w in words), external),
            }
        )
    write_json(
        ROOT / "docs/research/adversarial/methodology.json",
        {
            "schema": 1,
            "rows": rows,
            "baselineRow": baseline,
            "ablations": ablations,
            "engineeringParetoFrontiers": frontiers,
            "baselineEngineeringDominators": dominators,
            "objectives": [
                "minimize expected codepoints at explicit illustrative target",
                "minimize fraction with distance-one neighbor",
                "maximize external lexical attestation fraction",
            ],
            "limitations": [
                "These objectives are proxies, not human utility",
                "External corpus used for diagnosis, not profile selection",
                "Frontier depends on objectives and discrete entropy target",
                "No weighted utility or proven vocabulary optimum",
                "Grid and ablation candidates are not content-reviewed wordlists",
            ],
        },
    )
    print(json.dumps({"baseline": baseline, "frontiers": frontiers, "dominators": dominators}))


if __name__ == "__main__":
    main()
