# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T07:53:27Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `b32bc7c` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`; prior base `e4ca3f3`)
**Working tree:** **dirty** — `strategies/betting_against_beta/cli.py` modified (+4 lines); new untracked `tests/test_bab_cli_campaign11ab_cli_surfaces.py`. Not committed (commit only if explicitly requested).

**Environment/gates (re-verified this session, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`, rc=0
- Campaign11 probe regressions (11m–11s): **132 passed, rc=0** (120.24s) — pre-change baseline; post-change `11m–s + 11ab` = **147 passed, rc=0** (119.90s)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (6.44s post-change)
- Full BAB excl `data_loader`/`controller`: **4807 passed, 35 skipped, rc=0** (332.72s; baseline 3616/28 confirmed) — floor green
- Additional CLI modules (`test_bab_cli.*`, `test_bab_real_data_cli_repro.py`, `test_bab_backtest_contract_smoke.py`): **106 passed, rc=0** (38.84s)

**Evidence log:** `/home/runner/work/_temp/kilo-tmp/c11_cli_surface_probe_evidence.log` — 14 distinct C11 CLI surface-edge probe combos (cmd/rc/stdout/stderr/JSON), zero Tracebacks.

**Bottlenecks removed:** Step 0 gates re-established on current HEAD; no competing/stale handoff files; no in-flight source edits outside the C11 fix. **No session is blocked.**

**Evidence note:** Prior campaigns 6–10 probe evidence (174 probes) recorded in previous handoff text and log at `/home/runner/work/_temp/kilo-tmp/probe_evidence.log` (outside repo) — not re-run; gates confirm no regressions since.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**CAMPAIGN 11 (CLI surface edges) — COMPLETE.** Probed ≥12 distinct combos with full cmd/rc/stdout/stderr/JSON evidence; triaged; one proven gap fixed; gates re-verified green. See §SESSION EVIDENCE below.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** rerun Step 0 gates (deps, 11m≥28/11ab, 11n≥18, 11o≥19, 11p≥18, 11q≥33, 11s≥16, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2119/5). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **CAMPAIGNS 6–10 remain CLOSED (prior evidence, no gaps):** C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap edges (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag — all previously probed with evidence. Do not churn without new, statable, reproducible failure.
3. **C11 CLI surface edges (≥12 distinct probe combos) — DONE, evidenced:** `--output` dir/unwritable/nonexistent-parent, `--version` alone/with args, empty/whitespace `--universe ""`/`"   "`, missing `--data` with `--from-prices`, `--synthetic` + edge `--universe`/`--benchmark`, help/argparse edges. **One proven gap fixed:** `--from-prices` without `--data` silently fell back to synthetic (rc=0); now rejected cleanly `rc=1, "--from-prices requires --data", no Traceback` via smallest fix in `cli.py` only. Regression tests added in `tests/test_bab_cli_campaign11ab_cli_surfaces.py` (15 tests). All other probed areas: explicit "no proven gaps" with evidence refs.
4. **Validate comprehensively:** ran touched/new tests (147 passed), campaign11 regressions (147 passed), additional CLI modules (106 passed), `campaign_d` (883/5), full BAB excl `data_loader`/`controller` (4807/35 pre-change baseline). Record before/after counts/rc above.
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** done — this file.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. **No planning-only exit. No no-evidence exit. No session without probe evidence.**

---

## SESSION EVIDENCE (2026-11-10T07:53:27Z @ b32bc7c)

### Step 0 baseline (executed)
- deps: rc=0
- campaign11 11m–11s: **132 passed, rc=0** (120.24s); post-change `11m–s + 11ab` **147 passed, rc=0** (119.90s)
- `campaign_d`: **883 passed, 5 skipped, rc=0** (6.44s post-change; 6.68s pre-change)
- Full excl `data_loader`/`controller`: **4807 passed, 35 skipped, rc=0** (332.72s; baseline 3616/28)

### Heavy work this session
- Executed C11 probe matrix: 14 combos → `/home/runner/work/_temp/kilo-tmp/c11_cli_surface_probe_evidence.log`. All clean, zero Tracebacks.
- **Gap found + fixed:** `--from-prices` without `--data` silently ran synthetic (rc=0). Smallest `cli.py` fix: reject cleanly `rc=1, "--from-prices requires --data"`, no Traceback (run + dry-run).
- **No proven gaps (evidence-backed):** `--version` (rc=0, "bab 0.1.0"), `--output` unwritable/directory (rc=1), `--output` nonexistent parent (rc=0, parents created), `--universe ""`/`"   "` (rc=1), unknown flag (rc=2), `--help` (rc=0), nonexistent `--data` (rc=1), dry-run output unwritable (rc=1).
- Added `tests/test_bab_cli_campaign11ab_cli_surfaces.py` (15 regression tests) — all pass.
- Regression check: campaign11m–s + 11ab **147 passed**; additional CLI modules **106 passed**; `campaign_d` **883/5**.

### Modules touched
- `strategies/betting_against_beta/cli.py` (+4 lines: `--from-prices requires --data` validation)
- `tests/test_bab_cli_campaign11ab_cli_surfaces.py` (new, 15 tests)
- `HANDOFF.md` (refreshed in place)

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C12 — CLI `main()` in-process API error-path cleanliness (≥12 probe combos).** Probe direct `main(argv)` invocations (not subprocess) and capture rc/stdout/stderr, asserting rc=1 with actionable message and **no Traceback / no uncaught exception** for:
- invalid `--beta-window` (<1, 0, huge), invalid `--long-quantile`/`--short-quantile` (≤0, ≥1, sum≥1), negative `--transaction-costs`/`--slippage`, empty `--rebalance-freq`, empty/whitespace `--universe`, `--from-prices` without `--data` (confirm fix holds in-process), `--output` unwritable/directory, nonexistent `--data`, malformed benchmark symbol.
- Plus in-process parity: `main(...)` rc == subprocess rc for the same argv; output JSON strict-finite where written.

Capture cmd/rc/stdout/stderr to `/home/runner/work/_temp/kilo-tmp/c12_cli_api_probe_evidence.log`. Add regression tests + smallest `cli.py` fix only for proven, non-duplicative gaps; else explicit "no proven gaps" with evidence.

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥2119 passed, 5 skipped** (current baseline **4807/35**); campaign11 11m–s **+ 11ab** **≥147 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence; `cli.py` editable only for smallest proven fix from probe evidence. Do not weaken/delete `batch148/149/172` or `campaign_d*`. `probe*`/`debug*`/`ast_probe.py` are tracked artifacts — do not edit/commit.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C12 probe matrix (≥12 combos) with full evidence logging. 3) TRIAGE: regressions/fix only for proven gaps. 4) RE-RUN GATES if changed. 5) REFRESH THIS HANDOFF.md.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
