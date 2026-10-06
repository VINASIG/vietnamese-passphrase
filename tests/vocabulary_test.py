"""Independent small-space oracles and adversarial fixtures for vocabulary diagnostics."""

import hashlib
import itertools
import json
import pathlib
import sys
import tempfile
import unittest
from typing import Any

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from experiment_profiles import content_candidates, distinct_subset  # noqa: E402
from vocabulary_audit import (  # noqa: E402
    close_pairs,
    collision_groups,
    external_counts,
    fold,
    levenshtein,
    telex,
    without_tone,
)


def oracle(a: str, b: str) -> int:
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i, j in itertools.product(range(1, len(a) + 1), range(1, len(b) + 1)):
        table[i][j] = min(
            table[i - 1][j] + 1,
            table[i][j - 1] + 1,
            table[i - 1][j - 1] + int(a[i - 1] != b[j - 1]),
        )
    return table[-1][-1]


class VocabularyTests(unittest.TestCase):
    def test_corrupt_external_evidence_and_malformed_rows(self) -> None:
        with tempfile.TemporaryDirectory() as folder:
            source = pathlib.Path(folder)
            data = b"# sent_id = one\n1\tban\t_\tNOUN\t_\t_\t0\troot\t_\t_\n"
            entry: dict[str, Any] = {
                "path": "fixture.conllu",
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
            manifest = {"source": "local-fixture", "revision": "fixture", "files": [entry]}
            (source / entry["path"]).write_bytes(data)
            (source / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            self.assertEqual(external_counts(source)[0], {"ban": 1})
            (source / entry["path"]).write_bytes(data + b"bad")
            with self.assertRaisesRegex(ValueError, "digest"):
                external_counts(source)
            bad = b"1\ttoo-few-columns\n"
            entry.update(bytes=len(bad), sha256=hashlib.sha256(bad).hexdigest())
            (source / entry["path"]).write_bytes(bad)
            (source / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Malformed"):
                external_counts(source)

    def test_exhaustive_neighborhood_coverage(self) -> None:
        values = ["".join(x) for n in range(4) for x in itertools.product("aá_", repeat=n)]
        for radius in [1, 2]:
            expected = [
                (i, j, oracle(a, b))
                for i, a in enumerate(values)
                for j, b in enumerate(values)
                if i < j and oracle(a, b) <= radius
            ]
            self.assertEqual(close_pairs(values, radius), expected)
        for a, b in itertools.product(values, repeat=2):
            self.assertEqual(levenshtein(a, b), oracle(a, b))

    def test_lossy_transforms_are_not_semantic_aliases(self) -> None:
        self.assertEqual(fold("bàn"), fold("bán"))
        self.assertEqual(fold("đá"), "da")
        self.assertEqual(without_tone("đắ"), "đă")
        self.assertNotEqual(without_tone("đắ"), without_tone("dá"))
        self.assertEqual(
            collision_groups(["bàn", "bán", "mèo"], fold)[0]["members"], ["bàn", "bán"]
        )
        self.assertEqual(levenshtein("é", "e\u0301"), 2)
        self.assertEqual(telex("đặng"), "ddawngj")
        self.assertEqual(telex("bánh_mì"), "banhs_mif")

    def test_content_and_aliases_fail_closed(self) -> None:
        policy = {
            "categories": {"test": {"tokens": ["dâm"]}},
            "variantFamilies": [{"members": ["tai", "tay"], "representative": "tai"}],
        }
        values, ledger = content_candidates(["dâm", "tai", "tay", "buồn"], policy)
        self.assertEqual(values, ["tai", "buồn"])
        self.assertEqual(ledger[-1]["disposition"], "candidate")
        with self.assertRaises(ValueError):
            content_candidates(["tai", "tay"], policy)

    def test_distinction_constraint_is_maximal_not_maximum(self) -> None:
        values = ["ban", "bàn", "bán", "mèo", "mép", "công_ty", "công_ti"]
        chosen = distinct_subset(values)
        self.assertEqual(close_pairs(chosen, 1), [])
        for rejected in set(values) - set(chosen):
            self.assertTrue(any(oracle(rejected, accepted) == 1 for accepted in chosen))
        self.assertEqual(chosen, distinct_subset(list(reversed(values))))


if __name__ == "__main__":
    unittest.main()
