# INITIAL TASK MESSAGE (single durable handoff — leave for next agent; highest priority)

**Timestamp:** 2026-11-10T08:17:58Z
**Repo:** `Crypto-Betting-Against-Beta` (repo-name priority is binding: every slice must advance **Betting Against Beta** correctness/robustness/reporting fidelity; no unrelated refactors)
**HEAD/base:** `4d86549` (`chore(kilo): checkpoint agent session`, `main`, up-to-date with `origin/main`)
**Working tree:** **clean** (verified `git status --porcelain --untracked-files=all` empty). No in-flight edits.

**Environment/gates (recorded, not re-run this session except state checks):**
- deps: `import numpy,pandas,scipy,pytest` ok (rc=0) per prior session
- Campaign 11/12 regressions: **147 passed, rc=0** (`tests/test_bab_cli_campaign11{m,n,o,p,q,s,ab}*.py`) — includes C11ab surface-edge regressions and C12 in-process API cleanliness coverage as recorded in HANDOFF history
- `campaign_d` data-loader subset (`-k campaign_d tests/test_bab_data_loader*.py`): **883 passed, 5 skipped, rc=0**
- Full BAB excl `data_loader`/`controller`: baseline **4807 passed, 35 skipped, rc=0** (floor must remain green)
- Probe evidence logs (outside repo): `/home/runner/work/_temp/kilo-tmp/c11_cli_surface_probe_evidence.log`, `/home/runner/work/_temp/kilo-tmp/c12_cli_api_probe_evidence.log`, `/home/runner/work/_temp/kilo-tmp/probe_evidence.log`

**Bottlenecks removed:** single durable handoff is current and unambiguous; no stale/competing handoff files; working tree clean; no blocked sessions identified.

---

## BINDING INITIAL TASK MESSAGE (execute immediately, do not defer)

**YOU MUST DO HEAVY WORK.** No planning-only exits. No single-pass probes. No evidence-free exits. Every session must produce probe logs (cmd/rc/stdout/stderr and JSON validity where applicable) and either new regression tests for proven gaps or explicit "no proven gaps" with evidence references.

1. **Stabilize baseline (Step 0 — MANDATORY, before any edit):** run and record gates with `export PYTHONPATH=$PWD PATH=$HOME/.local/bin:$PATH`
   - `python3 -c "import numpy,pandas,scipy,pytest"` → rc=0
   - `python3 -m pytest -q tests/test_bab_cli_campaign11m*.py tests/test_bab_cli_campaign11n*.py tests/test_bab_cli_campaign11o*.py tests/test_bab_cli_campaign11p*.py tests/test_bab_cli_campaign11q*.py tests/test_bab_cli_campaign11s*.py tests/test_bab_cli_campaign11ab*.py` → **≥147 passed, rc=0**
   - `python3 -m pytest -q -k campaign_d tests/test_bab_data_loader*.py` → **≥883 passed, 5 skipped, rc=0**
   - `python3 -m pytest -q tests/test_bab_*.py tests/test_betting_against_beta*.py --ignore=tests/test_bab_data_loader* --ignore=tests/test_controller*` → **≥4807 passed, 35 skipped, rc=0** (hard floor; investigate any regression before production edits)
   Treat prior campaign regressions as evidence; do not revert without cause.

2. **Campaigns 6–12 remain CLOSED (evidence-backed, no churn):** C6 benchmark absent/mismatch, C7 NaN/inf CLI args, C8 universe overlap (11s-locked), C9 synthetic CLI↔in-process parity, C10 cost application parity/monotonic drag, C11 CLI surface edges (`--from-prices` without `--data` fixed in `cli.py` + 11ab regressions), C12 in-process `main()` API error-path/subprocess parity — all previously probed. Do not churn without a new, statable, reproducible failure.

3. **Execute C13 — CLI dry-run + JSON/output edge cleanliness (≥12 distinct probe combos, HEAVY):**
   - Probe `--dry-run` with valid real fixtures and `--synthetic`; confirm rc=0, no Traceback, expected summary/config output, and no unintended side effects (no output file written unless explicitly specified/expected by contract).
   - Probe `--dry-run` + `--output <tmp>` (writable) vs normal run + `--output <tmp>`; verify JSON validity, required keys, and write semantics parity/intent.
   - Probe `--dry-run` combined with error cases: bad quantiles/sum, invalid `--beta-window`, negative costs/slippage, empty/whitespace `--universe`, `--from-prices` without `--data`, `--from-prices` with valid `--data` (REAL/EXP as suitable), missing/nonexistent `--data`, unwritable/dir output targets → rc=1 actionable messages, **no Traceback**.
   - Probe `--output` success-path JSON for normal runs (synthetic + fixture-based) and validate parseable JSON structure.
   - Capture **subprocess and in-process `main(argv)` parity** for ≥4 representative dry-run/error combos.
   - Use fixtures: `REAL=tests/fixtures/real_market_prices.csv`, `EXP=tests/fixtures/real_market_prices_expanded.csv`.
   - Log all probes (cmd/rc/stdout/stderr/JSON validity notes) to `/home/runner/work/_temp/kilo-tmp/c13_cli_dryrun_probe_evidence.log`.

4. **Triage and fix only proven gaps:** smallest possible `cli.py`-only fix for any reproducible C13 defect; add/extend regression tests in the appropriate campaign module (prefer a new `tests/test_bab_cli_campaign13*.py` if scope warrants). No gap → explicit "no proven gaps" with evidence refs in HANDOFF.

5. **Validate comprehensively and record:** rerun touched/new tests, C11 regression bundle, `campaign_d`, and full BAB excl `data_loader`/`controller` (and any directly impacted CLI suites). Record exact counts/rc in HANDOFF.

6. **Refresh this HANDOFF.md before finishing (MANDATORY):** update timestamp/HEAD/state, completed evidence (C13), gate results, touched modules, and the next binding heavy campaign with ≥12 probe-combo requirement.

**Prohibited:** `.github/workflows/*` edits; gate-closed churn in `beta.py`/`data_loader.py`; edits/commits to tracked `probe*`/`debug*`/`ast_probe.py`; weakening/deleting `batch148/149/172` or `campaign_d*`; commit/push unless explicitly requested. `cli.py` editable only for smallest proven fix from probe evidence. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by new evidence. **No planning-only exit. No evidence-free session.**

---

## SESSION EVIDENCE (this session, 2026-11-10T08:17:58Z @ 4d86549)

- Verified repo state: clean working tree, HEAD `4d86549` on `main` tracking `origin/main`.
- Confirmed existing durable handoff and campaign history; campaigns C6–C12 evidenced/closed per prior logs and regressions; C11ab `--from-prices`-without-`--data` fix present in `strategies/betting_against_beta/cli.py` and covered by `tests/test_bab_cli_campaign11ab_cli_surfaces.py`.
- No source/test/gate changes executed this session (handoff refresh only). Prior recorded gates remain the binding baseline; Step 0 must be rerun before next production work.

---

## §NEXT FOCUS HEAVY CAMPAIGN (priority order — execute exhaustively, no skipping)

**C13 — CLI dry-run + JSON output edge cleanliness (≥12 probe combos).** Execute the matrix in §BINDING INITIAL TASK MESSAGE item 3 with full subprocess+in-process evidence. Triage/fix only proven gaps (smallest `cli.py` change + regressions), else record explicit "no proven gaps". Then refresh this HANDOFF with C13 evidence and nominate C14 with a concrete ≥12-combo probe plan (e.g. CLI reporting/summary formatting & stdout/stderr separation vs JSON/file outputs across success/error/dry-run paths, or next highest-risk BAB CLI surface) — no generic "continue" handoff.

**GATES THAT MUST STAY GREEN (NON-NEGOTIABLE):** `campaign_d` **883 passed, 5 skipped**; full excl `data_loader`/`controller` **≥4807 passed, 35 skipped** (or higher, never below recorded floor without investigation); campaign11 bundle incl. 11ab **≥147 passed**.

**COVERAGE / CLOSURE NOTES (LOCKED):** `beta.py`/`data_loader.py` gate closed — DO NOT ALTER. `portfolio.py`/`sizing.py`/`strategy.py`/`backtest.py`/`signals.py`/`metrics.py` locked unless disproven by evidence. `probe*`/`debug*`/`ast_probe.py` tracked artifacts — do not edit/commit. Do not weaken/delete `batch148/149/172` or `campaign_d*`.

**IMMEDIATE ACTIONS (MANDATORY SEQUENCE):** 1) RUN STEP 0 GATES → record. 2) EXECUTE C13 probe matrix (≥12 combos) with evidence log. 3) TRIAGE/fix proven gaps only. 4) RE-RUN GATES + impacted suites. 5) REFRESH THIS HANDOFF.md with evidence and next binding campaign.

---

*Single durable handoff for `Crypto-Betting-Against-Beta`. Do not create competing handoff files; update this file in place. Future agents: this handoff is binding. You must execute heavy work with probe evidence. No planning-only exits. No evidence-free sessions.*
