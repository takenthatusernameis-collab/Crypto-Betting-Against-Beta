#!/usr/bin/env python3
"""Deterministic replay harness for P27 WP0-WP2 JSON artifacts.

Regenerates each committed artifact from its generator into a temp dir and
byte-diffs against the committed file. Fails non-zero on any drift. Read-only
on committed P27 files.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENS = [
    ("bab_execution_hardening", "execution_hardening.json"),
    ("bab_risk_controls", "risk_controls.json"),
    ("bab_reconciliation_e2e", "reconciliation_e2e.json"),
]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    committed_dir = ROOT / "research_state" / "bab_p27"
    tmp = Path(tempfile.mkdtemp())
    ok = True
    for modname, fname in GENS:
        mod = _load(modname)
        build_name = {
            "bab_execution_hardening": "build_execution_hardening",
            "bab_risk_controls": "build_risk_controls",
            "bab_reconciliation_e2e": "build_reconciliation_e2e",
        }[modname]
        payload = getattr(mod, build_name)()
        payload2 = getattr(mod, build_name)()
        identical = json.dumps(payload, sort_keys=True) == json.dumps(payload2, sort_keys=True)
        payload["determinism"] = {"byte_identical": identical, "seed": mod.SEED}
        outdir = tmp / modname
        outdir.mkdir()
        mod.write_artifacts(payload, outdir)
        committed = committed_dir / fname
        regenerated = outdir / fname
        if not committed.exists() or not regenerated.exists():
            print(f"MISSING {fname}")
            ok = False
            continue
        if committed.read_bytes() != regenerated.read_bytes():
            print(f"DRIFT {fname}")
            ok = False
        else:
            print(f"OK {fname}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
