import coverage, pytest, os, sys

ROOT = os.getcwd()
target = os.path.join(ROOT, "strategies", "betting_against_beta", "data_loader.py")
cov = coverage.Coverage(source=[target], data_file=None)
cov.start()
files = sorted(
    os.path.join(ROOT, "tests", f)
    for f in os.listdir(os.path.join(ROOT, "tests"))
    if f.startswith("test_") and f.endswith(".py") and "data_loader" in f
)
rc = pytest.main(["-q"] + files)
cov.stop()
cov.save()
print("PYTEST_RC", rc)
cov.report(show_missing=True)