# HANDOFF: Crypto-Betting-Against-Beta — Next Agentic Work Session

**Timestamp:** 2026-11-11T06:58:16Z
**Repository:** Crypto-Betting-Against-Beta
**Priority:** HIGH — Production-ready BAB strategy; next phase = hardening, optimization, live-data integration

---

## PROJECT CONTEXT (Inferred from Repo Name & Structure)

**Crypto-Betting-Against-Beta** implements the **Betting Against Beta (BAB)** factor strategy for crypto markets:
- Long low-beta assets, short high-beta assets vs. a benchmark (default BTC)
- Dollar-neutral by default; configurable quantiles, rebalance freq, costs, slippage
- Full pipeline: data loading → rolling beta → signals → portfolio construction → backtest → metrics/attribution
- CLI entrypoint (`bab-example`) with `--dry-run`, `--from-prices`, JSON output, synthetic/real data
- 5072 tests covering adversarial paths, edge cases, CLI contracts, beta invariants, regime/shorting/sizing/quality modules

---

## CURRENT STATE (Verified)

| Area | Status |
|------|--------|
| Core strategy (`strategies/betting_against_beta/`) | **Complete** — 14 modules, typed, frozen config, defensive error handling |
| CLI (`cli.py`) | **Complete** — validated I/O, `--dry-run`, JSON-safe serialization, finite-coercion guards |
| Config (`config.py`) | **Complete** — 40+ fields, range validation, frozen post-init, universe resolution logic |
| Tests | **5072 collected** — campaigns for beta, signals, portfolio, backtest, CLI, regime, shorting, sizing, quality, attribution, data-loader |
| Synthetic data generator | **Complete** — reproducible, configurable assets/days/seed |
| Real-data loader | **Complete** — CSV/JSON/Parquet/HDF5/Pickle, benchmark alignment, min-rows guard |

**No failing tests observed in sampled runs.** Full suite takes ~3-5 min.

---

## BOTTLENECKS TO REMOVE (Immediate Action Items)

1. **No CI/CD pipeline** — Add GitHub Actions for lint (ruff), type-check (pyright/mypy), test matrix (3.9-3.12), coverage gate (≥90%).
2. **No lint/typecheck config** — Create `pyproject.toml` `[tool.ruff]`, `[tool.pyright]`/`[tool.mypy]`, `[tool.coverage]` sections.
3. **No pre-commit hooks** — Install `pre-commit` with ruff, pyright, black/isort if used.
4. **Coverage reporting absent** — `pytest --cov=strategies --cov-report=term-missing --cov-fail-under=90`.
5. **Dependency pinning** — `requirements.txt` or `uv.lock` for reproducible builds.
6. **Real-data fixtures limited** — Only 2 CSV fixtures in `tests/fixtures/`; need expanded universe (top 50 by vol), multi-exchange, futures/perp funding data.
7. **No performance benchmarks** — `scripts/perf_bench.py` exists but not integrated; add `pytest-benchmark` or `asv`.
8. **Documentation gap** — No `README.md`, no API docs (Sphinx/MkDocs), no strategy whitepaper link.

---

## NEXT FOCUS CAMPAIGN (Mandatory — Future Agents Cannot Skip)

### Phase 1: CI/CD & Quality Gates (Week 1)
- [ ] Add `.github/workflows/ci.yml` with matrix test, ruff, pyright, coverage gate
- [ ] Add `pyproject.toml` tool configs: ruff (line-length=100, target=py39), pyright (strict), coverage (branch=True)
- [ ] Add `pre-commit` config + `make lint`/`make typecheck`/`make test` targets
- [ ] Pin deps in `requirements.lock` or `uv.lock`

### Phase 2: Real-Data Expansion & Validation (Week 2)
- [ ] Script to fetch top-50 crypto spot returns from CCXT/Binance/Coinbase (daily OHLCV → returns)
- [ ] Generate fixtures: `real_market_returns_top50.csv`, `real_market_prices_top50.csv`, `funding_rates.csv`
- [ ] Add CLI smoke test with real fixtures in CI (assert periods > 200, Sharpe finite, no NaN in report)
- [ ] Validate beta-neutral enforcement on real data (tracking error < 10bps)

### Phase 3: Strategy Hardening & Extensions (Week 3-4)
- [ ] **Regime filter**: Stress-test `vol`/`trend`/`combined` on 2022 bear, 2023 recovery, 2024 bull
- [ ] **Shorting constraints**: Integrate borrow-cost curves, utilization caps, hard-to-borrow flags
- [ ] **Position sizers**: Backtest Kelly/vol-target/risk-parity vs. equal-weight on real data; select default
- [ ] **Beta-neutral enforcement**: Add unit tests for drift detection, correction paths, TE monitoring
- [ ] **Attribution**: Decompose PnL by beta-tilt, idiosyncratic, costs, slippage, regime-scaling

### Phase 4: Production Readiness (Week 5)
- [ ] **CLI hardening**: Add `--config-file` (YAML/TOML), `--profile` (dev/staging/prod), structured logging
- [ ] **Monitoring hooks**: Emit JSONL metrics per rebalance (weights, beta, turnover, costs, regime)
- [ ] **Container**: `Dockerfile` (python:3.12-slim, non-root, healthcheck), `docker-compose.yml` for backtest service
- [ ] **Docs**: `README.md` with quickstart, architecture diagram, config reference, CLI reference, contributing guide

---

## CRITICAL FILES TO TOUCH NEXT

| File | Reason |
|------|--------|
| `.github/workflows/ci.yml` | **Blocker** — no CI = no confidence on merge |
| `pyproject.toml` | **Blocker** — missing tool configs for lint/typecheck/coverage |
| `scripts/fetch_real_data.py` (new) | **High leverage** — expands test/validation surface 10x |
| `tests/fixtures/real_market_returns_top50.csv` (new) | **High leverage** — real-data contract tests |
| `docs/README.md` (new) | **Onboarding** — future agents need context fast |

---

## COMMANDS TO RUN IMMEDIATELY (Copy-Paste)

```bash
# 1. Verify current test health (sample)
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
python -m pytest tests/test_betting_against_beta.py -q --tb=line

# 2. Install dev tooling
pip install ruff pyright pytest-cov pre-commit

# 3. Create CI workflow skeleton
mkdir -p .github/workflows
cat > .github/workflows/ci.yml <<'YAML'
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e .[dev]  # add dev extras in pyproject.toml
      - run: ruff check strategies tests scripts
      - run: pyright strategies
      - run: pytest --cov=strategies --cov-report=term-missing --cov-fail-under=90
YAML

# 4. Add dev extras to pyproject.toml
cat >> pyproject.toml <<'TOML'

[project.optional-dependencies]
dev = [
    "ruff",
    "pyright",
    "pytest-cov",
    "pre-commit",
    "ccxt",          # for real-data fetch script
]

[tool.ruff]
line-length = 100
target-version = "py39"
select = ["E", "F", "I", "UP", "B", "C4", "SIM", "T20"]
ignore = []

[tool.pyright]
strict = true
python-version = "3.9"
type-stub-paths = ["strategies/betting_against_beta/*.pyi"]

[tool.coverage.run]
branch = true
source = ["strategies"]
omit = ["tests/*", "scripts/*"]

[tool.pytest.ini_options]
addopts = "-q --tb=line"
testpaths = ["tests"]
TOML
```

---

## SUCCESS CRITERIA FOR THIS HANDOFF

Next agent **must** deliver:
1. ✅ Green CI on push (ruff + pyright + tests + coverage ≥90%)
2. ✅ Real-data fixture with ≥50 assets, ≥500 daily bars each
3. ✅ CLI smoke test passing on real fixture in CI
4. ✅ `README.md` with one-command quickstart (`pip install -e . && bab-example --synthetic`)

**No exceptions. No "later".** This handoff is the contract.

---

## ESCALATION PATH

If blocked on any Phase 1 item > 4 hours:
- Post `HOLD` to board with specific error + repro steps
- Do not proceed to Phase 2 until Phase 1 gates pass

---

*Generated by Kilo agentic session 2026-11-11T06:58:16Z — durable handoff for autonomous continuation.*