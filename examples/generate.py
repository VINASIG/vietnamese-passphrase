"""Independent standard-library example. Output is a secret. Never log it."""

import argparse
import hashlib
import json
import math
import pathlib
import secrets
import sys
import unicodedata
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


def resolve(profile: str) -> tuple[str, dict[str, Any]]:
    catalog: dict[str, Any] = json.loads(
        (ROOT / "research/profile-catalog.json").read_text(encoding="utf-8")
    )
    for name, item in catalog["profiles"].items():
        if profile == name or profile == item["dataProfile"]:
            return name, item
    raise ValueError("Unknown profile")


def load(profile: str) -> list[str]:
    _, item = resolve(profile)
    source = item["dataProfile"]
    if not isinstance(source, str) or source not in {
        "vi",
        "vi-ascii",
        "vi-short",
        "vi-display",
        "vi-fused",
        "vi-ascii-display",
        "vi-ascii-native",
        "vi-distinct",
    }:
        raise ValueError("Unknown profile")
    historical = source in {"vi", "vi-ascii", "vi-short"}
    base = ROOT / ("data" if historical else "research/experimental/2026-10-06.agent-1")
    metadata: dict[str, Any] = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    value = (base / ("lists/" if historical else "") / (source + ".txt")).read_bytes()
    if hashlib.sha256(value).hexdigest() != metadata["profiles"][source]["sha256"]:
        raise ValueError("Wordlist checksum mismatch")
    text = value.decode("utf-8", errors="strict")
    if not text.endswith("\n") or "\r" in text or text.startswith("\ufeff"):
        raise ValueError("Invalid list framing")
    words = text[:-1].split("\n")
    if len(words) < 2 or len(set(words)) != len(words) or words != sorted(words):
        raise ValueError("Invalid vocabulary")
    if any(
        w != unicodedata.normalize("NFC", w) or not w or any(c.isspace() for c in w) for w in words
    ):
        raise ValueError("Invalid word token")
    return words


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--bits", type=float, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.bits) or args.bits <= 0 or args.bits > 4096:
        parser.error("Choose a finite bit target from 1 to 4096")
    try:
        name, item = resolve(args.profile)
    except ValueError as error:
        parser.error(str(error))
    if not item["generation"] or item["dataProfile"] in {"vi-short", "vi-ascii-native"}:
        parser.error(name + " is unavailable for generation. " + item["limitation"])
    if args.profile != name:
        print("Deprecated profile alias. Use " + name + ".", file=sys.stderr)
    print(item["status"] + ". " + item["limitation"], file=sys.stderr)
    words = load(args.profile)
    draws = math.ceil(args.bits / math.log2(len(words)))
    print("-".join(secrets.choice(words) for _ in range(draws)))


if __name__ == "__main__":
    main()
