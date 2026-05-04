#!/usr/bin/env python3
"""Compare a file hash against an expected value, or print the file hash.

Usage examples:
  python matchhash_improved.py myfile.iso
  python matchhash_improved.py sha512 myfile.iso
  python matchhash_improved.py D2C7... myfile.iso
  python matchhash_improved.py sha256 D2C7... myfile.iso
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Iterable

DEFAULT_ALGO = "sha256"
SUPPORTED_ALGOS = {name.lower() for name in hashlib.algorithms_available}


def compute_file_hash(file_path: Path, algorithm: str, chunk_size: int = 1024 * 1024) -> str:
    """Return the uppercase digest for a file using the selected algorithm."""
    hasher = hashlib.new(algorithm)
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            hasher.update(chunk)
    return hasher.hexdigest().upper()


def parse_inputs(values: Iterable[str]) -> tuple[str, str | None, Path | None]:
    """Parse positional inputs into (algorithm, expected_hash, file_path)."""
    algorithm = DEFAULT_ALGO
    expected_hash: str | None = None
    file_path: Path | None = None

    for value in values:
        candidate_path = Path(value)
        if candidate_path.is_file() and file_path is None:
            file_path = candidate_path
        elif value.lower() in SUPPORTED_ALGOS:
            algorithm = value.lower()
        else:
            expected_hash = value.strip().upper()

    return algorithm, expected_hash, file_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Print a file hash or compare it with an expected hash."
    )
    parser.add_argument(
        "items",
        nargs="+",
        help="Provide a file path, optionally an algorithm, and optionally an expected hash.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    algorithm, expected_hash, file_path = parse_inputs(args.items)

    if file_path is None:
        parser.error("No valid file path was provided.")

    if algorithm not in SUPPORTED_ALGOS:
        parser.error(f"Unsupported algorithm: {algorithm}")

    actual_hash = compute_file_hash(file_path, algorithm)

    if expected_hash is None:
        print(actual_hash)
        return 0

    if actual_hash == expected_hash:
        print("Hashes match")
        return 0

    print("Hashes do not match")
    print(f"Expected: {expected_hash}")
    print(f"Actual:   {actual_hash}")
    return 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FileNotFoundError as exc:
        print(f"File not found: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except PermissionError as exc:
        print(f"Permission denied: {exc}", file=sys.stderr)
        raise SystemExit(2)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)
