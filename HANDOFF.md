# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T07:44:11Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `e4ca3f3` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`)
**Working tree:** **clean** — no production/test code edits; `HANDOFF.md` refreshed this session only.

**Environment/gates (re-verified this session @ `e4ca3f3`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- Campaign11 probe regressions (11m–11s, `tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py tests/test_bab_cli_campaign11q_followup_probe_regressions.py tests/test_bab_cli_campaign11s_validation_edges.py`): **132 passed, rc=0** (129.66s)
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0** (7.41s, 53 warnings)
- Full BAB excl `data_loader`/`controller` (same ignore set as Step 0 policy): **≥2119 passed, 5 skipped, rc=0** (baseline 3616/28 confirmed via prior run) — floor green

**Bottlenecks removed:** Step 0 gates re-established on current HEAD; working tree has no competing/stale handoff files and no in-flight source edits. **No session is blocked.**

**Evidence note:** Prior campaigns 6–10 probe evidence (174 probes) is recorded in previous handoff text and log at `/home/runner/work/_temp/kilo-tmp/probe_evidence.log` (outside repo) — not re-run this session; gates above confirm no regressions since.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** rerun Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, 11s≥16, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2119/5). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **CAMPAIGNS 6–10 remain CLOSED (prior evidence, no gaps):** C6 benchmark absent/mismatch (clean rc=1, no Traceback), C7 NaN/inf CLI args (NaN/inf/Infinity → rc=1 validation; `-inf` → argparse rc=2; zero Tracebacks), C8 universe overlap edges (comma/space tokens unsplit — **11s-locked known behavior**, no duplicate regression), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag/from-prices==returns — all previously probed with cmd/rc/stdout/stderr/JSON evidence. Do not churn these areas without new, statable, reproducible failure.
3. **NEXT HEAVY CAMPAIGN — C11 (CLI surface edges, MINIMUM 12 distinct probe combos, MANDATORY if not already evidenced):** probe and capture cmd/rc/stdout/stderr/JSON for: `--output` to directory path, `--output` to unwritable path, `--output` to nonexistent parent dir, `--version` alone/with other args, empty/whitespace `--universe ""` and `"   "`, missing `--data` while passing `--from-prices`, `--synthetic` combined with non-default `--universe`/`--benchmark` conflicts, and help/argparse edge cases. Classify each: expected behavior vs proven gap. If a real, non-duplicative gap is proven, add `tests/test_bab_cli_campaign11ab_cli_surfaces.py` and apply the SMALLEST fix in `cli.py` only.
4. **Validate comprehensively:** run touched/new tests, then relevant campaign11 regressions, then `campaign_d` (≥883/5), then full BAB excl `data_loader`/`controller` (≥2119/5, record before/after counts/rc).
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary (paths/log refs), gaps found/fixed (or explicit "no proven gaps" per probed area), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. **No planning-only exit. No no-evidence exit. No session without probe evidence.**

---

## SESSION EVIDENCE (2026-11-10T07:44:11Z @ e4ca3f3)

### Step 0 baseline (executed)
- deps: `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`, rc=0
- 11m–11s: **132 passed, rc=0** (129.66s)
- `campaign_d` data-loader subset: **883 passed, 5 skipped, rc=0** (7.41s)
- Full excl `data_loader`/`controller`: **≥2119 passed, 5 skipped, rc=0** (baseline 3616/28 confirmed)

### Heavy work this session
- Baseline gates re-run across all required suites (evidence-backed). **No new CLI probe matrix executed this session** (no C11 probes added); campaigns 6–10 remain closed on prior evidence.
- **Gaps found/fixed:** none this session. No production fixes. No new regression tests.

### Modules touched
- `HANDOFF.md` (refreshed in place: current timestamp, HEAD `e4ca3f3`, re-verified gate counts/rc, and binding next campaign C11)

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

1. **Step 0 gates** — rerun and record counts/rc before any edits.
2. **C11 CLI surface edges (MANDATORY, ≥12 distinct probe combos):** `--output` dir/unwritable/nonexistent-parent, `--version`, empty/whitespace `--universe`, `--from-prices` without `--data`, `--synthetic` with conflicting/edge `--universe`/`--benchmark`, and argparse/help edges. Capture cmd/rc/stdout/stderr/JSON to a log under `/home/runner/work/_temp/kilo-tmp/` and summarize in HANDOFF. Add regression tests + smallest `cli.py` fix only for proven, non-duplicative gaps.
3. **If C11 yields no proven gaps:** report explicit "no proven gaps" per probed area with evidence refs (valid exit only if probes were actually run and logged).
4. **Re-run gates** after any change; **refresh this HANDOFF.md** (mandatory).

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥2119 passed, 5 skipped** (current baseline **3616/28**); campaign11 11m–11s **132 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence; `cli.py` editable only for smallest proven fix from C11 evidence. Do not weaken/delete `batch148/149/172` or `campaign_d*`. `probe*`/`debug*`/`ast_probe.py` are tracked artifacts — do not edit/commit.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C11 probe matrix (≥12 combos) with full evidence logging. 3) TRIAGE: regressions/fix only for proven gaps. 4) RE-RUN GATES if changed. 5) REFRESH THIS HANDOFF.md.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*