"""Independent standard-library example. Output is a secret. Never log it."""

import argparse
import hashlib
import json
import math
import pathlib
import secrets
import unicodedata
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load(profile: str) -> list[str]:
    if profile not in {"vi", "vi-ascii", "vi-short"}:
        raise ValueError("Unknown profile")
    metadata: dict[str, Any] = json.loads((ROOT / "data/manifest.json").read_text(encoding="utf-8"))
    value = (ROOT / "data/lists" / (profile + ".txt")).read_bytes()
    if hashlib.sha256(value).hexdigest() != metadata["profiles"][profile]["sha256"]:
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
    parser.add_argument("--profile", choices=["vi", "vi-ascii", "vi-short"], default="vi")
    parser.add_argument("--bits", type=float, required=True)
    args = parser.parse_args()
    if not math.isfinite(args.bits) or args.bits <= 0 or args.bits > 4096:
        parser.error("Choose a finite bit target from 1 to 4096")
    words = load(args.profile)
    draws = math.ceil(args.bits / math.log2(len(words)))
    print("-".join(secrets.choice(words) for _ in range(draws)))


if __name__ == "__main__":
    main()
