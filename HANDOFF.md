# HANDOFF — Crypto-Betting-Against-Beta

**Canonical durable handoff (single source of truth).**
**Timestamp (UTC):** 2026-11-14T14:28:09Z
**Repo:** `Crypto-Betting-Against-Beta`
**HEAD:** `3df7d45` (`chore: capture completed workflow run diagnostics`) — trust live git output over this file if they differ.
**Branch:** `main`

## INITIAL TASK MESSAGE (START HERE, 2026-11-14T14:28:09Z UTC) — BINDING

Execute this campaign in order. Do **not** do probe/debug archaeology (`probe_*.py`, `debug_*.py`, `ast_probe.py`), do **not** create parallel handoff/session/task docs, and do **not** re-verify already-green areas unless your change touches them. If a step is blocked, produce concrete evidence (exact command + output summary) and continue with the next unblocked priority; never stop at analysis.

### Campaign objective
Make the Betting Against Beta (BAB) crypto strategy **operational on real, updatable market data** with a clean lint/test baseline and a recorded performance guardrail.

### Priority 1 — Environment & quality baseline unblock (remove bottlenecks)
**Why:** Without installed deps and a clean lint baseline, real progress and CI confidence are blocked/inefficient.
- Establish a reproducible local environment for this repo (prefer repo-native approach; at minimum `python3 -m pip install -r requirements.txt` and/or `pip install -e .` as appropriate in this environment). Do not commit environment artifacts/venvs.
- Verify and record: `python3 -m pytest --version`, `python3 -m ruff --version`, `python3 -m pip show numpy pandas scipy`.
- Run baseline evidence:
  - `python3 -m pytest --co -q` (collection health)
  - `python3 -m pytest tests/test_bab_data_loader_campaign_heavy.py -q` (fast sanity; extend only if needed)
  - `python3 -m ruff check .`
- Fix `ruff` violations with **behavior-preserving** edits (mostly `E501` in tests: wrap/split strings, comments, assertions; keep intent identical). Avoid `--unsafe-fixes` unless individually verified safe. Do not weaken `pyproject.toml` lint policy unless unavoidable and explicitly justified.
- **Done when:** deps are installable/reproducible in-session, baseline commands are recorded, and `python3 -m ruff check .` exits 0 (or any unfixable residue is documented with file:line evidence and safety rationale).

### Priority 2 — Real data fetch/update pipeline (core product work)
**Why:** Strategy logic is mature, but the real-data workflow must be reproducible and idempotent (not just a static fixture).
- Build on `strategies/betting_against_beta/data_loader.py`, `scripts/generate_real_market_fixture.py`, `scripts/load_real_bab_example.py`, and fixture contract in `tests/fixtures/real_market_prices.csv` (`date` + BTC benchmark + asset columns; downstream expects loader-compatible schema).
- Implement a runnable **fetch/update** entrypoint (e.g. `scripts/fetch_real_bab_prices.py` and/or extend generator with a clearly documented mode) that:
  - outputs price/returns data in the same schema/contract consumed by `load_prices`/`load_returns`,
  - accepts configurable symbols/universe, benchmark, date range/window, and output path,
  - performs **idempotent incremental updates** (append new rows, dedupe by date, sort, validate continuity/schema, never corrupt existing history),
  - documents data source and licensing/ToS constraints; on fetch failure or missing network/credentials, fails loudly or provides a documented deterministic offline fallback — **no silent bad/partial data**.
- Prefer a public, no-auth source if feasible in this environment; if unavailable, make the offline/deterministic path first-class and explicitly documented so runs remain reproducible.
- Add focused automated tests for: schema contract, dedupe/sort/idempotent append, date handling, and validation/error paths (keep runtime reasonable; target relevant loader/script tests, not the whole 5k+ suite).
- **Done when:** a documented command can create/update real-format data reproducibly and tests prove the contract.

### Priority 3 — Performance baseline & regression guard
- Use `scripts/perf_bench.py` (and a real-format dataset path, fixture or generated) to capture a baseline (timings/memory/available metrics).
- Add a lightweight deterministic regression guard (e.g. checked-in baseline JSON + compare script with tolerance, or CI-friendly check) — least invasive, reliable in this environment.
- **Done when:** baseline is recorded in-repo/docs with command used and a repeatable check exists.

### Priority 4 — Evidence refresh & handoff maintenance
- Run and record only commands relevant to your changes (env/versions, lint, targeted tests/collection as applicable, real-data fetch/update smoke, perf check).
- Update **this file**: new UTC timestamp, new HEAD, completed work, exact evidence, remaining gaps/risks, and the next binding task.
- Keep `AGENT_HANDOFF.md` as a pointer only. Commit coherent, reviewable changes; do not amend unrelated history.

## Live baseline snapshot (2026-11-14T14:28:09Z, pre-change)
- Git: `3df7d45` on `main`, working tree clean at read.
- Environment: `python3` present but `numpy/pandas/scipy/pytest/ruff` not installed in system site-packages at check (`pip show` not found). `python -m pytest/ruff` unavailable until deps installed.
- Prior handoff recorded: `pytest --co -q` → 5709 collected, `pytest tests/test_bab_data_loader_campaign_heavy.py -q` → 46 passed, `ruff check .` → 128 errors (verify after env setup; treat as expected debt until cleared).
- Key assets: `strategies/betting_against_beta/` (BAB pipeline, `data_loader.py`), `scripts/generate_real_market_fixture.py`, `scripts/load_real_bab_example.py`, `scripts/perf_bench.py`, `tests/fixtures/real_market_prices.csv`, `.github/workflows/main.yml`.
- No `workflow_diagnostics/` directory; `research_state/` exists (diagnostics artifacts/history are not the focus—ignore unless blocking).

## Known non-issues (do not churn)
- Large test suite is intentional; iterate with targeted subsets.
- Pandas/numpy warnings in stress tests are expected unless they indicate behavioral regression.
- Historical `probe_*.py` / `debug_*.py` / `ast_probe.py` in root: ignore unless directly required.
- Past workflow agent logs show `edit` invalid-argument/turn-abort incidents; ensure tool calls are well-formed and prefer small, verifiable edits.

## Handoff protocol
1. Read this file fully before acting.
2. Execute priorities in order; document blockers with command evidence and continue where possible.
3. Leave repo coherent and refresh this handoff before stopping.
