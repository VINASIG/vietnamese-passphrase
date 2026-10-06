"""Adversarial release identity and independent example-policy fixtures."""

import contextlib
import copy
import hashlib
import importlib
import io
import json
import pathlib
import shutil
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
package_release = importlib.import_module("package_release")


class PublicationTest(unittest.TestCase):
    def fixture(self, root: pathlib.Path, version: str = "0.2.5") -> None:
        for filename, value in {
            "release.json": {
                "schema": 1,
                "tag": "v" + version,
                "channel": "research-preview",
                "notes": "docs/releases/v" + version + ".md",
            },
            "package.json": {"version": version, "private": True, "packageManager": "npm@12.2.0"},
            "package-lock.json": {"version": version, "packages": {"": {"version": version}}},
        }.items():
            (root / filename).write_text(json.dumps(value), encoding="utf-8")
        (root / ".node-version").write_text("24.21.0\n", encoding="ascii")
        (root / "requirements-dev.txt").write_text("# synthetic test lock\n", encoding="ascii")
        notes = root / "docs/releases" / ("v" + version + ".md")
        notes.parent.mkdir(parents=True, exist_ok=True)
        notes.write_text(
            "# Vietnamese Passphrase " + version + "\n\nRelease channel - research preview\n",
            encoding="utf-8",
        )

    def asset_fixture(self, root: pathlib.Path) -> pathlib.Path:
        release = release_metadata.validate(root)
        folder = root / "assets"
        folder.mkdir()
        names = ["source-v0.2.5.zip", "vinasig-vietnamese-passphrase-0.2.5.zip"]
        for name in names:
            (folder / name).write_bytes(b"separately authored fixture bytes")
        hashes = {name: hashlib.sha256((folder / name).read_bytes()).hexdigest() for name in names}
        record = {
            "schema": 2,
            "sourceCommit": "a" * 40,
            "packageVersion": "0.2.5",
            "releaseTag": "v0.2.5",
            "releaseNotesSha256": release.notes_sha256,
            "environmentRecords": release_metadata.environment_records(),
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
        return folder

    def environment_fixture(
        self, root: pathlib.Path, assets: pathlib.Path, label: str = "ubuntu-24.04"
    ) -> dict[str, Any]:
        selected_os, image_os, python = release_metadata.BUILD_ENVIRONMENTS[label]
        return {
            "schema": 1,
            "sourceCommit": "a" * 40,
            "packageVersion": "0.2.5",
            "releaseTag": "v0.2.5",
            "runner": {
                "label": label,
                "os": selected_os,
                "arch": "X64",
                "environment": "github-hosted",
                "imageOS": image_os,
                "imageVersion": "20260927.320.1",
                "release": "synthetic OS release",
                "version": "synthetic OS version",
            },
            "tools": {
                "python": python,
                "pythonImplementation": "CPython",
                "unicode": "synthetic Unicode version",
                "node": "v24.21.0",
                "npm": "12.2.0",
                "git": "synthetic Git version",
            },
            "run": {"id": "1234", "attempt": "1", "ref": "refs/tags/v0.2.5"},
            "artifacts": {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in assets.iterdir()
            },
            "dependencyLocks": {
                name: hashlib.sha256((root / name).read_bytes()).hexdigest()
                for name in ("package-lock.json", "requirements-dev.txt")
            },
        }

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
            folder = self.asset_fixture(root)
            release_metadata.validate_assets(folder, release, "a" * 40)
            with self.assertRaises(ValueError):
                release_metadata.validate_assets(folder, release, "b" * 40)
            (folder / "source-v0.2.5.zip").write_bytes(b"corrupted archive")
            with self.assertRaises(ValueError):
                release_metadata.validate_assets(folder, release, "a" * 40)

    def test_environment_requires_observed_hosted_image_and_pinned_tools(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            release = release_metadata.validate(root)
            folder = self.asset_fixture(root)
            path = root / "environment-ubuntu-24.04.json"
            original = self.environment_fixture(root, folder)
            path.write_text(json.dumps(original), encoding="utf-8")
            release_metadata.validate_environment(
                path, "ubuntu-24.04", folder, release, "a" * 40, root
            )
            for section, key, wrong in (
                ("runner", "imageVersion", None),
                ("runner", "imageVersion", "unknown"),
                ("runner", "imageOS", "ubuntu26"),
                ("runner", "environment", "self-hosted"),
                ("runner", "arch", "ARM64"),
                ("tools", "python", "3.12.13"),
                ("tools", "node", "v24.22.0"),
                ("tools", "npm", "12.2.1"),
                ("run", "ref", "refs/heads/main"),
                ("run", "id", "unknown"),
                ("run", "attempt", "0"),
            ):
                changed = copy.deepcopy(original)
                changed[section][key] = wrong
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(section=section, key=key), self.assertRaises(ValueError):
                    release_metadata.validate_environment(
                        path, "ubuntu-24.04", folder, release, "a" * 40, root
                    )

    def test_environment_cannot_be_substituted_between_artifacts_or_sources(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            release = release_metadata.validate(root)
            folder = self.asset_fixture(root)
            path = root / "environment-ubuntu-24.04.json"
            original = self.environment_fixture(root, folder)
            for key, wrong in (
                ("sourceCommit", "b" * 40),
                ("releaseTag", "v0.2.4"),
                ("packageVersion", "0.2.4"),
                ("artifacts", {}),
                ("dependencyLocks", {}),
                ("runner", []),
            ):
                changed = {**original, key: wrong}
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.subTest(key=key), self.assertRaises(ValueError):
                    release_metadata.validate_environment(
                        path, "ubuntu-24.04", folder, release, "a" * 40, root
                    )
            path.write_text(json.dumps(original), encoding="utf-8")
            (root / "requirements-dev.txt").write_bytes(b"changed dependency lock")
            with self.assertRaises(ValueError):
                release_metadata.validate_environment(
                    path, "ubuntu-24.04", folder, release, "a" * 40, root
                )
            path.write_bytes(b'{"truncated":')
            with self.assertRaises(ValueError):
                release_metadata.validate_environment(
                    path, "ubuntu-24.04", folder, release, "a" * 40, root
                )

    def test_environment_pair_requires_the_same_exact_tag_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            release = release_metadata.validate(root)
            assets = self.asset_fixture(root)
            builds = root / "builds"
            for label, name in release_metadata.environment_records().items():
                folder = builds / label
                shutil.copytree(assets, folder / "release")
                environment = folder / "environment"
                environment.mkdir()
                (environment / name).write_text(
                    json.dumps(self.environment_fixture(root, assets, label)), encoding="utf-8"
                )
            release_metadata.validate_environments(builds, release, "a" * 40, root)
            path = builds / "windows-2025-vs2026/environment/environment-windows-2025-vs2026.json"
            changed = json.loads(path.read_text(encoding="utf-8"))
            changed["run"]["attempt"] = "2"
            path.write_text(json.dumps(changed), encoding="utf-8")
            with self.assertRaises(ValueError):
                release_metadata.validate_environments(builds, release, "a" * 40, root)

    def test_capture_does_not_dump_unrelated_environment_or_overwrite_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            self.fixture(root)
            folder = self.asset_fixture(root)
            path = root / "environment-ubuntu-24.04.json"
            environment = {
                "RUNNER_OS": "Linux",
                "RUNNER_ARCH": "X64",
                "RUNNER_ENVIRONMENT": "github-hosted",
                "ImageOS": "ubuntu24",
                "ImageVersion": "20260927.320.1",
                "GITHUB_RUN_ID": "1234",
                "GITHUB_RUN_ATTEMPT": "1",
                "GITHUB_REF": "refs/heads/main",
                "SECRET_TEST_CANARY": "must-not-be-persisted",
            }
            with (
                mock.patch.dict(package_release.os.environ, environment, clear=True),
                mock.patch.object(package_release, "ROOT", root),
                mock.patch.object(package_release.shutil, "which", return_value="npm"),
                mock.patch.object(
                    package_release.platform, "python_version", return_value="3.12.14"
                ),
                mock.patch.object(
                    package_release.platform, "python_implementation", return_value="CPython"
                ),
                mock.patch.object(
                    package_release.platform, "release", return_value="synthetic OS release"
                ),
                mock.patch.object(
                    package_release.platform, "version", return_value="synthetic OS version"
                ),
                mock.patch.object(
                    package_release.subprocess,
                    "check_output",
                    side_effect=["a" * 40, "v24.21.0", "12.2.0", "synthetic Git version"] * 2,
                ),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                package_release.record_environment(path, "ubuntu-24.04", folder)
                with self.assertRaises(FileExistsError):
                    package_release.record_environment(path, "ubuntu-24.04", folder)
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("must-not-be-persisted", content)
            self.assertNotIn("SECRET_TEST_CANARY", content)

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
            workflow.index("--assets builds/ubuntu-24.04/release"),
            workflow.index("gh release create"),
        )
        self.assertLess(workflow.index("--environments builds"), workflow.index("subject-path:"))
        self.assertIn("--latest=false", workflow)


if __name__ == "__main__":
    unittest.main()
