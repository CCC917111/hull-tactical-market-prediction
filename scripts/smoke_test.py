#!/usr/bin/env python3
"""Execute the full working notebook with synthetic data in a temporary folder."""
from pathlib import Path
import tempfile

import numpy as np
import pandas as pd

from run_notebook import execute_notebook


def main():
    rng = np.random.default_rng(42)
    n_train, n_test = 320, 24
    features = [f"M{i}" for i in range(8)]
    train = pd.DataFrame(rng.normal(size=(n_train, len(features))), columns=features)
    target = 0.004 * train["M0"] - 0.002 * train["M1"] + rng.normal(0, 0.01, n_train)
    train.loc[::9, "M2"] = np.nan
    train.loc[::37, "M3"] = 15.0
    train["date_id"] = np.arange(n_train)
    train["forward_returns"] = target
    test = pd.DataFrame(rng.normal(size=(n_test, len(features))), columns=features)
    test.loc[::3, "M2"] = np.nan
    test.loc[0, "M3"] = 50.0
    # Verify that missing test features are handled, and extra identifiers excluded.
    test = test.drop(columns="M7")
    test["row_id"] = np.arange(1000, 1000 + n_test)
    test["date_id"] = np.arange(n_train, n_train + n_test)
    with tempfile.TemporaryDirectory(prefix="hull-smoke-") as temporary:
        folder = Path(temporary)
        train.to_csv(folder / "train.csv", index=False)
        test.to_csv(folder / "test.csv", index=False)
        csv, _ = execute_notebook(folder / "train.csv", folder / "test.csv", folder / "outputs")
        result = pd.read_csv(csv)
        assert list(result.columns) == ["row_id", "prediction"], result.columns
        assert len(result) == n_test, result.shape
        np.testing.assert_array_equal(result["row_id"], test["row_id"])
        assert not result["row_id"].duplicated().any()
        assert np.isfinite(result["prediction"]).all()
        assert result["prediction"].between(0, 2).all()
    print("PASS: full synthetic training, inference and CSV checks (320 train / 24 test rows).")
    print("Competition data, evaluation gateway and leaderboard scores were not tested.")


if __name__ == "__main__":
    main()
