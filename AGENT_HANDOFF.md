# AGENT_HANDOFF.md (pointer)

**Canonical durable handoff:** [`HANDOFF.md`](HANDOFF.md) — single source of truth. Read it in full before starting. Do not create parallel handoff/session docs.

- **Refreshed:** 2026-11-16T13:39:35Z (UTC)
- **Git HEAD:** `d23011e` (local == remote `origin/main` `d23011e`; persistence verified). Working tree clean.
- **P19-1:** commit `b641b7a` (`ci: ship P19-1 bab-gate enforcement job`) on local branch `kilo-p19-1-push`, rebased onto `d23011e`, ready to fast-forward push. **NOT on `origin/main`** — push rejected by GitHub: `workflows` write permission required for `.github/workflows/main.yml`; repo-scoped token has `contents: write` only. Needs maintainer `workflows` access, web UI amendment, or PAT with `workflows:write`.
- **Binding task:** `HANDOFF.md` → **P19-1 — unblock CI enforcement push** (`b641b7a` carries `bab-gate` job; verify `git ls-remote origin refs/heads/main` matches, then watch `bab-gate` CI GREEN on `origin/main`). After P19-1 DoD, proceed to **P19-2 — REAL-DATA INGEST + LIVE-FILL FIDELITY HARDENING**.
- **Verified done (do not redo):** P17-1, P17-2, P18-1, P18-2, P18-3 — see `HANDOFF.md`.
- **Local gates this session:** `ruff` clean. (Prior verified: `bab_reconcile_gate.sh` GREEN; `BAB_GATE_MIN_COVERAGE=98.5 bash scripts/bab_gate.sh` GREEN 6215 passed / 35 skipped / 99%; `BAB_GATE_MIN_COVERAGE=99.5` RED fail-closed proven.)

If evidence conflicts with live output, trust live output and update `HANDOFF.md`.
