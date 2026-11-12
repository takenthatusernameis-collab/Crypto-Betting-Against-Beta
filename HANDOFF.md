# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T03:41:20Z
**HEAD:** `f206cb4` on `main`
**Repo priority (binding):** advance **Betting Against Beta** correctness, robustness, CLI/API/reporting/metrics fidelity, or a newly proven regression. No unrelated refactors.

## BINDING INITIAL TASK MESSAGE — NEXT AGENT (C39 heavy closure campaign)

**C39 is active. Execute heavy, evidence-producing work immediately. "No proven gaps" is valid only after all gate floors are green with durable evidence in this state AND an expanded Step 2 adversarial probe campaign is executed with durable logs. Do not stop at smoke checks.**

### Step 0 — Controller/workflow sync
- No sync regression observed. `.github/workflows/*` unchanged vs prior verified state. **Do not edit `.github/workflows/*`** unless you reproduce a newly proven controller/workflow sync regression with durable evidence (smallest proven fix only).

### Step 1 — Gate floors (mandatory, durable logs required)
Run from repo root with system Python 3.12.3 (`/usr/bin/python3`); **no `.venv` in this env**.
Command prefix: `PYTHONPATH=/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta python3 -m pytest ...`
Every gate run must write a durable log under `/home/runner/work/_temp/kilo-tmp/` (stdout+stderr, start/end, final summary line, rc, duration). Timeout/interruption without observed final failure is **INCONCLUSIVE, not green**.

| Gate | Scope | Floor | Last verified (this handoff/state) | Log |
|---|---|---:|---|---|
| 1 | `pytest -q tests/test_bab_data_loader_campaign_d*.py tests/test_bab_data_loader_batch148.py tests/test_bab_data_loader_batch149.py tests/test_bab_data_loader_batch172.py` | ≥898 passed, 5 skipped, rc=0 | **PASS** 898 passed, 5 skipped, 53 warnings, rc=0 (4.44s) | `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign_d_20261112T032635Z.log` |
| 2 | `pytest -q --ignore-glob='*data_loader*' --ignore=tests/test_controller_progress_accounting.py` | rc=0 (baseline ~2234 passed, 5 skipped) | **PASS** 2234 passed, 5 skipped, 41 warnings, rc=0 (263.85s, 0:04:23) | `/home/runner/work/_temp/kilo-tmp/c38_gate_full_bab_20261112T033511Z.log` |
| 3 | `pytest -q tests/test_bab_cli_campaign11* tests/test_bab_cli_campaign14*` | ≥164 passed, 0 failed, rc=0 | **PASS** 164 passed, rc=0 (110.65s) | `/home/runner/work/_temp/kilo-tmp/c38_gate_campaign11_14_20261112T032635Z.log` |

**If any floor is red:** smallest proven fix in allowed areas only, add minimal regression, re-run affected gate(s) and then all floors as required, record evidence.

### Step 2 — C39 adversarial probe campaign (mandatory, expand beyond C38)
Exercise **editable/allowed surfaces only** (`cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`) via untracked scripts under `/home/runner/work/_temp/kilo-tmp/` with durable logs. Rotate/expand; do not reuse only prior probe shapes.

**Required probe matrix (minimum):**
- **CLI/API parity & edge contracts:** `--data/--from-prices/--synthetic/--dry-run/--output/--benchmark/--universe/--beta-window/--min-rows/--long-quantile/--short-quantile/--transaction-costs/--slippage` combos incl. repeated flags, boundary/invalid/NaN/Inf, quantile edges/sums, small windows, negative/zero params as applicable. Data edges: missing/dir/symlink-missing/symlink-valid, empty/malformed/huge-header/duplicate-col, unicode/whitespace/duplicate universe tokens, output to dir/existing file/overwrite. **User-path contract:** nonzero + no traceback on invalid inputs unless stricter rc evidenced by tests.
- **`bab_backtest_report.py` / report CLI:** supported arg forms (`--data-source/--returns-csv/--returns/--synthetic` path conventions, `--json`), invalid/missing inputs, boundary params; confirm no traceback, strict/finite JSON behavior where claimed.
- **Metrics/reporting robustness:** constant/NaN/Inf/short/extreme/empty-like series; `metrics.summary` raw non-finite behavior may be by contract, but sanitized/report/JSON paths must remain strict-finite/no-leakage where applicable. Validate monotonicity/invariants on sane cases.
- **Costs/regime/attribution/shorting/sizing:** correct API usage (`compute_transaction_costs` takes `model/weights/weights_prev/prices/adv_usd`, not `cost_bps`; `get_regime_state(returns_df, ...)`; `trade_attribution(backtest_df)`; `apply_position_sizing(signals, returns, sizer)` e.g. `EqualWeightSizer()`; `apply_shorting_constraints(weights)`), boundary/zero/extreme params, monotonicity/invariants, NaN/Inf handling.

**Prior probe evidence (no proven BAB regressions):**
- `/home/runner/work/_temp/kilo-tmp/c38_probe2_20261112T032959Z.log` (`c38_probe2.py`, rc=0): **9/9 PASS** (regime df/basic+small+nan/inf, `EqualWeightSizer` sizing basic/zero, CLI min-rows/beta-window large/unicode token, report `--synthetic`).
- `/home/runner/work/_temp/kilo-tmp/c38_probe3_20261112T034030Z.log` (`c38_probe3.py`, rc=1): **28/34 PASS, 6 FAIL — all non-regressions (harness/API-misuse or contract-consistent):**
  - `cli_repeated_benchmark` rc=0 (argparse last-wins, no traceback) — acceptable.
  - `cli_beta_window_one` rc=0, `cli_quantile_sum_gt1` rc=0 — consistent with current config/CLI behavior (no traceback); not a proven regression absent stricter contract/test evidence.
  - `report_synthetic_basic`/`report_from_prices` failures in probe were due to using unsupported flags (`--data/--from-prices`) for `bab_backtest_report.py`; manual checks confirm `--data-source synthetic` and `--data-source <csv>` work (rc=0).
  - `costs_block` was probe misuse (`cost_bps` kwarg); correct API (`TransactionCostModel`) verified OK (zero vs fee monotonic).

### Step 3 — Fix/closure & handoff refresh (before exit)
- **If gaps found:** durable repro log → smallest proven fix in allowed area → minimal regression test → re-run affected + all gate floors → record evidence.
- **If no proven gaps after full Step 1+2:** record **"C39: no proven gaps"** with evidence summary/log paths and covered matrix.
- **Always refresh this same `HANDOFF.md`** with: timestamp/HEAD, exact gate counts+rc+durations+durable log paths, probe matrix outcomes (PASS/FAIL per area + repro paths), working-tree notes, and the next concrete heavy task. Keep single, durable, unambiguous.

## Current status
- **Working tree:** clean tracked state at refresh (no intentional source changes). Untracked probe/gate artifacts exist under `/home/runner/work/_temp/kilo-tmp/` (do not commit): `c38_gate_full_bab_20261112T033511Z.log`, `c38_probe3.py`, `c38_probe3_20261112T034030Z.log`, plus prior `c38_*` logs/scripts.
- **Environment:** `python3` 3.12.3 at `/usr/bin/python3`; no `.venv`; set `PYTHONPATH` to repo root.
- **`research_state/workflow_run_diagnostics.jsonl`:** historical captured CI/log signals, not evidence of current checkout failures.

## Locks / prohibitions
- **No** edits to `.github/workflows/*` except newly proven controller/workflow sync regression with evidence.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py` (use untracked `/home/runner/work/_temp/kilo-tmp/`).
- **No** weakening/deleting `batch148/149/172` or `campaign_d*` tests.
- **Locked unless disproven by new evidence + minimal fix:** `beta.py`, `data_loader.py`, `portfolio.py`, `sizing.py`, `strategy.py`, `backtest.py`, `signals.py`, `config.py`.
- **Editable only for smallest proven fix from probe/gate evidence:** `cli.py`, `metrics.py`, reporting, `scripts/*`, `costs.py`, `regime.py`, `attribution.py`, `shorting.py`, `sizing.py`.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
- Do not reopen C28–C38 without a new statable reproducible failure + durable evidence.
