import argparse
import collections
import gzip
import hashlib
import json
import math
import pathlib
import re
import statistics
import unicodedata
from collections.abc import Iterable
from typing import Any

from prepare_sources import ROOT, unpack

parser = argparse.ArgumentParser(
    description="Benchmark licensed upstream lists without incorporating them into production wordlists"
)
parser.add_argument("--upstream", type=pathlib.Path, required=True)
args = parser.parse_args()
UPSTREAM = args.upstream
REPORT = ROOT / "docs/research"
lock = json.loads((ROOT / "data/source-lock.json").read_text(encoding="utf-8"))
for source in lock["sources"]:
    value = (UPSTREAM / source["file"]).read_bytes()
    if hashlib.sha256(value).hexdigest() != source["sha256"] or len(value) != source["bytes"]:
        raise ValueError("Benchmark input mismatch " + source["file"])

bins = unpack(gzip.decompress((UPSTREAM / "wordfreq-vi.msgpack.gz").read_bytes()))[1:]
frequency = {
    unicodedata.normalize("NFC", word): round(9 - index / 100, 2)
    for index, words in enumerate(bins)
    for word in words
}
letters = set("abcdefghijklmnopqrstuvwxyzđ")
for vowel in "aăâeêioôơuưy":
    for mark in ["", "\u0300", "\u0301", "\u0303", "\u0309", "\u0323"]:
        letters.add(unicodedata.normalize("NFC", vowel + mark))


def fold(word: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", word.replace("đ", "d"))
        if not unicodedata.combining(c)
    )


def safe(word: str) -> bool:
    return (
        bool(word)
        and word == word.strip()
        and "  " not in word
        and all(c in letters or c == " " for c in word)
    )


bad_tags = {
    "abbreviation",
    "acronym",
    "initialism",
    "obsolete",
    "archaic",
    "rare",
    "dated",
    "vulgar",
    "offensive",
    "derogatory",
    "slur",
    "slang",
    "nonstandard",
    "misspelling",
    "dialectal",
    "regional",
    "literary",
    "poetic",
    "historical",
}


def dictionary(file: str) -> tuple[dict[str, Any], dict[str, Any]]:
    words: dict[str, Any] = {}
    counters: collections.Counter[str] = collections.Counter()
    tags: collections.Counter[str] = collections.Counter()
    positions: collections.Counter[str] = collections.Counter()
    opener = gzip.open if file.endswith(".gz") else open
    with opener(UPSTREAM / file, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            counters["records"] += 1
            if record.get("lang_code") != "vi":
                continue
            counters["vi_records"] += 1
            raw = record.get("word", "")
            word = unicodedata.normalize("NFC", raw)
            pos = record.get("pos", "")
            positions[pos] += 1
            labels = set(record.get("tags", []))
            for sense in record.get("senses", []):
                labels.update(sense.get("tags", []))
                labels.update(sense.get("raw_tags", []))
            tags.update(labels)
            normalized = word.lower()
            item = words.setdefault(
                normalized,
                {
                    "word": normalized,
                    "pos": set(),
                    "tags": set(),
                    "glosses": set(),
                    "uppercase": False,
                    "bad_form": False,
                },
            )
            item["pos"].add(pos)
            item["tags"].update(labels)
            item["uppercase"] |= word != normalized
            item["bad_form"] |= not safe(normalized)
            for sense in record.get("senses", []):
                item["glosses"].update(sense.get("glosses", []))
    clean = {
        w: r
        for w, r in words.items()
        if not r["uppercase"]
        and not r["bad_form"]
        and {"noun", "verb", "adj"} & r["pos"]
        and not bad_tags & r["tags"]
    }
    print(
        json.dumps(
            {
                "file": file,
                "counts": dict(counters),
                "distinct": len(words),
                "eligible": len(clean),
                "pos": dict(positions),
                "tags": tags.most_common(20),
            },
            ensure_ascii=False,
        )
    )
    return words, clean


en, en_clean = dictionary("wiktionary-en-vi.jsonl")
vi, vi_clean = dictionary("wiktionary-vi.jsonl.gz")
print(
    json.dumps(
        {
            "wordfreq_tokens": len(frequency),
            "multi_syllable_tokens": sum(" " in w for w in frequency),
            "known_first": list(frequency.items())[:15],
        },
        ensure_ascii=False,
    )
)


def metrics(name: str, words: Iterable[str]) -> dict[str, Any]:
    words = list(words)
    normalized = [unicodedata.normalize("NFC", w.lower()) for w in words]
    unique = list(dict.fromkeys(normalized))
    ascii_counts = collections.Counter(fold(w).replace(" ", "_") for w in unique)
    tokens = [w.replace(" ", "_") for w in unique]
    scores = [min(frequency.get(s, 0) for s in w.split(" ")) for w in unique]
    return {
        "name": name,
        "rows": len(words),
        "uniqueNfc": len(unique),
        "asciiUnique": len(ascii_counts),
        "asciiCollidingEntries": sum(c for c in ascii_counts.values() if c > 1),
        "largestAsciiClass": max(ascii_counts.values(), default=0),
        "bitsPerEntry": math.log2(len(unique)) if unique else 0,
        "meanCodepoints": statistics.mean(map(len, tokens)) if tokens else 0,
        "meanUtf8Bytes": statistics.mean(len(w.encode()) for w in tokens) if tokens else 0,
        "meanSyllables": statistics.mean(w.count(" ") + 1 for w in unique) if unique else 0,
        "missingSyllableFrequency": sum(s == 0 for s in scores),
        "minFrequencyMedian": statistics.median(scores) if scores else 0,
    }


rows = []
for file in [
    "eff-large.txt",
    "eff-short.txt",
    "eff-short2.txt",
    "orchard-medium.txt",
    "orchard-long.txt",
    "bip39-vietnamese.txt",
]:
    rows.append(
        metrics(
            file,
            [
                line.split()[-1]
                for line in (UPSTREAM / file).read_text(encoding="utf-8").splitlines()
                if line.strip()
            ],
        )
    )
for size in ["11K", "22K", "39K", "74K"]:
    words = (UPSTREAM / f"duyet-{size}.txt").read_text(encoding="utf-8-sig").splitlines()
    rows.append(metrics("duyet-" + size, words))

intersection = set(en_clean) & set(vi_clean)
for name, pool in [
    ("en-native", en_clean),
    ("vi-native", vi_clean),
    ("attested-both", intersection),
]:
    rows.append(metrics(name, pool))
    for syllables in [1, 2, 3]:
        short = {w for w in pool if w.count(" ") + 1 <= syllables}
        for threshold in [3.0, 3.5, 4.0, 4.5, 5.0]:
            selected = {
                w for w in short if min(frequency.get(s, 0) for s in w.split(" ")) >= threshold
            }
            rows.append(
                metrics(f"{name}-syllables{syllables}-minzipf{threshold}", sorted(selected))
            )

eff = [
    line.split()[-1]
    for line in (UPSTREAM / "eff-large.txt").read_text(encoding="utf-8").splitlines()
    if line.strip()
]
reverse = collections.defaultdict(list)
for word, r in en_clean.items():
    for gloss in r["glosses"]:
        simple = re.sub(r"\([^)]*\)", "", gloss).strip().rstrip(".").strip().lower()
        if re.fullmatch(r"[a-z]+", simple):
            reverse[simple].append(word)
translations = [min(reverse[w], key=lambda v: (len(v), v)) for w in eff if reverse[w]]
counts = collections.Counter(translations)
translation = {
    "effEnglishEntries": len(eff),
    "exactGlossCovered": len(translations),
    "vietnameseUnique": len(counts),
    "maxMultiplicity": max(counts.values(), default=0),
    "collisionClasses": [
        {"word": w, "multiplicity": n} for w, n in counts.most_common(20) if n > 1
    ],
    "shannonBits": -sum(
        (n / len(translations)) * math.log2(n / len(translations)) for n in counts.values()
    ),
    "minEntropyBits": -math.log2(max(counts.values()) / len(translations)),
}
rows.append(metrics("eff-exact-gloss-translation-pilot", translations))
compact = collections.defaultdict(list)
for word in en_clean.keys() | vi_clean.keys():
    compact[word.replace(" ", "")].append(word)
bip = (UPSTREAM / "bip39-vietnamese.txt").read_text(encoding="utf-8").splitlines()
fold_counts = collections.Counter(fold(word) for word in bip)
prefixes = collections.Counter(word[:4] for word in bip)
bip_comparison = {
    "entries": len(bip),
    "nfcUnique": len({unicodedata.normalize("NFC", w) for w in bip}),
    "nfkdUnique": len({unicodedata.normalize("NFKD", w) for w in bip}),
    "asciiUnique": len(fold_counts),
    "largestAsciiClass": max(fold_counts.values()),
    "minEntropyAfterAsciiFolding": -math.log2(max(fold_counts.values()) / len(bip)),
    "duplicateFourCodepointPrefixes": sum(n - 1 for n in prefixes.values() if n > 1),
    "dictionaryMatchesAfterRestoringBoundaries": sum(w in compact for w in bip),
    "matchingMethod": "Remove spaces from eligible dictionary headwords, then compare exact text. This is different from raw headword matching.",
    "nativeSpeakerReview": "Pending according to upstream README. Not independently validated here.",
}
report = {
    "schema": 1,
    "wordfreqTokenCount": len(frequency),
    "nativeBoth": len(intersection),
    "metrics": rows,
    "translationPilot": translation,
    "tzurComparison": bip_comparison,
    "sourceRevisions": {s["file"]: s["sha256"] for s in lock["sources"]},
}
(REPORT / "baselines.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
for item in rows:
    print(json.dumps(item, ensure_ascii=False))
print(json.dumps({"translation": translation}, ensure_ascii=False))
pairs = [
    {"english": w, "vietnamese": min(reverse[w], key=lambda v: (len(v), v))}
    for w in eff
    if reverse[w]
]
(REPORT / "translation-pilot.json").write_text(
    json.dumps(
        {
            "method": "Exact single-word gloss after parenthesis removal. Shortest Vietnamese lexical choice. Partial coverage only.",
            "pairs": pairs,
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    + "\n",
    encoding="utf-8",
)
