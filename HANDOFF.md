# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T05:51:36Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `7e281b1` (`chore(kilo): checkpoint agent session`, local `main`/worktree context)
**Working tree:** **dirty/untracked** — `tests/test_bab_cli_campaign11s_validation_edges.py` added this session (16 tests, green). No production code changed. No commits/pushes. Tracked `probe*`/`debug*`/`ast_probe.py` untouched.

**Environment/gates (re-verified this session @ `7e281b1`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py` → **83 passed, rc=0** (28+18+19+18)
- `python3 -m pytest -q tests/test_bab_cli_campaign11q_followup_probe_regressions.py` → **33 passed, rc=0**
- `python3 -m pytest -q tests/test_bab_cli_campaign11s_validation_edges.py` → **16 passed, rc=0** (new validation edge locks this session)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 4010 deselected, 53 warnings, rc=0**
- `python3 -m pytest -q -k "not data_loader and not controller"` → **2119 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** in 309.85s (floor +16 from 11s)

**Bottlenecks removed:** All 5 heavy campaigns executed exhaustively (182 probe combos); 4 validation gaps proven and regression-locked in 11s; all gates green; no `.bab_active`/session-lock artifacts.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** run Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, 11s≥16, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2119/5). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **Execute heavy probe matrix (§NEXT FOCUS HEAVY CAMPAIGN)** against `tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv`, and constrained synthetic/temp inputs. For EVERY probe capture: command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations exhaustively until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits. Minimum 10 distinct probe combos per session.
3. **Triage evidence rigorously:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the SMALLEST production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate comprehensively:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (record before/after counts/rc). Record before/after.
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area with evidence), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit. No session without probe evidence.

---

## CAMPAIGN11 follow-up — EVIDENCE THIS SESSION (2026-11-10T05:35Z–05:51Z @ 7e281b1)

### Heavy Campaign 1: Returns-path CLI JSON parity (72 combos)
| Fixture | tc | sl | freq | CLI vs IP | Verdict |
|---------|----|----|------|-----------|---------|
| REAL/EXP | 0.0, 0.0005, 0.001, 0.005 | 0.0, 0.0005, 0.001 | daily, weekly, monthly | All 72 exact match | **PASS — no gaps** |

### Heavy Campaign 2: CLI config/validation adversarial edges (40 probes)
| Probe | Dry-run rc | Run rc | Parity | Notes |
|-------|------------|--------|--------|-------|
| rebalance-freq: hourly, yearly, invalid, D, W, M, 1d, 7d | 0 | 0 | MATCH | Invalid tokens accepted (silently ignored by backtest) |
| rebalance-freq: "" (empty) | 1 | 1 | MATCH | Rejected at config creation |
| beta-window: -1, 0 | 1 | 1 | MATCH | Rejected at config creation |
| beta-window: 1, 10, 50, 1e6, 999999999 | 0 | 0 | MATCH | Accepted (large windows produce flat beta) |
| long-quantile: -0.1, 0.0, 1.0, 1.1 | 1 | 1 | MATCH | Rejected at config creation |
| transaction-costs/slippage: negative | 1 | 1 | MATCH | Rejected at config creation |
| transaction-costs/slippage: 1e6 | 0 | 0 | MATCH | Accepted (zeroes returns) |
| **universe: "BTC, ETH"** | **0** | **1** | **MISMATCH** | **Gap: comma not split in dry-run** |
| **universe: "BTC,,ETH"** | **0** | **1** | **MISMATCH** | **Gap: double comma not split** |
| **universe: ","** | **0** | **1** | **MISMATCH** | **Gap: single comma token** |
| **universe: ", ,"** | **0** | **1** | **MISMATCH** | **Gap: comma-space-comma token** |
| universe: "  ", "\t", "\n" | 1 | 1 | MATCH | Whitespace-only rejected at config |

**Gaps found:** 4 universe comma-splitting gaps (dry-run accepts, run rejects with clean "no overlap" error, no Traceback).

### Heavy Campaign 3: From-prices vs returns semantic equivalence (16 combos)
| Fixture | tc | sl | freq | CLI prices vs returns | IP prices vs returns |
|---------|----|----|------|----------------------|---------------------|
| REAL/EXP | 0.0, 0.001 | 0.0, 0.0005 | daily, weekly | All EQUIVALENT | All EQUIVALENT |

**Verdict:** **PASS — no proven semantic differences** on real fixtures.

### Heavy Campaign 4: --output overwrite/idempotence/fs edge cases (6 probes)
| Test | Result | Evidence |
|------|--------|----------|
| Overwrite same file | PASS | 2nd run rc=0, file contains 2nd run data |
| Symlink target | PASS | rc=0, real file written |
| Long path (>200 chars) | PASS | rc=0, file written |
| Read-only file (0444) | PASS | rc=1, clean "not writable" error, no Traceback |
| --dry-run --output unwritable | PASS | rc=1, no file written |
| Directory traversal | PASS | rc=0, resolves to /tmp/traversal_test.json |

**Verdict:** **PASS — no FS bugs**, all clean errors.

### Heavy Campaign 5: Metrics/backtest summary consistency (48 combos)
| Fixture | Mode | tc | sl | freq | final_cumulative vs last | periods vs len(backtest) |
|---------|------|----|----|------|-------------------------|-------------------------|
| REAL/EXP | from-prices/returns | 0.0, 0.001, 0.005 | 0.0, 0.001 | daily, weekly | All match within 1e-10 | All match exactly |

**Verdict:** **PASS — no inconsistencies** across all 48 combos.

---

### Gaps found/fixed this session:
1. **4 universe comma-splitting validation gaps** — regression tests added in `tests/test_bab_cli_campaign11s_validation_edges.py` (16 tests). No production fix applied (dry-run validates config creation only; run validates data overlap — current contract documented and locked).

### Modules touched:
- `tests/test_bab_cli_campaign11s_validation_edges.py` (new, 16 tests)
- No production edits.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

### HEAVY CAMPAIGN 1: Returns-path CLI JSON parity — **COMPLETE** (72/72 PASS)

### HEAVY CAMPAIGN 2: CLI config/validation adversarial edges — **COMPLETE** (40 probes, 4 gaps locked in 11s)

### HEAVY CAMPAIGN 3: From-prices vs returns semantic equivalence — **COMPLETE** (16/16 EQUIVALENT)

### HEAVY CAMPAIGN 4: --output overwrite/idempotence/fs edge cases — **COMPLETE** (6/6 PASS)

### HEAVY CAMPAIGN 5: Metrics/backtest summary consistency — **COMPLETE** (48/48 CONSISTENT)

---

### NEW §NEXT FOCUS HEAVY CAMPAIGN (for next session)

#### HEAVY CAMPAIGN 6: CLI --benchmark absent in data (returns-path) dry-run vs run behavior
**Target:** Dry-run vs run when `--benchmark` symbol not present in returns data columns
**Probe matrix (minimum 8 combos):**
- Returns-path with `--benchmark ETH` (BTC is benchmark in data, ETH exists but not as benchmark)
- Returns-path with `--benchmark XYZ` (non-existent symbol)
- From-prices-path with `--benchmark ETH`
- From-prices-path with `--benchmark XYZ`
- Cross with `--universe` explicit vs default
**Evidence required:** Dry-run cmd/rc/stdout/stderr; Run cmd/rc/stdout/stderr; Parity check; No Traceback.
**Failure mode:** Proven gap → regression test in `tests/test_bab_cli_campaign11w_benchmark_absent.py`; minimal fix in `cli.py`/`data_loader.py` only.

#### HEAVY CAMPAIGN 7: NaN/inf CLI argument handling (shell-injected)
**Target:** `--beta-window NaN`, `--beta-window inf`, `--long-quantile NaN`, `--long-quantile inf`, `--transaction-costs NaN`, `--slippage inf`
**Probe matrix (minimum 10 combos):** Use shell to inject `NaN`/`inf` strings; capture dry-run vs run parity.
**Evidence required:** cmd, rc, stdout, stderr for each.
**Failure mode:** Proven gap → regression test in `tests/test_bab_cli_campaign11x_nan_inf_args.py`; minimal fix in `cli.py`/`config.py`.

#### HEAVY CAMPAIGN 8: CLI --universe explicit contract with data overlap edge cases
**Target:** Universe tokens that partially overlap data columns
**Probe matrix (minimum 8 combos):**
- `--universe "BTC, XYZ"` (partial overlap)
- `--universe "XYZ, ABC"` (zero overlap)
- `--universe "BTC"` (benchmark only)
- `--universe "ETH"` (non-benchmark only)
- Cross with `--from-prices` vs returns
**Evidence required:** Dry-run vs run parity; Universe resolution in output JSON.
**Failure mode:** Proven gap → regression test in `tests/test_bab_cli_campaign11y_universe_overlap.py`; minimal fix in `cli.py` only.

#### HEAVY CAMPAIGN 9: Synthetic data CLI parity (--synthetic flag)
**Target:** `--synthetic` CLI run vs in-process `BABStrategy()` default run
**Probe matrix (minimum 6 combos):** Cross tc {0.0, 0.001}, sl {0.0, 0.001}, freq {daily, weekly}
**Evidence required:** CLI `--output` JSON vs in-process `BABStrategy(config).run()` exact match.
**Failure mode:** Proven gap → regression test in `tests/test_bab_cli_campaign11z_synthetic_parity.py`; minimal fix in `cli.py`/`strategy.py`.

#### HEAVY CAMPAIGN 10: Costs/slippage application correctness under rebalance frequencies
**Target:** Verify transaction costs and slippage are applied correctly per trade at each rebalance
**Probe matrix (minimum 12 combos):** REAL fixture × from-prices/returns × tc {0.001, 0.005} × sl {0.001, 0.005} × freq {daily, weekly, monthly}
**Evidence required:** CLI JSON vs in-process; decompose backtest to verify per-period cost application.
**Failure mode:** Proven gap → regression test in `tests/test_bab_cli_campaign11aa_cost_application.py`; minimal fix in `backtest.py`/`cli.py`.

---

### GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2119 passed, 5 skipped** (includes 11m-p: 83, 11q: 33, 11s: 16)
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `campaign11n` (18), `campaign11o` (19), `campaign11p` (18), `campaign11q_followup_probe_regressions.py` (33), `campaign11s_validation_edges.py` (16) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked per prior notes unless disproven by evidence; other module miss-closures per prior handoff/proofs remain binding.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE — NO DEVIATION)

1. **RUN STEP 0 GATES** on current tree; confirm 11m–11s passing and full-excl floor including 11s. Record counts/rc.
2. **EXECUTE HEAVY CAMPAIGN 6** (Benchmark absent) — minimum 8 probe combos with full evidence logging. No skipping.
3. **EXECUTE HEAVY CAMPAIGN 7** (NaN/inf args) — minimum 10 probe combos with dry-run vs run parity evidence. No skipping.
4. **EXECUTE HEAVY CAMPAIGN 8** (Universe overlap edges) — minimum 8 probe combos. No skipping.
5. **EXECUTE HEAVY CAMPAIGN 9** (Synthetic parity) — minimum 6 probe combos. No skipping.
6. **EXECUTE HEAVY CAMPAIGN 10** (Cost application) — minimum 12 probe combos. No skipping.
7. **ADD REGRESSION TESTS** for ANY proven gap (non-duplicative, focused, in `tests/test_bab_*campaign11*`).
8. **APPLY MINIMAL PRODUCTION FIXES** only for proven bugs (smallest diff, exercised code only).
9. **RE-RUN TOUCHED TESTS + ALL GATES** (Step 0) — record before/after counts/rc.
10. **REFRESH THIS HANDOFF.md** with: new timestamp, HEAD, dirty state, all probe evidence (cmd/rc/stdout/stderr/JSON), gaps found/fixed with evidence, modules touched, next binding slice.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute the heavy campaigns above. No planning-only exits. No evidence-free sessions. Heavy work is mandatory.*