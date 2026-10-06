"""Independent, deterministic vocabulary diagnostics. These are not human error rates."""

import argparse
import collections
import hashlib
import json
import math
import pathlib
import unicodedata
from collections.abc import Callable, Sequence
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
TONES = set("\u0300\u0301\u0303\u0309\u0323")


def fold(value: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", value.replace("đ", "d"))
        if not unicodedata.combining(c)
    )


def without_tone(value: str) -> str:
    return unicodedata.normalize(
        "NFC", "".join(c for c in unicodedata.normalize("NFD", value) if c not in TONES)
    )


def onset_stress(value: str) -> str:
    syllables = []
    for syllable in value.split("_"):
        for alternatives in [("gi", "d", "r"), ("s", "x"), ("tr", "ch"), ("l", "n")]:
            match = next((x for x in alternatives if syllable.startswith(x)), None)
            if match is not None:
                syllable = "{" + alternatives[0] + "}" + syllable[len(match) :]
                break
        syllables.append(syllable)
    return "_".join(syllables)


def telex(value: str) -> str:
    shapes = {"ă": "aw", "â": "aa", "ê": "ee", "ô": "oo", "ơ": "ow", "ư": "uw", "đ": "dd"}
    tone_keys = {"\u0301": "s", "\u0300": "f", "\u0309": "r", "\u0303": "x", "\u0323": "j"}
    syllables = []
    for syllable in value.split("_"):
        tone = "".join(
            tone_keys[c] for c in unicodedata.normalize("NFD", syllable) if c in tone_keys
        )
        letters = without_tone(syllable)
        syllables.append("".join(shapes.get(c, c) for c in letters) + tone)
    return "_".join(syllables)


def levenshtein(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        row = [i]
        for j, right in enumerate(b, 1):
            row.append(min(row[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = row
    return previous[-1]


def deletions(value: str, radius: int) -> set[str]:
    result = {value}
    frontier = {value}
    for _ in range(radius):
        frontier = {x[:i] + x[i + 1 :] for x in frontier for i in range(len(x))}
        result.update(frontier)
    return result


def close_pairs(tokens: Sequence[str], radius: int = 2) -> list[tuple[int, int, int]]:
    buckets: dict[str, list[int]] = collections.defaultdict(list)
    candidates: set[tuple[int, int]] = set()
    for i, token in enumerate(tokens):
        for key in sorted(deletions(token, radius)):
            for j in buckets[key]:
                if abs(len(tokens[j]) - len(token)) <= radius:
                    candidates.add((j, i))
            buckets[key].append(i)
    result = []
    for i, j in sorted(candidates):
        distance = levenshtein(tokens[i], tokens[j])
        if distance <= radius:
            result.append((i, j, distance))
    return result


def collision_groups(tokens: Sequence[str], key: Callable[[str], str]) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = collections.defaultdict(list)
    for token in tokens:
        groups[key(token)].append(token)
    return [
        {"key": name, "members": values}
        for name, values in sorted(groups.items())
        if len(values) > 1
    ]


def group_summary(groups: list[dict[str, Any]], size: int) -> dict[str, Any]:
    involved = sum(len(g["members"]) for g in groups)
    return {
        "groups": len(groups),
        "involvedTokens": involved,
        "tokenFraction": round(involved / size, 6),
        "largestClass": max((len(g["members"]) for g in groups), default=1),
    }


def external_counts(
    source: pathlib.Path = ROOT / "research/inputs/ud-vtb",
) -> tuple[dict[str, int], dict[str, Any]]:
    lock = json.loads((source / "manifest.json").read_text(encoding="utf-8"))
    counts: collections.Counter[str] = collections.Counter()
    sentences: set[str] = set()
    text_metadata_rows = 0
    rows = 0
    for file in lock["files"]:
        data = (source / file["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != file["sha256"] or len(data) != file["bytes"]:
            raise ValueError("External source digest or length mismatch")
        if not file["path"].endswith(".conllu"):
            continue
        for line in data.decode("utf-8", errors="strict").splitlines():
            if line.startswith("# sent_id = "):
                sentences.add(file["path"] + ":" + line.removeprefix("# sent_id = "))
            if line.startswith("# text = "):
                text_metadata_rows += 1
            if not line or line.startswith("#"):
                continue
            columns = line.split("\t")
            if len(columns) != 10:
                raise ValueError("Malformed CoNLL-U row")
            if not columns[0].isdigit():
                continue
            rows += 1
            counts[unicodedata.normalize("NFC", columns[1]).lower().replace(" ", "_")] += 1
    return dict(counts), {
        "source": lock["source"],
        "revision": lock["revision"],
        "sentences": len(sentences),
        "textMetadataRows": text_metadata_rows,
        "tokenRows": rows,
        "wordTypes": len(counts),
        "measure": "exact segmented FORM lexical attestation",
        "limitations": [
            "news genre",
            "small corpus",
            "not familiarity or recall",
            "source differs from Tatoeba; statistical independence is not established",
        ],
    }


def diagnose(
    tokens: list[str], counts: dict[str, int], pair_details: bool = True
) -> dict[str, Any]:
    if len(tokens) < 2 or len(set(tokens)) != len(tokens):
        raise ValueError("Need at least two unique tokens")
    size = len(tokens)
    pairs = close_pairs(tokens, 2)
    transforms = {
        "asciiFold": fold,
        "toneOnly": without_tone,
        "iyStress": lambda x: unicodedata.normalize(
            "NFC", unicodedata.normalize("NFD", x).replace("y", "i")
        ),
        "onsetStress": onset_stress,
        "shapeVisualStress": lambda x: without_tone(x).replace("đ", "d"),
        "prefix4": lambda x: x[:4],
        "suffix4": lambda x: x[-4:],
        "fused": lambda x: x.replace("_", ""),
    }
    groups = {name: collision_groups(tokens, key) for name, key in transforms.items()}
    qwerty_rows = ["qwertyuiop", "asdfghjkl", "zxcvbnm"]
    neighbors = {frozenset((a, b)) for row in qwerty_rows for a, b in zip(row, row[1:])}
    keyboard_pairs = []
    transpositions = []
    membership = {x: i for i, x in enumerate(tokens)}
    for i, a in enumerate(tokens):
        for k in range(len(a) - 1):
            b = a[:k] + a[k + 1] + a[k] + a[k + 2 :]
            j = membership.get(b)
            if j is not None and i < j:
                transpositions.append((i, j))
    for i, j, distance in pairs:
        a, b = tokens[i], tokens[j]
        if distance == 1 and len(a) == len(b):
            substitutions = [(x, y) for x, y in zip(a, b) if x != y]
            if len(substitutions) == 1 and frozenset(substitutions[0]) in neighbors:
                keyboard_pairs.append((i, j))
    distances = {}
    for radius in [1, 2]:
        selected = [(i, j) for i, j, d in pairs if d <= radius]
        involved = len({x for pair in selected for x in pair})
        distances[str(radius)] = {
            "pairs": len(selected),
            "involvedTokens": involved,
            "tokenFraction": round(involved / size, 6),
        }
    proper_prefix = [
        (tokens[j], token)
        for token in tokens
        for k in range(1, len(token))
        if (j := membership.get(token[:k])) is not None
    ]
    proper_suffix = [
        (tokens[j], token)
        for token in tokens
        for k in range(1, len(token))
        if (j := membership.get(token[-k:])) is not None
    ]
    typed_pairs = close_pairs([telex(x) for x in tokens], 1)
    bits = math.log2(size)
    draws = math.ceil(80 / bits)
    collisions = groups["asciiFold"]
    max_class = max((len(g["members"]) for g in collisions), default=1)
    result: dict[str, Any] = {
        "size": size,
        "bitsPerDraw": round(bits, 6),
        "drawsForIllustrative80Bits": draws,
        "deliveredBits": round(bits * draws, 6),
        "meanCodepoints": round(sum(map(len, tokens)) / size, 6),
        "expectedPhraseCodepoints": round(draws * sum(map(len, tokens)) / size + draws - 1, 6),
        "maxTokenCodepoints": max(map(len, tokens)),
        "externalAttestedTokens": sum(counts.get(x, 0) > 0 for x in tokens),
        "externalAttestedFraction": round(sum(counts.get(x, 0) > 0 for x in tokens) / size, 6),
        "levenshtein": distances,
        "groups": {name: group_summary(values, size) for name, values in groups.items()},
        "asciiFoldAfterNativeSamplingMinEntropy": round(math.log2(size / max_class), 6),
        "qwertySameRowAdjacentSubstitutionPairs": len(set(keyboard_pairs)),
        "adjacentTranspositionPairs": len(set(transpositions)),
        "properPrefixPairs": len(proper_prefix),
        "properSuffixPairs": len(proper_suffix),
        "canonicalTelexDistance1Pairs": len(typed_pairs),
        "canonicalTelexNeighbor1Fraction": round(
            len({i for a, b, _ in typed_pairs for i in (a, b)}) / size, 6
        ),
        "fusedExpectedPhraseCodepoints": round(
            draws * sum(len(x.replace("_", "")) for x in tokens) / size + draws - 1, 6
        ),
    }
    if pair_details:
        result["collisionDetails"] = groups
        result["distanceDetails"] = [
            {"a": tokens[i], "b": tokens[j], "distance": d} for i, j, d in pairs
        ]
        result["typingDetails"] = {
            "sameRowAdjacent": [[tokens[i], tokens[j]] for i, j in sorted(set(keyboard_pairs))],
            "transpositions": [[tokens[i], tokens[j]] for i, j in sorted(set(transpositions))],
            "canonicalTelex": [[tokens[i], tokens[j], d] for i, j, d in typed_pairs],
        }
        result["affixDetails"] = {"properPrefix": proper_prefix, "properSuffix": proper_suffix}
    return result


def write_json(path: pathlib.Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=pathlib.Path, default=ROOT / "docs/research/adversarial")
    args = parser.parse_args()
    counts, external = external_counts()
    profiles = {}
    for path in sorted((ROOT / "data/lists").glob("*.txt")):
        tokens = path.read_text(encoding="utf-8").splitlines()
        comparison_counts = counts
        if path.stem == "vi-ascii":
            projected: collections.Counter[str] = collections.Counter()
            for token, count in counts.items():
                projected[fold(token)] += count
            comparison_counts = dict(projected)
        result = diagnose(tokens, comparison_counts)
        result["externalMatchRepresentation"] = (
            "ASCII-folded FORM (not semantic equivalence)"
            if path.stem == "vi-ascii"
            else "native NFC FORM"
        )
        write_json(args.out / (path.stem + ".json"), result)
        profiles[path.stem] = {k: v for k, v in result.items() if not k.endswith("Details")}
    write_json(
        args.out / "summary.json",
        {
            "schema": 1,
            "baselineDataVersion": "2026-10-06.1",
            "external": external,
            "scope": "structural diagnostics and lexical attestation, not predicted human performance",
            "unicode": "NFC codepoint Levenshtein; not grapheme, Telex or VNI distance",
            "typingModel": "Canonical Telex letter-shape expansion and tone key at syllable end; one modeled input sequence, not all legal input orders, IME behavior, VNI, keypress timing or observed error rates",
            "stressKeys": "lossy similarity scenarios, not dialect labels, homophone assertions or normalization rules",
            "profiles": profiles,
        },
    )
    print(json.dumps(profiles, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
