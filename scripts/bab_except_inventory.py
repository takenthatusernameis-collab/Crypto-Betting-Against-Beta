#!/usr/bin/env python3
"""Inventory broad/silent exception handlers in the BAB product code (P15).

The P14 coverage campaign closed at TOTAL 99% (>= 98.5% floor). The remaining
misses are proven-unreachable defensive branches, so further coverage chasing is
not productive. The real engineering debt is the large number of broad
``except Exception`` handlers -- many of them silently ``pass`` -- that can hide
data-integrity and execution-safety defects.

This script is the deterministic P15 work queue. It parses the product modules
with :mod:`ast` (no imports, no side effects) and reports, per file:

  * ``broad``  -- handlers whose type is ``Exception``/``BaseException``/bare
  * ``silent`` -- handlers whose body is exactly ``pass`` (or ``pass`` + docstring)

Usage:
  python3 scripts/bab_except_inventory.py            # human summary
  python3 scripts/bab_except_inventory.py --json     # machine-readable
  python3 scripts/bab_except_inventory.py --file data_loader.py
  python3 scripts/bab_except_inventory.py --silent-only

Exit code is 0 unless the arguments are invalid, so it is safe in CI as a
reporting step. Use ``--min-silent N`` to fail closed once the silent-handler
count drops below a target (e.g. a future release gate).
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PRODUCT_DIR = REPO_ROOT / "strategies" / "betting_against_beta"

_BROAD_NAMES = {"Exception", "BaseException"}


def _handler_type_name(node: ast.ExceptHandler) -> str | None:
    """Return the textual exception type for a handler (None for bare except)."""
    if node.type is None:
        return None
    if isinstance(node.type, ast.Name):
        return node.type.id
    if isinstance(node.type, ast.Attribute):
        return node.type.attr
    if isinstance(node.type, ast.Tuple):
        parts = []
        for elt in node.type.elts:
            if isinstance(elt, ast.Name):
                parts.append(elt.id)
            elif isinstance(elt, ast.Attribute):
                parts.append(elt.attr)
            else:
                parts.append(ast.dump(elt))
        return "|".join(parts)
    return ast.dump(node.type)


def _is_broad(type_name: str | None) -> bool:
    if type_name is None:
        return True
    return any(part.strip() in _BROAD_NAMES for part in type_name.split("|"))


def _is_silent(node: ast.ExceptHandler) -> bool:
    """True when the handler does nothing but ``pass`` (docstring allowed)."""
    body = list(node.body)
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    return len(body) == 1 and isinstance(body[0], ast.Pass)


def scan_file(path: Path) -> list[dict]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: list[dict] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        type_name = _handler_type_name(node)
        if not _is_broad(type_name):
            continue
        found.append(
            {
                "file": path.name,
                "line": node.lineno,
                "type": type_name or "<bare>",
                "silent": _is_silent(node),
            }
        )
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON")
    parser.add_argument("--file", help="only scan this product filename")
    parser.add_argument("--silent-only", action="store_true", help="only silent handlers")
    parser.add_argument(
        "--min-silent",
        type=int,
        default=None,
        help="exit 1 if the silent-handler count is below N (release gate)",
    )
    args = parser.parse_args(argv)

    paths = sorted(PRODUCT_DIR.glob("*.py"))
    if args.file:
        paths = [p for p in paths if p.name == args.file]
        if not paths:
            print(f"no such product file: {args.file}", file=sys.stderr)
            return 2

    records: list[dict] = []
    for path in paths:
        records.extend(scan_file(path))

    if args.silent_only:
        records = [r for r in records if r["silent"]]

    per_file: dict[str, dict[str, int]] = {}
    for rec in records:
        entry = per_file.setdefault(rec["file"], {"broad": 0, "silent": 0})
        entry["broad"] += 1
        if rec["silent"]:
            entry["silent"] += 1

    total_broad = len(records)
    total_silent = sum(1 for r in records if r["silent"])

    if args.json:
        json.dump(
            {
                "product_dir": str(PRODUCT_DIR.relative_to(REPO_ROOT)),
                "total_broad": total_broad,
                "total_silent": total_silent,
                "per_file": per_file,
                "handlers": records,
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
    else:
        print(f"broad handlers: {total_broad}  silent: {total_silent}")
        print(f"{'file':<20} {'broad':>6} {'silent':>7}")
        for name in sorted(per_file):
            entry = per_file[name]
            print(f"{name:<20} {entry['broad']:>6} {entry['silent']:>7}")

    if args.min_silent is not None and total_silent < args.min_silent:
        print(
            f"silent-handler floor not met: {total_silent} < {args.min_silent}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
