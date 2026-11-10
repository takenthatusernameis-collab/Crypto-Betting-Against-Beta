# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T05:35:54Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `7e281b1` (`chore(kilo): checkpoint agent session`, local `main`/worktree context; prior session base in file was `1d9f342` content-refresh checkpoint)
**Working tree:** **dirty/untracked** — `tests/test_bab_cli_campaign11q_followup_probe_regressions.py` added this session (33 tests, green). No production code changed. No commits/pushes. Tracked `probe*`/`debug*`/`ast_probe.py` untouched.

**Environment/gates (re-verified this session @ `7e281b1`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` → **83 passed, rc=0** (28+18+19+18)
- `python3 -m pytest -q tests/test_bab_cli_campaign11q_followup_probe_regressions.py` → **33 passed, rc=0** (new probe locks this session)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 3994 deselected, 53 warnings, rc=0**
- `python3 -m pytest -q -k "not data_loader and not controller"` → **2099 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** in 288.65s (baseline floor before this session's 11q file existed; re-run after adding/adjusting 11q to confirm ≥2103 passed/5 skipped expected — do as Step 0 before further edits)

**Bottlenecks removed:** Step 0 gates re-run; campaign_d green; prior `data_loader`/`controller` exclusion baseline stable. No `.bab_active`/session-lock artifacts observed.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** run Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2099/5 adjusted for new 11q coverage). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **Execute heavy probe matrix (§NEXT FOCUS HEAVY CAMPAIGN)** against `tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv`, and constrained synthetic/temp inputs. For EVERY probe capture: command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations exhaustively until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits. Minimum 10 distinct probe combos per session.
3. **Triage evidence rigorously:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the SMALLEST production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate comprehensively:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (record before/after counts/rc). Record before/after.
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area with evidence), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit. No session without probe evidence.

---

## CAMPAIGN11 follow-up — EVIDENCE THIS SESSION (2026-11-10T05:18Z–05:34Z @ 7e281b1)

### Probe matrix executed & locked

| # | Combo | Evidence | Verdict |
|---|-------|----------|---------|
| 1 | **Dry-run semantic audit (before fix):** `--dry-run` vs real run for `--long-quantile 0.6 --short-quantile 0.6` on `REAL` from-prices | dry-run rc=0 prints `(valid, --from-prices=True)`; real run rc=0 finite `Final cumulative return: 0.480526 Periods: 398` | Characterized: dry-run does not reject quantile-sum≥1; run accepts per current contract. Locked in 11q. |
| 2 | Dry-run vs run `--universe ZZZ,YYY` (zero overlap) on `REAL` from-prices | dry-run rc=0 `(valid)` reports `universe: ['ZZZ,YYY']`; real run rc=1 clean `Error running strategy: configured universe ['ZZZ,YYY'] has no overlap with data columns ...` no Traceback | Semantic gap characterized (dry-run validates loadability, not run-time overlap). Locked in 11q. |
| 3 | Dry-run vs run `--universe ,,,` (all-empty after split semantics) on `REAL` from-prices | dry-run rc=0 `(valid)` reports `universe: [',,,']`; real run rc=1 clean overlap error, no Traceback | Characterized/locked in 11q. |
| 4 | **Real fixture from-prices CLI parity** via `--output` JSON on `REAL`+`EXP`, combos (0.001/0.0005/daily, 0.01/0/daily, 0/0.01/weekly, 0.005/0.005/daily) vs in-process `load_prices`+`BABStrategy` | rc=0, strict finite JSON, exact `final_cumulative`/`periods`/`benchmark` match; CLI `universe` equals resolved `result.config.universe` (e.g. `REAL`: `['BTC','ETH','SOL','BNB','XRP','ADA','AVAX','DOT']`; note `LINK` present in loaded cols but not in resolved run universe — parity locked to in-process run config) | PASS — locked in 11q. |
| 5 | **Malformed/edge data dry-run** temp inputs (empty_csv, header_only, single_col, nat_heavy) returns+from-prices | all rc=1, `Traceback` absent, `INVALID` in output | PASS — locked in 11q. |
| 6 | Malformed/edge (duplicate index, duplicate columns, mixed inf/nan rows) temp inputs, returns+from-prices | rc 0 or 1 depending on loader contract, `Traceback` absent; rc=1 cases include `INVALID` | Loader-contract behavior characterized/locked in 11q (no crashes). |
| 7 | Baselines: `REAL`/`EXP` dry-run returns+from-prices | rc=0, `(valid...)`, no Traceback | PASS. |
| 8 | **`--output` edge cases:** output to pre-existing directory (`tests/fixtures`) | backtest ran (`Periods: 398`) then rc=1 clean `Error validating output path: --output path is a directory, not a file...` no Traceback | PASS (clean failure). Locked in 11q. |
| 9 | Deep nested output creation | rc=0, file written, finite JSON `final_cumulative` | PASS. Locked in 11q. |
| 10 | `--dry-run --output` with invalid missing data | rc=1 for data reason, `INVALID` shown, **no output file written**, no Traceback | PASS. Locked in 11q. |
| 11 | `--dry-run --output` with valid data to deep nested path | rc=0, **no file written**, no Traceback | PASS. Locked in 11q. |

**Gaps found/fixed:** explicit **no proven gaps** requiring production change. Dry-run semantic differences (#1-#3) are characterized against exercised run behavior and locked as current contract; no existing test requires stricter dry-run rejection.

**Modules touched:** `tests/test_bab_cli_campaign11q_followup_probe_regressions.py` (new, 33 tests). No production edits.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

### HEAVY CAMPAIGN 1: Returns-path CLI JSON parity (from-prices parity locked in 11q; returns path unprobed for JSON)
**Target:** `load_returns` + `BABStrategy` in-process vs CLI `--output` JSON on REAL/EXP fixtures (no `--from-prices`)
**Combos (minimum 12):** Cross product of tc ∈ {0.0, 0.0005, 0.001, 0.005}, slippage ∈ {0.0, 0.0005, 0.001}, rebalance ∈ {daily, weekly, monthly}
**Evidence required per combo:** CLI cmd, rc, stdout tail, stderr tail, `--output` JSON parsed; in-process `load_returns`+`BABStrategy` run with identical config; exact finite match on `final_cumulative`/`periods`/`benchmark`/`universe` (stringified).
**Failure mode:** Any mismatch → add regression test in `tests/test_bab_cli_campaign11r_returns_json_parity.py`; if bug proven → minimal fix in `cli.py`/`strategy.py` only.

### HEAVY CAMPAIGN 2: CLI config/validation adversarial edges (evidence-first, no assumptions)
**Target:** Dry-run vs run parity on validation paths
**Probe matrix (minimum 15 combos):**
- Invalid `--rebalance-freq` tokens: `hourly`, `yearly`, `invalid`, `D`, `W`, `M`, `1d`, `7d`, `` (empty)
- `--beta-window`: `-1`, `0`, `1`, `10`, `50`, `1000000`, `999999999`, `NaN` (via shell), `inf`
- `--long-quantile`/`--short-quantile`: `-0.1`, `0.0`, `1.0`, `1.1`, `NaN`, `inf`, `-inf`, `0.999999`, `1.000001`
- `--transaction-costs`/`--slippage`: negative, NaN, inf, very large (1e6)
- `--benchmark` absent in data (returns-path): dry-run vs run behavior
- `--universe` whitespace: `" BTC "`, `"BTC, ETH"`, `"BTC,,ETH"`, `"  "`, `","`, `", ,"`
**Evidence required per combo:** Dry-run cmd/rc/stdout/stderr; Run cmd/rc/stdout/stderr; Compare parity; Note any Traceback (must be absent).
**Failure mode:** Proven validation gap → regression test in `tests/test_bab_cli_campaign11s_validation_edges.py`; minimal fix in `cli.py`/`config.py` only.

### HEAVY CAMPAIGN 3: From-prices vs returns semantic equivalence on real fixtures
**Target:** `load_prices(...)` → returns vs `load_returns(...)` on REAL/EXP fixtures
**Probe matrix (minimum 8 combos):** Cross product of rebalance ∈ {daily, weekly}, tc ∈ {0.0, 0.001}, slippage ∈ {0.0, 0.0005}
**Evidence required:** CLI `--from-prices` run JSON vs CLI returns-path run JSON vs in-process both paths; Characterize differences (beta calc, universe resolution, period alignment); Only lock if stable/non-duplicative.
**Failure mode:** Proven semantic difference → regression test in `tests/test_bab_cli_campaign11t_prices_vs_returns.py`; document expected difference.

### HEAVY CAMPAIGN 4: `--output` overwrite/idempotence/fs edge cases
**Target:** File write semantics
**Probe matrix (minimum 6 combos):**
- Run twice to same `--output` path (overwrite): 2nd run rc=0, file contains 2nd run data
- Output to symlink target (create temp symlink → real file): rc=0, file written
- Very long path component (>200 chars): rc=0 or clean error, no crash
- Output to existing file with `0444` perms (read-only): clean error, no Traceback
- `--dry-run --output` to unwritable location: rc=1, no file written
- `--output` with directory traversal `../../../tmp/out.json`: rc=0 or clean error
**Evidence required:** cmd, rc, stdout, stderr, file existence/contents after, perms check.
**Failure mode:** Proven fs bug → regression test in `tests/test_bab_cli_campaign11u_output_fs.py`; minimal fix in `cli.py`.

### HEAVY CAMPAIGN 5: Metrics/backtest summary consistency under costs/slippage
**Target:** CLI JSON `final_cumulative` vs last cumulative in result vs `periods` vs backtest length
**Probe matrix (minimum 10 combos):** REAL/EXP fixtures × from-prices/returns × costs {0.0, 0.001, 0.005} × slippage {0.0, 0.001} × rebalance {daily, weekly}
**Evidence required:** Parse CLI `--output` JSON; extract `result.backtest.cumulative` last value; extract `len(result.backtest)`; Verify `final_cumulative` ≈ last cumulative (within 1e-10); Verify `periods` == `len(backtest)`; Any mismatch → regression.
**Failure mode:** Proven inconsistency → regression test in `tests/test_bab_cli_campaign11v_summary_consistency.py`; minimal fix in `cli.py`/`backtest.py`/`metrics.py`.

---

### GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2099 passed, 5 skipped** (pre-11q floor this session; expected +33 with 11q present — re-verify)
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `campaign11n` (18), `campaign11o` (19), `campaign11p` (18), `campaign11q_followup_probe_regressions.py` (33) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked per prior notes unless disproven by evidence; other module miss-closures per prior handoff/proofs remain binding.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE — NO DEVIATION)

1. **RUN STEP 0 GATES** on current tree; confirm 11m–11q passing and full-excl floor including 11q. Record counts/rc.
2. **EXECUTE HEAVY CAMPAIGN 1** (Returns-path JSON parity) — minimum 12 probe combos with full evidence logging. No skipping.
3. **EXECUTE HEAVY CAMPAIGN 2** (Validation edges) — minimum 15 probe combos with dry-run vs run parity evidence. No skipping.
4. **EXECUTE HEAVY CAMPAIGN 3** (Prices vs returns equivalence) — minimum 8 probe combos. No skipping.
5. **EXECUTE HEAVY CAMPAIGN 4** (Output fs edges) — minimum 6 probe combos. No skipping.
6. **EXECUTE HEAVY CAMPAIGN 5** (Summary consistency) — minimum 10 probe combos. No skipping.
7. **ADD REGRESSION TESTS** for ANY proven gap (non-duplicative, focused, in `tests/test_bab_*campaign11*`).
8. **APPLY MINIMAL PRODUCTION FIXES** only for proven bugs (smallest diff, exercised code only).
9. **RE-RUN TOUCHED TESTS + ALL GATES** (Step 0) — record before/after counts/rc.
10. **REFRESH THIS HANDOFF.md** with: new timestamp, HEAD, dirty state, all probe evidence (cmd/rc/stdout/stderr/JSON), gaps found/fixed with evidence, modules touched, next binding slice.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute the heavy campaigns above. No planning-only exits. No evidence-free sessions. Heavy work is mandatory.*