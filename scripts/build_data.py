"""Build deterministic wordlists and an inclusion/exclusion ledger offline."""

import argparse
import collections
import hashlib
import json
import math
import pathlib
import statistics
import unicodedata
from collections.abc import Callable, Iterable
from decimal import Decimal, localcontext
from typing import Any

from prepare_sources import LETTERS, ROOT, safe, write_json

TONE_MARKS = set("\u0300\u0301\u0303\u0309\u0323")


def log2_count(count: int) -> float:
    with localcontext() as context:
        context.prec = 50
        return float((Decimal(count).ln() / Decimal(2).ln()).quantize(Decimal("0.000000000001")))


def fold(word: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", word.replace("đ", "d"))
        if not unicodedata.combining(c)
    )


def orthography_key(word: str) -> str:
    result = []
    for syllable in word.split(" "):
        decomposed = unicodedata.normalize("NFD", syllable)
        shape = "".join(c for c in decomposed if c not in TONE_MARKS)
        tones = "".join(sorted(c for c in decomposed if c in TONE_MARKS))
        result.append(shape + ":" + tones)
    return " ".join(result)


def token(word: str) -> str:
    return word.replace(" ", "_")


def read_inputs() -> tuple[list[dict[str, Any]], dict[str, int], dict[str, list[int]]]:
    folder = ROOT / "data/inputs"
    manifest = json.loads((folder / "manifest.json").read_text(encoding="utf-8"))
    for name, spec in manifest["files"].items():
        value = (folder / name).read_bytes()
        if len(value) != spec["bytes"] or hashlib.sha256(value).hexdigest() != spec["sha256"]:
            raise ValueError("Portable input checksum mismatch " + name)
    records = [
        json.loads(line)
        for line in (folder / "lexicon.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    if len({r["word"] for r in records}) != len(records):
        raise ValueError("Duplicate lexical record")
    frequency = json.loads((folder / "syllable-frequency.json").read_text(encoding="utf-8"))
    corpus = json.loads((folder / "corpus-evidence.json").read_text(encoding="utf-8"))
    return records, frequency, corpus


def reasons(
    record: dict[str, Any],
    rules: dict[str, Any],
    frequency: dict[str, int],
    corpus: dict[str, list[int]],
    both: bool = True,
    maximum: int | None = None,
    minimum_zipf: int | None = None,
    minimum_sentences: int | None = None,
) -> list[str]:
    result = []
    word = record["word"]
    if not safe(word):
        result.append("unsafe-form")
    editions = [record[e] for e in rules["requiredEditions"] if record[e] is not None]
    if (both and len(editions) != len(rules["requiredEditions"])) or not editions:
        result.append("dictionary-coverage")
    if any(r["uppercase"] for r in editions):
        result.append("uppercase-entry")
    if any(r["badForm"] for r in editions):
        result.append("source-form")
    if any(not (set(rules["partsOfSpeech"]) & set(r["pos"])) for r in editions):
        result.append("part-of-speech")
    tags = {t.lower() for r in editions for t in r["tags"]}
    if tags & set(rules["excludedTags"]):
        result.append("excluded-label")
    if rules["requireStandaloneSense"] and any(not r["standalone"] for r in editions):
        result.append("bound-or-unexplained")
    if word.count(" ") + 1 > (rules["maxSyllables"] if maximum is None else maximum):
        result.append("syllable-limit")
    if min((frequency.get(s, 0) for s in word.split(" ")), default=0) < (
        rules["minimumSyllableZipfCentibels"] if minimum_zipf is None else minimum_zipf
    ):
        result.append("syllable-frequency")
    if len(corpus.get(word, [])) < (
        rules["minimumDistinctCorpusSentences"] if minimum_sentences is None else minimum_sentences
    ):
        result.append("corpus-coverage")
    return result


def rank(
    word: str, frequency: dict[str, int], corpus: dict[str, list[int]]
) -> tuple[int, int, str]:
    return (-len(corpus.get(word, [])), -min(frequency.get(s, 0) for s in word.split(" ")), word)


def merge_variants(
    words: Iterable[str],
    frequency: dict[str, int],
    corpus: dict[str, list[int]],
    key: Callable[[str], str],
) -> tuple[list[str], dict[str, str]]:
    groups = collections.defaultdict(list)
    for word in words:
        groups[key(word)].append(word)
    winners = {}
    for group in groups.values():
        chosen = min(group, key=lambda w: rank(w, frequency, corpus))
        for word in group:
            winners[word] = chosen
    return sorted(set(winners.values())), winners


def metrics(words: Iterable[str]) -> dict[str, Any]:
    tokens = list(words)
    n = len(tokens)
    bits = log2_count(n) if n > 1 else 0
    lengths = [len(w) for w in tokens]
    utf8 = [len(w.encode("utf-8")) for w in tokens]
    prefixes = collections.Counter(w[:4] for w in tokens)
    return {
        "entries": n,
        "bitsPerDraw": bits,
        "minCodepoints": min(lengths, default=0),
        "maxCodepoints": max(lengths, default=0),
        "meanCodepoints": statistics.mean(lengths) if n else 0,
        "meanUtf8Bytes": statistics.mean(utf8) if n else 0,
        "maxUtf8Bytes": max(utf8, default=0),
        "fourCodepointPrefixCollidingEntries": sum(c for c in prefixes.values() if c > 1),
        "targets": {
            str(target): {
                "draws": math.ceil(target / bits),
                "bits": math.ceil(target / bits) * bits,
                "expectedCodepoints": math.ceil(target / bits) * (statistics.mean(lengths) + 1) - 1,
                "expectedUtf8Bytes": math.ceil(target / bits) * (statistics.mean(utf8) + 1) - 1,
            }
            for target in [64, 80, 96, 128]
            if bits
        },
    }


def build(out: pathlib.Path) -> dict[str, Any]:
    records, frequency, corpus = read_inputs()
    rules = json.loads((ROOT / "data/rules.json").read_text(encoding="utf-8"))
    eligible = [r["word"] for r in records if not reasons(r, rules, frequency, corpus)]
    native, variants = merge_variants(eligible, frequency, corpus, orthography_key)
    ascii_words, ascii_winners = merge_variants(native, frequency, corpus, fold)
    profiles = {
        "vi": [token(w) for w in native],
        "vi-ascii": sorted(token(fold(w)) for w in ascii_words),
        "vi-short": [token(w) for w in native if " " not in w],
    }
    for name, words in profiles.items():
        if (
            len(words) < 2
            or len(words) != len(set(words))
            or any(w != unicodedata.normalize("NFC", w) for w in words)
        ):
            raise ValueError("Invalid generated profile " + name)
        if words != sorted(words) or any(
            not all(c in LETTERS or c == "_" for c in w) for w in words
        ):
            raise ValueError("Invalid ordering or alphabet " + name)
        path = out / "lists" / (name + ".txt")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(words) + "\n", encoding="utf-8", newline="\n")
        rolls_per_group = 1
        dice_range = 6
        while dice_range < len(words):
            dice_range *= 6
            rolls_per_group += 1
        accepted_range = dice_range - dice_range % len(words)
        dice_path = out / "dice" / (name + ".tsv")
        dice_path.parent.mkdir(parents=True, exist_ok=True)
        with dice_path.open("w", encoding="utf-8", newline="\n") as stream:
            stream.write("rolls\tindex\ttoken\n")
            for value in range(dice_range):
                remaining = value
                code = ""
                for _ in range(rolls_per_group):
                    code = str(remaining % 6 + 1) + code
                    remaining //= 6
                if value < accepted_range:
                    index = value % len(words)
                    stream.write(f"{code}\t{index}\t{words[index]}\n")
                else:
                    stream.write(f"{code}\t-\tREJECT\n")
    ledger = []
    included = set(native)
    for r in records:
        word = r["word"]
        why = reasons(r, rules, frequency, corpus)
        if not why and variants[word] != word:
            why.append("orthographic-variant")
        ledger.append(
            {
                "word": word,
                "reasons": why,
                "nativeToken": token(word) if word in included else None,
                "variantOf": variants.get(word) if variants.get(word) != word else None,
            }
        )
    (out / "audit").mkdir(parents=True, exist_ok=True)
    (out / "audit/decisions.jsonl").write_text(
        "".join(
            json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for r in ledger
        ),
        encoding="utf-8",
        newline="\n",
    )
    by_word = {r["word"]: r for r in records}
    ascii_groups = collections.defaultdict(list)
    for word in native:
        ascii_groups[token(fold(word))].append(word)
    provenance = []
    for word in native:
        r = by_word[word]
        provenance.append(
            {
                "token": token(word),
                "word": word,
                "en": r["en"],
                "vi": r["vi"],
                "syllableZipfCentibels": [frequency[s] for s in word.split(" ")],
                "sentenceIds": corpus[word],
                "asciiToken": token(fold(word)),
                "asciiRepresentative": word == ascii_winners[word],
                "asciiVariants": sorted(ascii_groups[token(fold(word))]),
            }
        )
    (out / "provenance.jsonl").write_text(
        "".join(
            json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            for r in provenance
        ),
        encoding="utf-8",
        newline="\n",
    )
    fold_counts = collections.Counter(fold(w) for w in native)
    meta = {
        "schema": 1,
        "dataVersion": rules["version"],
        "status": rules["status"],
        "license": "CC-BY-SA-4.0",
        "normalization": "NFC",
        "internalSeparator": "_",
        "selection": rules,
        "profiles": {
            name: {
                **metrics(words),
                "path": "lists/" + name + ".txt",
                "sha256": hashlib.sha256(
                    (out / "lists" / (name + ".txt")).read_bytes()
                ).hexdigest(),
                "format": "ascii" if name == "vi-ascii" else "nfc",
                "scope": "short single-syllable alternative"
                if name == "vi-short"
                else "primary"
                if name == "vi"
                else "compatibility",
            }
            for name, words in profiles.items()
        },
        "asciiAfterSampling": {
            "unique": len(fold_counts),
            "largestCollisionClass": max(fold_counts.values()),
            "minEntropyPerDraw": round(
                log2_count(len(native)) - log2_count(max(fold_counts.values())), 12
            ),
        },
        "inputRecords": len(records),
        "eligibleBeforeOrthographyMerge": len(eligible),
        "excludedReasons": dict(
            sorted(collections.Counter(t for row in ledger for t in row["reasons"]).items())
        ),
        "validation": {
            "deterministicStructural": "PASS",
            "independentLinguisticReview": "NOT_RUN",
            "humanMemorabilityStudy": "NOT_RUN",
            "independentSecurityAudit": "NOT_RUN",
        },
    }
    write_json(out / "manifest.json", meta)
    checksums = {
        p.relative_to(out).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out.rglob("*"))
        if p.is_file() and p.relative_to(out).parts[0] in {"lists", "audit", "dice"}
    }
    checksums["manifest.json"] = hashlib.sha256((out / "manifest.json").read_bytes()).hexdigest()
    checksums["provenance.jsonl"] = hashlib.sha256(
        (out / "provenance.jsonl").read_bytes()
    ).hexdigest()
    write_json(out / "checksums.json", checksums)
    print(
        json.dumps(
            {
                "status": "PASS",
                "profiles": {
                    name: {
                        k: v
                        for k, v in m.items()
                        if k in {"entries", "bitsPerDraw", "meanCodepoints"}
                    }
                    for name, m in meta["profiles"].items()
                },
                "orthographicVariantsMerged": len(eligible) - len(native),
            },
            ensure_ascii=False,
        )
    )
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "data")
    args = parser.parse_args()
    build(args.out)


if __name__ == "__main__":
    main()
