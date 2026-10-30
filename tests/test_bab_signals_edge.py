"""Edge-branch coverage for signals.py reference implementation.

Cover the single-row DataFrame beta extraction and the no-finite-beta skip.
"""

import numpy as np
import pandas as pd

from strategies.betting_against_beta import signals


class TestReferenceGenerateBabSignals:
    def test_single_row_dataframe_extracts_series(self):
        # signals.py:28 ``betas = betas.iloc[0]`` for a 1-row DataFrame
        out = signals._finite_beta_series(pd.DataFrame([[0.5]], columns=["A"]))
        assert out is not None
        assert float(out.iloc[0]) == 0.5

    def test_row_with_no_finite_betas_is_skipped(self):
        # signals.py:70-71 ``if clean is None: continue``
        out = signals._reference_generate_bab_signals(
            pd.DataFrame([[np.nan, np.nan]], columns=["A", "B"])
        )
        assert (out.iloc[0] == 0).all()

    def test_vectorized_matches_reference_on_random_input(self):
        rng = np.random.default_rng(7)
        betas = pd.DataFrame(rng.normal(1.0, 0.5, size=(20, 6)),
                             columns=[f"A{i}" for i in range(6)])
        vec = signals.generate_bab_signals(betas)
        ref = signals._reference_generate_bab_signals(betas)
        pd.testing.assert_frame_equal(vec, ref)
        assert np.all(np.isfinite(vec.to_numpy()))
