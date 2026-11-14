import json
import subprocess
import sys
from pathlib import Path


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def test_perf_baseline_record_and_check(tmp_path):
    baseline = tmp_path / "perf.json"
    dataset = "tests/fixtures/real_market_prices.csv"
    rec = run(
        [
            sys.executable,
            "scripts/perf_baseline.py",
            "--record",
            "--dataset",
            dataset,
            "--output",
            str(baseline),
            "--repeats",
            "2",
            "--warmup",
            "0",
        ]
    )
    assert rec.returncode == 0, rec.stderr + rec.stdout
    assert baseline.exists()
    payload = json.loads(baseline.read_text())
    assert "metrics" in payload and "command" in payload
    m = payload["metrics"]
    assert m["shape"][0] > 0 and m["beta_ms_median"] >= 0 and m["full_ms_median"] >= 0

    chk = run(
        [
            sys.executable,
            "scripts/perf_baseline.py",
            "--check",
            "--baseline",
            str(baseline),
            "--dataset",
            dataset,
            "--repeats",
            "2",
            "--warmup",
            "0",
            "--time-tolerance",
            "5.0",
            "--mem-tolerance-mb",
            "200",
        ]
    )
    assert chk.returncode == 0, chk.stderr + chk.stdout
    out = json.loads(chk.stdout)
    assert out["failures"] == []
