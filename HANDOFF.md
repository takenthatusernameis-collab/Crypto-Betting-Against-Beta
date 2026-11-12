# HANDOFF — Crypto-Betting-Against-Beta (single durable handoff)

**Timestamp (refreshed):** 2026-11-12T22:12:20Z
**HEAD at session start:** `70bcaaac440a6366785abd71ba9fefbb20c1e337` (working tree CLEAN — all C54 session changes committed; nothing uncommitted)
**Code state:** `cli.py` print-block hardened (output failures surface as rc=1); `tests/test_bab_cli_coverage_push.py` regression updated; `docs/COVERAGE_NOTES.md` added; `docs/unreachable_proofs.md` + `docs/unreachable_proofs_append_b150.py` deleted. Focused CLI suites passed (86 passed). Full suite **not** re-run after these edits — last recorded C54 Step 1 baseline: **5069 passed / 35 skipped / RC=0**, no ignores, log `/home/runner/work/_temp/kilo-tmp/c54_gates/full_20261112T214930Z.log`.
**Repo:** `crypto-betting-against-beta` — BAB (Betting Against Beta) market-neutral product: long low-beta / short high-beta crypto vs BTC benchmark.

## Why this handoff changed (read first)

The previous handoff's "binding" instruction was **C53 = author ≥40 more synthetic adversarial probes, then C54/C55…** forever. The C54 refresh removed that loop:

- **The product is saturated.** Coverage is **99%** (4535 stmts, 66 miss). `quality.py`, `regime.py`, `shorting.py`, `sizing.py`, `portfolio.py`, `strategy.py`, `attribution.py`, `data_sources.py`, `backtest.py`, `data.py` are at **100%**. There is no meaningful "new probe surface" left.
- **289 test files / 5069 tests for a 6.7k-line product** (≈0.75 tests per product line), produced by **1894 auto-commits in 5 days** of a cron loop (`.github/workflows/main.yml` runs Kilo every 5 minutes).
- **`docs/unreachable_proofs.md` is 2152 lines** of "no reduction identified" reports — an append-only log that consumed sessions without shipping anything.
- **The gates were engineered so failures could not surface.** Gate 2 ran `--ignore=tests/test_controller_progress_accounting.py`, which hid **2 real failures** for an unknown number of sessions. Any campaign built on "gates green" was measuring the wrong thing.

**Binding policy from C54 onward: probe-count quotas are abolished.** Do not author probes for their own sake. Every session must produce a **durable, verifiable product improvement** (correctness, robustness of error surfacing, or performance), with tests only as proof. If no such improvement exists, say so with evidence and stop — do not manufacture probe volume.

## C53 — unblock (executed in the C53 session)

**Blocker found and fixed (real, reproducible):**

```
FAILED tests/test_controller_progress_accounting.py::TestStageSafeChangesPatternSync::
  test_python_patterns_are_subset_of_workflow
  - Python EXCLUDE_PATTERNS has patterns missing from the workflow's
    stage_safe_changes list: ['*/.github/workflows/*']
FAILED ...::test_nested_workflow_pattern_is_present_in_workflow
```

**Root cause:** commit `32fbdf2` (2026-10-27) added assertions claiming the workflow's bash `case "$changed_path" in` list must contain every Python `EXCLUDE_PATTERNS` entry. It does not, and cannot: `.github/workflows/*` is protected by an explicit force-restore in the checkpoint block (`.github/workflows` is maintainer-managed; the repo token cannot authorize workflow edits). Encoding it as a case pattern would assert a protection bash never performs.

**Fix (test-only, `tests/test_controller_progress_accounting.py`):** the two subset assertions now exclude the two workflow-managed patterns (`WORKFLOW_MANAGED_DIRECTLY`), and a new test `test_workflow_directory_is_protected_by_restore_not_case_pattern` asserts the *actual* enforcement — `git restore --source=$base_sha --staged --worktree -- .github/workflows` and `git clean -fd -- .github/workflows` are present, the pattern is in Python `EXCLUDE_PATTERNS`, and it is **not** a case pattern. `test_nested_workflow_pattern_is_present_in_workflow` now checks the real contract instead of the false one.

**Evidence:**
- `python3 -m pytest -q tests/test_controller_progress_accounting.py` → **69 passed**
- Full non-data_loader suite incl. previously-masked file → **2334 passed, 5 skipped, rc=0**
- Before/after on the controller file itself (via `git stash`): **2 failed, 66 passed** before → **69 passed** after.

**Measured product facts (reusable, verified in the C53 session):**

| Metric | Value |
|---|---|
| Product LOC (`strategies/betting_against_beta/*.py`) | 6,736 |
| Coverage (`--source=strategies/betting_against_beta`) | **99%** (4535 stmts, 66 miss) |
| Test files / tests | 289 files / 5069 passed + 35 skipped |
| Auto-checkpoint commits | 1,894 |
| `docs/unreachable_proofs.md` | 2,152 lines (append-only noise) |
| Broad `except Exception` in product | **244** (**103 direct silent `pass`**) — **167** broad / **85** silent in `data_loader.py` alone |
| `data_loader.py` | 2,270 LOC / 1,683 stmts — 34% of the whole product |

**Silent-pass definition used below:** the handler body is exactly `pass` after ignoring a docstring, verified by AST at `f940534`. Fallback handlers that `return`, assign a default, or re-raise are not counted as silent. The earlier "101 silent pass" and per-module table were not AST-verified and undercounted `data_loader.py` (actual: 85); use these corrected numbers.

**Remaining uncovered lines (the *only* honest "coverage gap", ~66 lines):** `data_loader.py` 43-44, 234-244, 246-247, 268-269, 326, 338-342, 403-404, 641-642, 694-695, 791-792, 953 (mostly defensive `except Exception: pass` in date-parsing fallbacks); `beta.py` 124, 149-150, 162, 169-170, 188, 215-218, 356-359, 429-433; `cli.py` 5 lines; `metrics.py` 4; `signals.py` 2; `config.py` 2; `costs.py` 2. **These are 99%-saturation residue, not a campaign.** Do not spend sessions chasing them unless a line hides a real defect.

**CLI verified working end-to-end:** `--synthetic` → `Final cumulative return: 0.413704 / Periods: 252`, rc=0; `--data tests/fixtures/real_market_prices.csv --from-prices --benchmark BTC` → `0.339735 / 398`, rc=0; `--version` → `bab 0.1.0`.

## C54 Step 2 — in progress (attack broad `except Exception` / direct silent `pass`)

**Binding next task:** continue **C54 Step 2** in `strategies/betting_against_beta/cli.py` — audit remaining direct silent `except Exception: pass` handlers (AST-verified at 2026-11-12T22:10Z: **8** silent at lines **87, 192, 432, 447, 483, 498, 507, 562**; broad count **29**), convert only proven-invalid-path silences with regressions, and prove valid-path behavior preserved. Then proceed module-by-module: `costs.py` (59, 281), `config.py` (123), `regime.py` (139), `backtest.py` (116, 124, 160), `portfolio.py` (118, 131), `strategy.py` (396). `beta.py` and `data_loader.py` are high-risk — touch only for a specific reproducible defect plus a regression; no mechanical sweep.

**Execution order (binding, smallest proven diff first):**
1. **Continue `cli.py`.** The print block (~432/447 region) already surfaces failures as rc=1 with regression evidence. Remaining silent handlers to audit: **432, 447, 483, 498, 507** inside `_extract_cumulative` (these can mask a failed cumulative extraction by returning/wrong-defaulting instead of surfacing) and **562** in `_json_safe`; confirm **87/192** are intentional valid-path fallbacks or convert with proof. For each: narrow/surface only on a proven invalid path, add regression proving no silent plausible wrong output, and prove valid-path behavior preserved (focused CLI tests + full suite at module boundary). **Re-AST before each change** — line numbers drift after edits.
2. Then `costs.py` (59, 281), `config.py` (123), `regime.py` (139), `backtest.py` (116, 124, 160), `portfolio.py` (118, 131), `strategy.py` (396). One module per batch; do not mix modules in one commit.
3. `beta.py` and `data_loader.py` remain high-risk. Touch them only for a *specific, reproducible defect*; no mechanical sweep and no 167-line refactor.

**Rules for each conversion:**
- Convert the worst **silent** swallows into either a **narrowed exception type** or an **error that surfaces** (raise `BABDataError` with context, or record a diagnostic) — without changing behavior for valid inputs.
- Every conversion needs a **regression test proving the new behavior** (invalid input now raises/records instead of silently producing wrong data).
- **Prove each change is behavior-preserving for valid data**: run the module's focused tests after each conversion and the full suite at each module boundary. If a conversion changes valid-path behavior, revert that conversion.
- Do **not** do a mechanical sweep of all 244 at once. Work module by module, smallest diff first, full suite green after each module. Target: direct silent-`pass` count measurably reduced with evidence in this session.
- **No handoff-only execution session.** The next execution session must leave at least one product-code change plus its regression test, or a reproducible proof that every candidate in the batch is an intentional valid-path fallback. Updating this file is not progress.

## Step 3 — Performance (only if Step 2 is done or blocked)

`beta.py` rolling OLS has a numpy cache (`tests/test_beta_perf_numpy_cache.py`) and a perf bench (`scripts/perf_bench.py`). Measure, then optimize only with before/after numbers in the handoff. Correctness first; no speculative rewrites.

## Step 4 — Delete the busywork (DONE, committed in 70bcaaa)

`docs/unreachable_proofs.md` and `docs/unreachable_proofs_append_b150.py` removed; replaced with `docs/COVERAGE_NOTES.md` (<=40 lines) with measured 99% coverage, residual miss lines, and anti-probe-volume policy.

## Step 5 — Only after Steps 1–4 are durably recorded

If you still have capacity, add tests **only** for the residual missing lines listed above where you can show they represent reachable behavior, and re-measure. Do not invent probe volumes.

## Bottlenecks removed (do not reintroduce)

- The C52-era "≥40 new adversarial probes per session, then C54/C55…" loop is abolished (probe-count quotas abolished). Coverage is already 99%; there is no meaningful new probe surface.
- Gate 2's `--ignore=tests/test_controller_progress_accounting.py` is removed; that file hid 2 real failures. Never re-add any per-file `--ignore` to a gate.
- `docs/unreachable_proofs.md` append-only busywork is replaced (Step 4, done).
- **The old "editable vs locked" contradiction is removed.** Every product module is editable for the smallest proven fix. Only `beta.py` and `data_loader.py` require a specific reproducible defect plus a regression; they are not blanket-locked. This prevents the next agent from treating `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, or `config.py` as off-limits while the campaign table calls them editable.
- **No handoff-only execution session.** The next execution session must produce a product-code change plus regression evidence, or a reproducible proof that every candidate is an intentional valid-path fallback. Do not spend the session rewriting this file.

Before exit (mandatory): full suite green (single command, no ignores) with a timestamped log under `/home/runner/work/_temp/kilo-tmp/c54_gates/`; refresh this file (timestamp/HEAD, what shipped, before/after evidence, residual debt with numbers, next concrete step); keep `AGENT_HANDOFF.md` pointer-only; commit nothing unless explicitly requested.

## Completed campaigns (do not reopen without new reproducible failure + durable evidence)

- **C42–C51:** CLOSED (historical probe campaigns; superseded by the policy above).
- **C52:** CLOSED — 43/43 probes, 1 fix (`cli._extract_cumulative`), gates green *as measured with the controller file ignored* — see caveat above.
- **C53:** CLOSED — unblocked the suite. 2 real failures fixed in `tests/test_controller_progress_accounting.py`; full non-data_loader gate now 2334 passed / 0 failed (was 2 failed / 5066 passed). Product code unchanged; coverage 99%.
- **C54 Step 1:** CLOSED — full suite is the gate, no ignores, 5069 passed / 35 skipped / RC=0 (2026-11-12T21:49:30Z).
- **C54 Step 4:** CLOSED — busywork docs deleted; `docs/COVERAGE_NOTES.md` added.

## Locks / prohibitions

- **No** edits to `.github/workflows/*` (maintainer-managed; the repo token cannot authorize it). The checkpoint block force-restores that directory.
- **No** edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; use untracked `/home/runner/work/_temp/kilo-tmp/`.
- **No** weakening/deleting `batch148/149/172`, `campaign_d*`, or `tests/test_bab_*_c5*_regressions.py`.
- **Editable for smallest proven fix:** all product modules, including `portfolio.py`, `strategy.py`, `backtest.py`, `signals.py`, and `config.py`. `beta.py` and `data_loader.py` require a specific reproducible defect plus a regression; no mechanical sweep.
- **Do not** re-add `--ignore=tests/test_controller_progress_accounting.py` or any per-file ignore to any gate.
- **No commit/push unless explicitly requested.** Do not revert intentional changes.
