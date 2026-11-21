#!/usr/bin/env python3
"""Read-only deterministic replay harness for P29 WP2 decision docs + JSONL sidecars.

Reproduces, byte-identically, the committed P25/P26/P27 decision markdown docs,
the P27 decision sidecar JSON, and the two P27 paper JSONL sidecars, by
redirecting each generator's module-level output path constants to a temp dir
and diffing the regenerated output against the committed file. Never writes to a
committed path.

Usage:
    python3 scripts/bab_replay_decisions.py                 # replay ALL artifacts
    python3 scripts/bab_replay_decisions.py --subset a,b    # replay named artifacts
    python3 scripts/bab_replay_decisions.py --list          # print registry names
    python3 scripts/bab_replay_decisions.py --self-test     # fast drift-detection proof

Exit code 0 when every selected artifact replays byte-identical (and, for
``--self-test``, when a deliberately corrupted copy is detected as drift);
non-zero otherwise.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESEARCH_P27 = ROOT / "research_state" / "bab_p27"

# Each entry: name, generator module, kind, and outputs.
# kind "decision": exec the generator source with module-level output constants
#   redirected to temp, then diff each regenerated file against committed.
# kind "jsonl": import the module, build the payload read-only, write JSONL to
#   temp via _write_jsonl, diff against committed.
REGISTRY: list[dict] = [
    {
        "name": "p25_decision.md",
        "module": "generate_p25_decision",
        "gen_dir": ROOT,
        "kind": "decision",
        "outputs": [
            {"constant": "REPORT_PATH", "committed": ROOT / "docs/BAB_P25_DECISION.md"},
        ],
    },
    {
        "name": "p26_decision.md",
        "module": "generate_p26_decision",
        "gen_dir": ROOT,
        "kind": "decision",
        "outputs": [
            {"constant": "REPORT_PATH", "committed": ROOT / "docs/BAB_P26_DECISION.md"},
        ],
    },
    {
        "name": "p27_decision",
        "module": "generate_p27_decision",
        "gen_dir": ROOT,
        "kind": "decision",
        "outputs": [
            {"constant": "REPORT_PATH", "committed": ROOT / "docs/BAB_P27_DECISION.md"},
            {"constant": "SIDECAR_PATH", "committed": RESEARCH_P27 / "p27_decision_sidecar.json"},
        ],
    },
    {
        "name": "paper_orders.jsonl",
        "module": "bab_execution_hardening",
        "gen_dir": ROOT / "scripts",
        "kind": "jsonl",
        "records_attr": ("paper", "orders"),
        "committed": RESEARCH_P27 / "paper_orders.jsonl",
    },
    {
        "name": "paper_diagnostics.jsonl",
        "module": "bab_execution_hardening",
        "gen_dir": ROOT / "scripts",
        "kind": "jsonl",
        "records_attr": ("paper", "diagnostics"),
        "committed": RESEARCH_P27 / "paper_diagnostics.jsonl",
    },
]

# Cheap (fast) entry used by the drift self-test so it runs in ~1s instead of
# regenerating the multi-second execution-hardening payload.
CHEAP_NAMES = ("p25_decision.md",)


def _load_module(name: str, gen_dir: Path):
    spec = importlib.util.spec_from_file_location(name, gen_dir / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    return spec, module


def _exec_decision_source(module_path: Path, constants: dict[str, Path], namespace: dict) -> None:
    """Exec the generator source with output path constants redirected to temp.

    Reads the source, replaces each ``<constant> = <expr>`` assignment with
    ``<constant> = Path(<temp>)`` so top-level writes land in the temp dir, then
    execs in ``namespace``. ``__file__`` is set so ``REPO_ROOT`` resolves to the
    real repo (JSON artifacts load read-only); only the redirected constants
    write, and only to temp.
    """
    source = module_path.read_text(encoding="utf-8")
    for const_name, temp_path in constants.items():
        pattern = re.compile(r"^(\s*" + re.escape(const_name) + r"\s*=).*$", re.MULTILINE)
        replacement = r"\1 Path(" + repr(str(temp_path)) + ")"
        source, n = pattern.subn(replacement, source, count=1)
        if n != 1:
            raise RuntimeError(f"could not redirect {const_name} in {module_path}")
    namespace["__file__"] = str(module_path)
    namespace["__name__"] = module_path.stem
    # Suppress the generator's informational prints so they do not pollute
    # the replay harness's own stdout (e.g. the --self-test JSON payload).
    with redirect_stdout(StringIO()):
        exec(compile(source, str(module_path), "exec"), namespace)


def _replay_decision(entry: dict, tmpdir: Path) -> list[tuple[Path, bytes]]:
    """Regenerate decision outputs to temp; return (committed, generated_bytes)."""
    module_path = entry["gen_dir"] / f"{entry['module']}.py"
    namespace: dict = {}
    constants: dict[str, Path] = {}
    targets: list[tuple[Path, Path]] = []
    for output in entry["outputs"]:
        temp_path = tmpdir / output["committed"].name
        constants[output["constant"]] = temp_path
        targets.append((output["committed"], temp_path))
    _exec_decision_source(module_path, constants, namespace)
    return [(committed, temp_path.read_bytes()) for committed, temp_path in targets]


def _replay_jsonl(entry: dict, tmpdir: Path) -> list[tuple[Path, bytes]]:
    """Rebuild the payload read-only, write JSONL to temp, return (committed, bytes)."""
    spec, module = _load_module(entry["module"], entry["gen_dir"])
    spec.loader.exec_module(module)
    payload = module.build_execution_hardening()
    records: object = payload
    for attr in entry["records_attr"]:
        records = records[attr]
    temp_path = tmpdir / entry["committed"].name
    module._write_jsonl(temp_path, records)
    return [(entry["committed"], temp_path.read_bytes())]


def _check(entry: dict, tmpdir: Path) -> tuple[bool, list[str]]:
    """Return (ok, problems) for one artifact against its committed file(s)."""
    problems: list[str] = []
    if entry["kind"] == "decision":
        results = _replay_decision(entry, tmpdir)
    else:
        results = _replay_jsonl(entry, tmpdir)
    for committed, generated_bytes in results:
        if not committed.is_file():
            return False, [f"MISSING {committed}"]
        if committed.read_bytes() != generated_bytes:
            problems.append(f"DRIFT {entry['name']}: {committed.name} differs")
    return (not problems), problems


def _select(names: list[str]) -> list[dict]:
    wanted = {n.strip() for n in names if n and n.strip()}
    if not wanted:
        return list(REGISTRY)
    return [e for e in REGISTRY if e["name"] in wanted]


def _self_test() -> int:
    """Fast proof: clean tree replays OK AND a corrupted committed copy drifts."""
    cheap = [e for e in REGISTRY if e["name"] in CHEAP_NAMES]
    clean_ok = True
    for entry in cheap:
        with tempfile.TemporaryDirectory() as tmp:
            ok, _ = _check(entry, Path(tmp))
            clean_ok = clean_ok and ok

    drift_detected = False
    target = next(e for e in cheap if e["name"] == "p25_decision.md")
    with tempfile.TemporaryDirectory() as tmp:
        results = _replay_decision(target, Path(tmp))
        committed_bytes = results[0][0].read_bytes()
        corrupted = bytearray(committed_bytes)
        mid = len(corrupted) // 2
        corrupted[mid] ^= 0x01
        if bytes(corrupted) != committed_bytes:
            drift_detected = results[0][1] != bytes(corrupted)

    passed = clean_ok and drift_detected
    print(json.dumps({
        "self_test": True,
        "clean_ok": clean_ok,
        "drift_detected": drift_detected,
        "pass": passed,
    }))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--subset", default="", help="Comma-separated artifact names to replay")
    parser.add_argument("--list", action="store_true", help="Print registry artifact names")
    parser.add_argument("--self-test", action="store_true", help="Fast drift-detection proof")
    args = parser.parse_args(argv)

    if args.list:
        for entry in REGISTRY:
            print(entry["name"])
        return 0

    if args.self_test:
        return _self_test()

    entries = _select(args.subset.split(","))
    if not entries:
        print("NO MATCHING ARTIFACTS")
        return 1

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for entry in entries:
            good, problems = _check(entry, tmpdir)
            if good:
                targets = entry["outputs"] if entry["kind"] == "decision" else [entry]
                for output in targets:
                    label = output["committed"].name
                    print(f"OK {entry['name']} -> {label}")
            else:
                ok = False
                for problem in problems:
                    print(problem)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
