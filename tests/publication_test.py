"""Adversarial release identity and independent example-policy fixtures."""

import contextlib
import hashlib
import importlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from typing import Any
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "examples"))
generate = importlib.import_module("generate")
release_metadata = importlib.import_module("release_metadata")


class PublicationTest(unittest.TestCase):
    def fixture(self, root: pathlib.Path, version: str = "0.2.5") -> None:
        for filename, value in {
            "release.json": {
                "schema": 1,
                "tag": "v" + version,
                "channel": "research-preview",
                "notes": "docs/releases/v" + version + ".md",
            },
            "package.json": {"version": version, "private": True},
            "package-lock.json": {"version": version, "packages": {"": {"version": version}}},
        }.items():
            (root / filename).write_text(json.dumps(value), encoding="utf-8")
        notes = root / "docs/releases" / ("v" + version + ".md")
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text(
            "# Vietnamese Passphrase " + version + "\n\nRelease channel - research preview\n",
            encoding="utf-8",
        )

    def test_future_patch_selects_its_own_notes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            result = release_metadata.validate(root, "v0.2.5")
            self.assertEqual(result.notes, "docs/releases/v0.2.5.md")
            self.assertIn("0.2.5", result.title)

    def test_unsupported_or_injected_tags_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            for tag in (
                "v0.2.3",
                "v0.2.05",
                "v0.2.5-rc1",
                "v0.3.0",
                "v0.2.5\nnotes=other",
                "v0.2.5/../x",
            ):
                with self.subTest(tag=tag), self.assertRaises(ValueError):
                    release_metadata.validate(root, tag)

    def test_missing_or_stale_notes_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            notes = root / "docs/releases/v0.2.5.md"
            for content in (
                "# Vietnamese Passphrase 0.2.3\n\nRelease channel - research preview\n",
                "# Vietnamese Passphrase 0.2.5\n\nStable\n",
            ):
                notes.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    release_metadata.validate(root)
            notes.unlink()
            with self.assertRaises(ValueError):
                release_metadata.validate(root)
            self.fixture(root)
            metadata: dict[str, Any] = json.loads((root / "release.json").read_text())
            metadata["notes"] = "docs/releases/v0.2.3.md"
            (root / "release.json").write_text(json.dumps(metadata), encoding="utf-8")
            with self.assertRaises(ValueError):
                release_metadata.validate(root)

    def test_lockfile_and_channel_mismatch_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            for filename, changed in (
                ("package.json", {"version": "0.2.4", "private": True}),
                ("package.json", {"version": "0.2.5", "private": False}),
                ("package-lock.json", {"version": "0.2.5", "packages": {"": {"version": "0.2.3"}}}),
                ("release.json", {"tag": "v0.2.5", "schema": 1, "channel": "stable"}),
            ):
                self.fixture(root)
                (root / filename).write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(filename=filename), self.assertRaises(ValueError):
                    release_metadata.validate(root)

    def test_artifact_identity_and_integrity_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            release = release_metadata.validate(root)
            folder = root / "assets"
            folder.mkdir()
            names = ["source-v0.2.5.zip", "vinasig-vietnamese-passphrase-0.2.5.zip"]
            for name in names:
                (folder / name).write_bytes(b"independent fixture bytes")
            hashes = {
                name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names
            }
            record = {
                "sourceCommit": "a" * 40,
                "packageVersion": "0.2.5",
                "releaseTag": "v0.2.5",
                "releaseNotesSha256": release.notes_sha256,
                "sha256": hashes,
            }
            (folder / "build-record.json").write_text(json.dumps(record), encoding="utf-8")
            checksums = {
                **hashes,
                "build-record.json": hashlib.sha256(
                    (folder / "build-record.json").read_bytes()
                ).hexdigest(),
            }
            (folder / "SHA256SUMS.txt").write_bytes(
                "".join(f"{value}  {name}\n" for name, value in sorted(checksums.items())).encode(
                    "ascii"
                )
            )
            release_metadata.validate_assets(folder, release, "a" * 40)
            with self.assertRaises(ValueError):
                release_metadata.validate_assets(folder, release, "b" * 40)
            (folder / names[0]).write_bytes(b"corrupted archive")
            with self.assertRaises(ValueError):
                release_metadata.validate_assets(folder, release, "a" * 40)

    def test_python_example_blocks_diagnostics_and_controls_before_randomness(self) -> None:
        for profile in (
            "vi-short",
            "diagnostic-short-v1",
            "vi-ascii-native",
            "control-paired-native",
        ):
            output = io.StringIO()
            with (
                mock.patch.object(
                    sys, "argv", ["generate.py", "--profile", profile, "--bits", "80"]
                ),
                mock.patch.object(
                    generate.secrets, "choice", side_effect=AssertionError("must not sample")
                ),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit),
            ):
                generate.main()
            self.assertEqual(output.getvalue(), "")
        self.assertEqual(len(generate.load("experimental-agent-vi")), 2966)

    def test_workflow_cannot_use_a_hardcoded_release_notes_file(self) -> None:
        workflow = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertNotIn("--notes-file docs/releases/", workflow)
        self.assertIn('--notes-file "$RELEASE_NOTES"', workflow)
        self.assertLess(
            workflow.index("--assets builds/ubuntu-latest"), workflow.index("gh release create")
        )
        self.assertIn("--latest=false", workflow)


if __name__ == "__main__":
    unittest.main()
