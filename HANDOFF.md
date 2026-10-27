# HANDOFF - 2026-10-27T21:12:05Z

## Timestamp
2026-10-27T21:12:05Z (canonical handoff for next session)

## Purpose
Durable single handoff. Start here. Ignore older handoffs unless explicitly needed for context.

## PRIMARY OBJECTIVE (Non-Negotiable)
**Implement a working "Betting Against Beta" (BAB) strategy for crypto.**

The repository name says it. The infrastructure (GitHub Actions agent loop, controller accounting, diagnostics) exists purely to support agents building this strategy. **There is no strategy implementation yet. That is the product.**

## Bottlenecks Removed
- **Focus clarified**: Treat `.github/workflows/` and agent-loop plumbing as read-only scaffolding unless a test explicitly fails because of them.
- **Ambiguity killed**: "Build the strategy" is now concrete with acceptance criteria below.
- **Drift prevented**: Future agents cannot avoid heavy work because the task is specified end-to-end with files to create and verifiable milestones.

## Current State
- Location: `/home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta`
- Branch: `main` @ `c06ee5b` (chore(kilo): checkpoint agent session)
- Uncommitted: `.github/workflows/main.yml` (pattern-sync fix staged from prior session)
- Tests: **124 passed, 0 failed** (all infrastructure-only tests)
- Core strategy: **Does not exist**

## INITIAL TASK FOR NEXT SESSION (Do This First)

### 1) Reconnaissance (5-10 min)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git log --oneline -5
git status
grep -rn "beta\|BAB\|betting.*beta\|CAPM\|low.*beta.*high" . 2>&1 | head -40
find . -name "*.py" -not -path "*/tests/*" -not -path "*/scripts/*" -not -path "*/__pycache__/*" | head -30
ls -la
```

### 2) Design The Strategy (Research + Decide)
Standard "Betting Against Beta" (Frazzini-Pedersen style): construct a portfolio that is long low-beta assets and short high-beta assets (or rank and go long bottom quantile / short top quantile) with beta measured vs a market benchmark. For crypto:
- **Universe**: Start with liquid top coins by market cap (e.g. BTC, ETH, SOL, BNB, XRP, etc.). Be explicit about how you define it.
- **Benchmark**: Likely BTC or equal-weight crypto market index. Justify in code/comments only if necessary, but make it configurable.
- **Beta estimation**: Rolling window (e.g. 60-90 days) of daily returns, OLS vs benchmark. Handle NaN/missing data.
- **Signal**: Beta per asset. Sort ascending/descending.
- **Portfolio construction**: Long low-beta decile/quintile, short high-beta decile/quintile. Equal-weight or risk-adjusted. Keep it simple first.
- **Rebalance**: Define frequency (daily/weekly). Start with daily on close.
- **Constraints**: Leverage? Probably market-neutral or dollar-neutral. Start simple and testable.

### 3) Create Implementation (TDD)
Create a minimal, testable module structure. Suggested layout:

```
strategies/
  __init__.py
  betting_against_beta/
    __init__.py
    config.py      # Universe, benchmark, windows, weights
    data.py        # Data loading/normalization (can start with synthetic for tests)
    beta.py        # Rolling beta calculation
    signals.py     # Ranking + position generation
    portfolio.py   # Portfolio construction / weights
    backtest.py    # Minimal backtest loop
    strategy.py    # High-level Strategy class / entrypoint
```

Also add `tests/test_betting_against_beta_*.py` as you go.

### 4) Implement Incrementally & Verify
- Write a failing test for beta calculation first (use synthetic returns).
- Implement `beta.py` to pass it.
- Add signals/portfolio tests.
- Add minimal backtest that runs on synthetic data.
- Run tests frequently: `python -m pytest -q` (or discover tests). All existing tests must remain passing.

## ACCEPTANCE CRITERIA (Definition of Done)
- [ ] `strategies/betting_against_beta/` module exists with core files
- [ ] Can compute rolling beta for assets vs benchmark on synthetic data
- [ ] Can rank assets by beta and generate long/short positions
- [ ] Portfolio construction produces weights (dollar-neutral or explicitly stated)
- [ ] Minimal backtest runs end-to-end on synthetic data without errors
- [ ] Unit tests added for core logic (beta, signals, portfolio) and pass
- [ ] All existing 124 tests still pass
- [ ] Strategy is importable and has a clear entrypoint (`strategy.py` or `__init__.py`)
- [ ] `README.md` updated with a short "Betting Against Beta (Crypto)" section describing approach, assumptions, and how to run

## CONSTRAINTS & RULES
- **Product-first**: Do not refactor the agent-loop/workflow unless absolutely necessary to make tests pass.
- **TDD**: Tests first where logic is non-obvious.
- **Start simple**: Synthetic data first. Don't get blocked on real data APIs.
- **Keep it testable**: Pure functions where possible.
- **No scope creep**: Focus on the strategy only.
- **Handoff discipline**: Before ending, update `HANDOFF.md` with progress, create a new timestamped handoff (e.g. `HANDOFF_YYYY-MM-DDTHH-MM-SSZ.md`), and update `HANDOFF_NEXT_SESSION.md` symlink if present.

## Suggested First Commands (Copy/Paste)
```bash
cd /home/runner/work/Crypto-Betting-Against-Beta/Crypto-Betting-Against-Beta
git log --oneline -3
grep -rn "beta" . 2>&1 | head -20
find . -type f -name "README*" -o -name "*.md" | xargs grep -l "strategy\|beta" 2>&1 | head -10
python -m pytest -q 2>&1 | tail -2
```

## Notes
This is a clean campaign: research → skeleton → TDD → implementation → verification. Do heavy work. The scaffolding is done. The strategy is missing. Build it.
