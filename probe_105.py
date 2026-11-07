"""Batch 105 mechanism probe (uncommitted scratch). Verifies 403-404 hypothesis."""
import re
import numpy as np
import pandas as pd

from strategies.betting_against_beta import data_loader as dl

PAT = re.compile(r'^[+-]?(\d+)(\.\d+)?([eE][+-]?\d+)?$')

# 1) float() on regex-matched overflow strings -> inf (never raises)
for s in ["1e999", "1e400", "9.9e999", "1e309"]:
    assert PAT.match(s), s
    assert float(s) == float("inf"), s
print("float() never raises for regex-matched strings: OK")

# 2) _coerce_to_datetime_scalar on overflow strings: returns Timestamp (no raise)
for s in ["1e999", "1e400", "9.9e999"]:
    r = dl._coerce_to_datetime_scalar(s)
    assert isinstance(r, pd.Timestamp), (s, type(r))
    assert not pd.isna(r), (s, r)
print("coercer returns Timestamp for overflow epoch strings: OK")

# 3) Outer except 403-404 unreachable: force float() to raise via subclass
class BadFloat(str):
    def __float__(self):
        raise RuntimeError("boom")

bf = BadFloat("1e999")
assert PAT.match(bf)
try:
    float(bf)
    raise AssertionError("expected float() to raise")
except RuntimeError:
    pass

# 4) Does the production code path hit 403-404 for BadFloat?
try:
    r = dl._coerce_to_datetime_scalar(bf)
    print("BadFloat coercer result:", type(r).__name__, repr(r))
except Exception as e:
    print("BadFloat raised:", type(e).__name__, e)

# 5) Direct coverage probe: instrument 403-404
import coverage

cov = coverage.Coverage(branch=True, source=["strategies.betting_against_beta"])
cov.start()
try:
    dl._coerce_to_datetime_scalar("1e999")
    dl._coerce_to_datetime_scalar("1e400")
    dl._coerce_to_datetime_scalar("9.9e999")
    dl._coerce_to_datetime_scalar("123")
    dl._coerce_to_datetime_scalar("1e309")
    dl._coerce_to_datetime_scalar(BadFloat("1e999"))
finally:
    cov.stop()
    cov.save()

data = cov.get_data()
for f in data.measured_files():
    if f.endswith("data_loader.py"):
        lines, excluded = cov.analysis2(f)
        executed = {ln for ln in lines if ln in data.lines(f)}
        missing = [ln for ln in lines if ln not in executed]
        print("executed lines include 403:", 403 in executed, "404:", 404 in executed)
        print("missing:", missing)

print("PROBE DONE")
