"""Reduce verified upstream snapshots to portable lexical evidence. No downloads."""

import argparse
import bz2
import collections
import gzip
import hashlib
import json
import pathlib
import unicodedata
from collections.abc import Iterator
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
LETTERS = set("abcdefghijklmnopqrstuvwxyzđ")
for vowel in "aăâeêioôơuưy":
    for mark in ["", "\u0300", "\u0301", "\u0303", "\u0309", "\u0323"]:
        LETTERS.add(unicodedata.normalize("NFC", vowel + mark))
BOUND_TAGS = {
    "morpheme",
    "in-compounds",
    "not in isolation",
    "not used in isolation",
    "used in compounds",
    "in Sino-Vietnamese compounds",
    "in limited combinations",
}


def write_json(path: pathlib.Path, value: Any | None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def unpack(data: bytes) -> Any:
    position = 0

    def integer(size: int) -> int:
        nonlocal position
        if position + size > len(data):
            raise ValueError("Truncated MessagePack")
        value = int.from_bytes(data[position : position + size], "big")
        position += size
        return value

    def read() -> Any:
        nonlocal position
        code = integer(1)
        if code < 128:
            return code
        if 160 <= code < 192:
            size = code - 160
        elif code in (217, 218, 219):
            size = integer({217: 1, 218: 2, 219: 4}[code])
        elif 144 <= code < 160:
            return [read() for _ in range(code - 144)]
        elif code in (220, 221):
            return [read() for _ in range(integer(2 if code == 220 else 4))]
        elif 128 <= code < 144:
            return {read(): read() for _ in range(code - 128)}
        else:
            raise ValueError("Unsupported MessagePack byte " + str(code))
        if position + size > len(data):
            raise ValueError("Truncated MessagePack string")
        value = data[position : position + size].decode("utf-8", errors="strict")
        position += size
        return value

    value = read()
    if position != len(data) or value[0] != {"format": "cB", "version": 1}:
        raise ValueError("Unexpected wordfreq format")
    return value


def safe(word: str) -> bool:
    return (
        bool(word)
        and word == word.strip()
        and "  " not in word
        and all(c in LETTERS or c == " " for c in word)
    )


def dictionary(path: pathlib.Path) -> tuple[dict[str, Any], dict[str, int]]:
    words: dict[str, Any] = {}
    stats: collections.Counter[str] = collections.Counter()
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            record = json.loads(line)
            stats["records"] += 1
            if record.get("lang_code") != "vi":
                continue
            stats["vietnameseRecords"] += 1
            raw = unicodedata.normalize("NFC", record["word"])
            word = raw.lower()
            item = words.setdefault(
                word,
                {
                    "pos": set(),
                    "tags": set(),
                    "uppercase": False,
                    "badForm": False,
                    "standalone": False,
                },
            )
            pos = record.get("pos", "")
            item["pos"].add(pos)
            item["uppercase"] |= raw != word
            item["badForm"] |= not safe(word)
            top_tags = set(record.get("tags", [])) | set(record.get("raw_tags", []))
            item["tags"].update(top_tags)
            for sense in record.get("senses", []):
                tags = top_tags | set(sense.get("tags", [])) | set(sense.get("raw_tags", []))
                item["tags"].update(tags)
                if (
                    pos in {"noun", "verb", "adj"}
                    and sense.get("glosses")
                    and not (tags & BOUND_TAGS)
                ):
                    item["standalone"] = True
    result = {
        w: {**r, "pos": sorted(r["pos"]), "tags": sorted(r["tags"])} for w, r in words.items()
    }
    return result, {**dict(stats), "uniqueLowerNfc": len(words)}


def segments(sentence: str) -> Iterator[list[str]]:
    group = []
    syllable = ""
    for char in unicodedata.normalize("NFC", sentence).lower() + "!":
        if char in LETTERS:
            syllable += char
            continue
        if syllable:
            group.append(syllable)
            syllable = ""
        if char != " ":
            if group:
                yield group
            group = []


def corpus(path: pathlib.Path, vocabulary: set[str]) -> tuple[dict[str, list[int]], dict[str, Any]]:
    counts = collections.defaultdict(set)
    authors = collections.defaultdict(set)
    seen = set()
    total = 0
    with bz2.open(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 6 or fields[1] != "vie":
                raise ValueError("Unexpected Tatoeba schema")
            total += 1
            sentence = unicodedata.normalize("NFC", fields[2]).lower()
            if sentence in seen:
                continue
            seen.add(sentence)
            for words in segments(sentence):
                for size in range(1, 4):
                    for start in range(len(words) - size + 1):
                        word = " ".join(words[start : start + size])
                        if word in vocabulary:
                            counts[word].add(int(fields[0]))
                            if fields[3] != "\\N":
                                authors[fields[3]].add(int(fields[0]))
    return (
        {w: sorted(ids) for w, ids in sorted(counts.items())},
        {
            "rows": total,
            "uniqueSentences": len(seen),
            "authors": {name: sorted(ids) for name, ids in sorted(authors.items())},
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=pathlib.Path, required=True)
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "data/inputs")
    args = parser.parse_args()
    lock = json.loads((ROOT / "data/source-lock.json").read_text(encoding="utf-8"))
    needed = [
        "wiktionary-en-vi.jsonl",
        "wiktionary-vi.jsonl.gz",
        "wordfreq-vi.msgpack.gz",
        "tatoeba-vie-detailed.tsv.bz2",
    ]
    for name in needed:
        spec = next(s for s in lock["sources"] if s["file"] == name)
        value = (args.upstream / name).read_bytes()
        if len(value) != spec["bytes"] or hashlib.sha256(value).hexdigest() != spec["sha256"]:
            raise ValueError("Upstream checksum mismatch " + name)
    en, en_stats = dictionary(args.upstream / needed[0])
    vi, vi_stats = dictionary(args.upstream / needed[1])
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "lexicon.jsonl").open("w", encoding="utf-8", newline="\n") as stream:
        for word in sorted(en.keys() | vi.keys()):
            record = {"word": word, "en": en.get(word), "vi": vi.get(word)}
            stream.write(
                json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
            )
    bins = unpack(gzip.decompress((args.upstream / needed[2]).read_bytes()))[1:]
    frequency = {
        unicodedata.normalize("NFC", w): 900 - i for i, words in enumerate(bins) for w in words
    }
    if any(" " in w for w in frequency) or len(frequency) != 10719:
        raise ValueError("Unexpected frequency snapshot")
    write_json(args.out / "syllable-frequency.json", frequency)
    evidence, credits = corpus(args.upstream / needed[3], set(en) | set(vi))
    write_json(args.out / "corpus-evidence.json", evidence)
    write_json(args.out / "tatoeba-credits.json", credits)
    files = {
        p.name: {"bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
        for p in sorted(args.out.iterdir())
        if p.name != "manifest.json"
    }
    write_json(
        args.out / "manifest.json",
        {
            "schema": 1,
            "sources": needed,
            "dictionaryStats": {"en": en_stats, "vi": vi_stats},
            "files": files,
        },
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "portableInputs": files,
                "dictionaries": {"en": en_stats, "vi": vi_stats},
                "corpusSentences": credits["uniqueSentences"],
            }
        )
    )


if __name__ == "__main__":
    main()
