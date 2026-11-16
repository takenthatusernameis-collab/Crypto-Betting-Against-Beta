# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T13:29:57Z (UTC)
- **Git HEAD:** `3707ee5` (local == remote `origin/main` `3707ee5`; persistence verified). P19-1 commit `de9eeac` preserved locally on branch `kilo-recovery-session-105` (also byte-identical as unstaged worktree change on `main`), **NOT on `origin/main`** — blocked by GH `workflows` permission policy. Recovery bundle `/tmp/kilo-recovery-session-105.bundle` + branch `kilo-recovery-session-105` at pre-recovery HEAD `2b72ed8`.
- **Binding task:** `HANDOFF.md` → **P19-1 — unblock CI enforcement push** (`de9eeac` carries `bab-gate` job; needs maintainer `workflows` write, web UI amendment, or PAT with `workflows:write`; verify `git ls-remote origin refs/heads/main` matches, then watch `bab-gate` CI GREEN on `origin/main`). After P19-1 DoD, proceed to **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING**.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3 — see `HANDOFF.md`.
- **Local gates this session:** `ruff` clean; `bab_reconcile_gate.sh` GREEN (drift rc=2, clean/emit-only rc=0). (Prior verified: `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN 6215 passed / 35 skipped / 99%; `BAB_GATE_MIN_COVERAGE=99.5 bash scripts/bab_gate.sh` RED fail-closed proven.)

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
