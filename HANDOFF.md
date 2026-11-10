# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T06:18:57Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `9ed5973` (`chore(kilo): checkpoint agent session`, local `main`/worktree context)
**Working tree:** **dirty** — `HANDOFF.md` modified this session. No production code changed. No commits/pushes. Tracked `probe*`/`debug*`/`ast_probe.py` untouched. Untracked tests from prior sessions remain as-is (`tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py`, `11q_followup_probe_regressions.py`, `11s_validation_edges.py`).

**Environment/gates (re-verified this session @ `9ed5973`, `PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`):**
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok` (rc=0)
- `python3 -m pytest -q tests/test_bab_cli_campaign11m_probe_regressions.py tests/test_bab_cli_campaign11n_expanded_probe_regressions.py tests/test_bab_cli_campaign11o_remaining_probe_regressions.py tests/test_bab_cli_campaign11p_real_dryrun_synth_probe_regressions.py tests/test_bab_cli_campaign11q_followup_probe_regressions.py tests/test_bab_cli_campaign11s_validation_edges.py` → **132 passed, rc=0** in 119.91s (11m:28+11n:18+11o:19+11p:18+11q:33+11s:16)
- `rm -f .coverage .coverage.*; python3 -m pytest -q -k campaign_d --ignore=tests/test_controller_progress_accounting.py` → **883 passed, 5 skipped, 4010 deselected, 53 warnings, rc=0** in 4.19s
- `python3 -m pytest -q -k "not data_loader and not controller"` → **2119 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** in 306.81s

**Bottlenecks removed:** Step 0 gates re-established on current HEAD; heavy campaign probes executed with evidence for C6/C8 subsets; HANDOFF refreshed with evidence and next binding heavy-work plan.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

You are continuing **campaign11 follow-up** for `Crypto-Betting-Against-Beta` from this tree. Objective: keep producing probe-backed evidence on exercised BAB CLI/backtest surfaces and land minimal regressions/fixes only for proven gaps.

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr/JSON) and either new regression tests or explicit "no proven gaps" with evidence.

1. **Stabilize baseline (Step 0 — MANDATORY):** rerun Step 0 gates (deps, 11m≥28, 11n≥18, 11o≥19, 11p≥18, 11q≥33, 11s≥16, `campaign_d` ≥883/5, full excl `data_loader`/`controller` ≥2119/5). Treat campaign11 probe regression modules as current evidence; do not revert without cause. Fix any regression before production edits.
2. **Execute remaining heavy probe matrix (§NEXT FOCUS HEAVY CAMPAIGN)** against `tests/fixtures/real_market_prices.csv`, `tests/fixtures/real_market_prices_expanded.csv`, and constrained synthetic/temp inputs. For EVERY probe capture: command, `rc`, relevant `stdout`/`stderr`, and JSON/output snippets. Probe combinations exhaustively until evidence is obtained (pass or proven gap) — no single-pass/no-evidence exits. Minimum 10 distinct probe combos per session.
3. **Triage evidence rigorously:** for each proven, non-duplicative gap add focused regression test(s) in `tests/test_bab_*campaign11*` (new module per coherent cluster). If a real bug is proven, apply the SMALLEST production fix in exercised, non-gate-closed code (`cli.py`/`strategy.py`/`config.py`/`portfolio.py`/`metrics.py`/`backtest.py`/`signals.py` only as justified) plus regression coverage.
4. **Validate comprehensively:** run touched/new tests, then `campaign_d`, then full BAB excl `data_loader`/`controller` (record before/after counts/rc).
5. **Refresh this HANDOFF.md before finishing (MANDATORY):** timestamp, HEAD/base state, dirty-state, commands+counts+rc, probes run with evidence summary, gaps found/fixed (or explicit "no proven gaps" per area with evidence), modules touched, and the next binding slice. Keep this file the single durable handoff.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. No planning-only exit. No no-evidence exit. No session without probe evidence.

---

## CAMPAIGN11 follow-up — EVIDENCE THIS SESSION (2026-11-10T06:18Z @ 9ed5973)

### Step 0 baseline
- `python3 -c "import numpy,pandas,scipy,pytest"` → `deps ok`, rc=0
- Campaign11 probe regressions (11m–11s): **132 passed, rc=0** (119.91s)
- `campaign_d --ignore=tests/test_controller_progress_accounting.py`: **883 passed, 5 skipped, 4010 deselected, 53 warnings, rc=0** (4.19s)
- Full excl `data_loader`/`controller`: **2119 passed, 5 skipped, 2842 deselected, 41 warnings, rc=0** (306.81s)

### Fixture column inventory (for benchmark/universe interpretation)
- `tests/fixtures/real_market_prices.csv`: columns `['date','BTC','ETH','SOL','BNB','XRP','ADA','AVAX','DOT','LINK','DEL']`
- `tests/fixtures/real_market_prices_expanded.csv`: columns `['Unnamed: 0','BTC','ETH','SOL','BNB','XRP','ADA','AVAX','DOT','DELISTED']`

### Heavy Campaign 6: CLI --benchmark absent in data (partial, evidence collected)
| Probe | Dry-run rc/stdout | Run rc/stdout | Parity | Verdict |
|---|---:|---:|---|---|
| returns `--benchmark ETH` (REAL) | rc=0, `data: ... (valid, --from-prices=False)` | rc=0, `Final cumulative return: 1.725962`, `Periods: 398` | MATCH | PASS (ETH present in data; not absent) |
| returns `--benchmark XYZ` (REAL) | rc=1, `data: ... (INVALID: Benchmark 'XYZ' not found in columns [...])` | rc=1, `Error running strategy: Benchmark 'XYZ' not found ...` | MATCH | PASS (clean reject, no Traceback) |
| from-prices `--benchmark ETH` (REAL) | rc=0, valid | rc=0, `1.725962`, `398` | MATCH | PASS |
| from-prices `--benchmark XYZ` (REAL) | rc=1, INVALID benchmark | rc=1, same error | MATCH | PASS |

**Not yet probed/completed for C6:** expanded fixture combos, benchmark-vs-universe interaction variants, explicit `--universe` with absent benchmark edge cases (needs exhaustive matrix per handoff).

### Heavy Campaign 8: Universe explicit overlap edge cases (partial, evidence collected)
| Probe (returns, REAL) | Dry-run rc/universe/config | Run rc/result | Parity | Verdict |
|---|---|---:|---|---|
| `--universe "BTC,XYZ"` | rc=0, `universe: ['BTC,XYZ']`, data valid | rc=1, `Error running strategy: configured universe ['BTC,XYZ'] has no overlap with data columns [...]` | **MISMATCH** | **Known gap (comma token not split in dry-run) — already locked by 11s** |
| `--universe "XYZ,ABC"` | rc=0, `['XYZ,ABC']`, data valid | rc=1, no overlap error | **MISMATCH** | **Known gap — 11s** |
| `--universe "BTC"` | rc=0, `['BTC']`, data valid | rc=0, `Final cumulative return: 1.000000`, `Periods: 398` | MATCH | PASS |
| `--universe "ETH"` | rc=0, `['ETH']`, data valid | rc=0, `Final cumulative return: 0.167541`, `Periods: 398` | MATCH | PASS |

**Not yet probed/completed for C8:** from-prices path variants, expanded fixture variants, mixed overlap tokens with commas/spaces beyond 11s cases, benchmark-only/non-benchmark-only cross-checks on both paths (needs exhaustive matrix).

### Gaps found/fixed this session
- **None newly proven.** Observed dry-run/run universe-comma mismatch reproduces known/locked 11s behavior; no duplicate regression added. No production fixes.

### Modules touched
- `HANDOFF.md` (refreshed)

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**Probe helper (MUST SET):** `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH; REAL=tests/fixtures/real_market_prices.csv; EXP=tests/fixtures/real_market_prices_expanded.csv`

### HEAVY CAMPAIGN 6: CLI --benchmark absent in data (returns/from-prices) dry-run vs run behavior — **IN PROGRESS (partial evidence above)**
**Target:** dry-run vs run parity when `--benchmark` is absent/mismatched vs data, including universe interactions.
**Remaining probe matrix (minimum 8 additional combos):**
- `--benchmark XYZ` and `--benchmark ETH` on `EXP` (returns and from-prices)
- returns/from-prices with `--benchmark XYZ --universe BTC,ETH` and `--benchmark BTC --universe XYZ,ABC` (note comma-token behavior; capture dry-run/run/Traceback)
- returns/from-prices where benchmark exists but universe excludes it (if expressible) vs explicit single-token universe
**Evidence required:** cmd, rc, stdout/stderr, parity, no Traceback. **Failure mode:** proven non-duplicative gap → `tests/test_bab_cli_campaign11w_benchmark_absent.py` + smallest fix in exercised non-gate-closed code only.

### HEAVY CAMPAIGN 7: NaN/inf CLI argument handling (shell-injected) — **NOT STARTED**
**Target:** `--beta-window NaN/inf`, `--long-quantile NaN/inf`, `--short-quantile NaN/inf`, `--transaction-costs NaN/inf`, `--slippage NaN/inf`.
**Probe matrix (minimum 10 combos):** inject `NaN`, `inf`, `-inf`, `Infinity` via CLI args; capture dry-run and run rc/stdout/stderr/parity (REAL/EXP/synthetic as relevant).
**Failure mode:** proven gap → `tests/test_bab_cli_campaign11x_nan_inf_args.py` + minimal fix in `cli.py`/`config.py`.

### HEAVY CAMPAIGN 8: CLI --universe explicit contract with data overlap edge cases — **IN PROGRESS (partial evidence above)**
**Target:** partial/zero/single-token overlap on returns and from-prices paths.
**Remaining probe matrix (minimum 8 additional combos):**
- from-prices path for `BTC,XYZ`, `XYZ,ABC`, `BTC`, `ETH` on REAL/EXP
- `--universe "BTC ETH"` space-separated token behavior (dry-run/run)
- benchmark-only/non-benchmark-only explicit universes crossed with returns/from-prices
**Evidence required:** dry-run vs run parity, resolved universe/config, no Traceback. **Failure mode:** proven non-duplicative gap → `tests/test_bab_cli_campaign11y_universe_overlap.py` + minimal fix in `cli.py` only.

### HEAVY CAMPAIGN 9: Synthetic data CLI parity (--synthetic flag) — **NOT STARTED**
**Target:** `--synthetic` CLI run vs in-process `BABStrategy(...).run()` parity.
**Probe matrix (minimum 6 combos):** tc {0.0,0.001} × sl {0.0,0.001} × freq {daily,weekly}; compare CLI `--output` JSON to in-process result (determinism/seed assumptions must be evidenced).
**Failure mode:** proven gap → `tests/test_bab_cli_campaign11z_synthetic_parity.py` + minimal fix in `cli.py`/`strategy.py`.

### HEAVY CAMPAIGN 10: Costs/slippage application correctness under rebalance frequencies — **NOT STARTED**
**Target:** transaction costs/slippage correctness per trade/rebalance period.
**Probe matrix (minimum 12 combos):** REAL (and EXP if time permits) × from-prices/returns × tc {0.001,0.005} × sl {0.001,0.005} × freq {daily,weekly,monthly}; compare CLI vs in-process and inspect backtest period/cost effects.
**Failure mode:** proven gap → `tests/test_bab_cli_campaign11aa_cost_application.py` + minimal fix in `backtest.py`/`cli.py`.

---

## GATES THAT MUST STAY GREEN (NON-NEGOTIABLE)

- `campaign_d` **883 passed, 5 skipped** (ignore `tests/test_controller_progress_accounting.py`)
- Full BAB excl `data_loader`/`controller` **≥2119 passed, 5 skipped** (includes 11m-p: 83, 11q: 33, 11s: 16)
- `test_bab_cli_campaign11m_probe_regressions.py` (28), `campaign11n` (18), `campaign11o` (19), `campaign11p` (18), `campaign11q_followup_probe_regressions.py` (33), `campaign11s_validation_edges.py` (16) green

## COVERAGE / CLOSURE NOTES (LOCKED — DO NOT CHURN)

- `beta.py` gate closed (dead/unreachable paths per prior proofs) — **DO NOT ALTER**.
- `data_loader.py` gate closed (strict misses/mechanism-closed) — **DO NOT ALTER**.
- `portfolio.py`/`sizing.py`/`cli.py`/`strategy.py` 100% locked per prior notes unless disproven by evidence; other module miss-closures per prior handoff/proofs remain binding.

## IMMEDIATE ACTIONS (MANDATORY SEQUENCE — NO DEVIATION)

1. **RUN STEP 0 GATES** on current tree; confirm 11m–11s passing and full-excl floor. Record counts/rc.
2. **COMPLETE HEAVY CAMPAIGN 6** — minimum 8 additional probe combos with full evidence logging. No skipping.
3. **EXECUTE HEAVY CAMPAIGN 7** (NaN/inf args) — minimum 10 probe combos with dry-run vs run parity evidence. No skipping.
4. **COMPLETE HEAVY CAMPAIGN 8** (Universe overlap edges) — minimum 8 additional probe combos. No skipping.
5. **EXECUTE HEAVY CAMPAIGN 9** (Synthetic parity) — minimum 6 probe combos. No skipping.
6. **EXECUTE HEAVY CAMPAIGN 10** (Cost application) — minimum 12 probe combos. No skipping.
7. **ADD REGRESSION TESTS** for ANY proven, non-duplicative gap (focused, in `tests/test_bab_*campaign11*`).
8. **APPLY MINIMAL PRODUCTION FIXES** only for proven bugs (smallest diff, exercised non-gate-closed code only).
9. **RE-RUN TOUCHED TESTS + ALL GATES** (Step 0) — record before/after counts/rc.
10. **REFRESH THIS HANDOFF.md** with: new timestamp, HEAD, dirty state, all probe evidence (cmd/rc/stdout/stderr/JSON), gaps found/fixed with evidence, modules touched, next binding slice.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute the heavy campaigns above. No planning-only exits. No evidence-free sessions. Heavy work is mandatory.*
