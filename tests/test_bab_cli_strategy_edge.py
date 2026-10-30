"""Edge-branch coverage for cli.py.

Cover the ``__main__`` SystemExit guard path.
"""

import runpy
import sys

import pytest


class TestCliMainGuard:
    def test_cli_run_as_main_raises_system_exit(self):
        # cli.py:62-63 ``if __name__ == "__main__": raise SystemExit(main())``
        old_argv = sys.argv
        sys.argv = ["cli", "--synthetic"]
        try:
            with pytest.raises(SystemExit):
                runpy.run_module(
                    "strategies.betting_against_beta.cli",
                    run_name="__main__",
                )
        finally:
            sys.argv = old_argv
