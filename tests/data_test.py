"""Independent structural checks and clean-directory rebuild verification."""

import collections
import hashlib
import json
import math
import pathlib
import subprocess
import sys
import tempfile
import unicodedata
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


class DataTests(unittest.TestCase):
    def test_standards_and_notices_are_preserved(self) -> None:
        manifest = json.loads((ROOT / ".vinasig/manifest.json").read_text(encoding="utf-8"))
        for name, expected in manifest["files"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), expected, name)
        text = (ROOT / "AGENTS.md").read_bytes()
        begin = b"<!-- VINASIG STANDARDS BEGIN -->"
        end = b"<!-- VINASIG STANDARDS END -->"
        block = text[text.index(begin) : text.index(end) + len(end)]
        self.assertEqual(hashlib.sha256(block).hexdigest(), manifest["agentBlock"])
        self.assertEqual(
            (ROOT / "BRAND_POLICY.md").read_bytes(),
            (ROOT / ".vinasig/standards/BRAND_POLICY.md").read_bytes(),
        )
        sources = json.loads((ROOT / "data/source-lock.json").read_text(encoding="utf-8"))[
            "sources"
        ]
        notice = next(s for s in sources if s["file"] == "wordfreq-NOTICE.md")
        self.assertEqual(
            hashlib.sha256((ROOT / "docs/third-party/wordfreq-NOTICE.md").read_bytes()).hexdigest(),
            notice["sha256"],
        )

    def test_cross_language_conformance_vectors(self) -> None:
        vectors = json.loads((ROOT / "tests/vectors.json").read_text(encoding="utf-8"))
        spec = vectors["uniform"]
        limit = (1 << 32) - (1 << 32) % spec["size"]
        self.assertEqual(
            [x % spec["size"] if x < limit else None for x in spec["inputs"]], spec["outputs"]
        )
        spec = vectors["dice"]
        self.assertEqual(
            [
                ((rolls[0] - 1) * 6 + rolls[1] - 1) % 7 if rolls != [6, 6] else None
                for rolls in spec["rolls"]
            ],
            spec["outputs"],
        )
        spec = vectors["phrase"]
        value = spec["separator"].join(spec["tokens"][i] for i in spec["indices"])
        self.assertEqual(value, spec["output"])
        self.assertEqual(len(value), spec["codepoints"])
        self.assertEqual(len(value.encode("utf-8")), spec["utf8Bytes"])

    def test_independent_structure_and_dice_balance(self) -> None:
        metadata = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
        for name, profile in metadata["profiles"].items():
            words = (ROOT / "data/lists" / (name + ".txt")).read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(words), profile["entries"])
            self.assertEqual(words, sorted(set(words)))
            self.assertTrue(all(w == unicodedata.normalize("NFC", w) for w in words))
            self.assertAlmostEqual(math.log2(len(words)), profile["bitsPerDraw"])
            for target, plan in profile["targets"].items():
                self.assertGreaterEqual(plan["bits"], int(target))
                self.assertLess((plan["draws"] - 1) * math.log2(len(words)), int(target))
            counts: collections.Counter[int] = collections.Counter()
            lines = (ROOT / "data/dice" / (name + ".tsv")).read_text(encoding="utf-8").splitlines()
            self.assertEqual(lines[0], "rolls\tindex\ttoken")
            for line in lines[1:]:
                code, index, word = line.split("\t")
                self.assertTrue(set(code) <= set("123456"))
                if index == "-":
                    self.assertEqual(word, "REJECT")
                else:
                    self.assertEqual(word, words[int(index)])
                    counts[int(index)] += 1
            self.assertEqual(len(counts), len(words))
            self.assertEqual(len(set(counts.values())), 1)

    def test_provenance_and_ascii_equivalence(self) -> None:
        native = set((ROOT / "data/lists/vi.txt").read_text(encoding="utf-8").splitlines())
        ascii_words = set(
            (ROOT / "data/lists/vi-ascii.txt").read_text(encoding="utf-8").splitlines()
        )
        evidence = [
            json.loads(line)
            for line in (ROOT / "data/provenance.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual({r["token"] for r in evidence}, native)
        self.assertEqual({r["asciiToken"] for r in evidence}, ascii_words)
        self.assertEqual(sum(r["asciiRepresentative"] for r in evidence), len(ascii_words))
        for record in evidence:
            self.assertGreaterEqual(len(set(record["sentenceIds"])), 3)
            self.assertIsNotNone(record["en"])
            self.assertIsNotNone(record["vi"])
            self.assertGreaterEqual(min(record["syllableZipfCentibels"]), 400)
            self.assertLessEqual(record["word"].count(" "), 1)
            expected = "".join(
                c
                for c in unicodedata.normalize("NFD", record["token"].replace("đ", "d"))
                if not unicodedata.combining(c)
            )
            self.assertEqual(record["asciiToken"], expected)

    def test_full_checksums(self) -> None:
        checksums = json.loads((ROOT / "data/checksums.json").read_text(encoding="utf-8"))
        for name, expected in checksums.items():
            self.assertEqual(
                hashlib.sha256((ROOT / "data" / name).read_bytes()).hexdigest(), expected, name
            )

    def test_clean_directory_rebuild(self) -> None:
        (ROOT / "output").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "output") as directory:
            subprocess.run(
                [sys.executable, str(ROOT / "scripts/build_data.py"), "--out", directory],
                check=True,
                stdout=subprocess.DEVNULL,
            )
            expected = json.loads((ROOT / "data/checksums.json").read_text(encoding="utf-8"))
            for name, digest in expected.items():
                self.assertEqual(
                    hashlib.sha256((pathlib.Path(directory) / name).read_bytes()).hexdigest(),
                    digest,
                    name,
                )
            self.assertEqual(
                (pathlib.Path(directory) / "checksums.json").read_bytes(),
                (ROOT / "data/checksums.json").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
