"""Regression checks for runtime fixes, using real notebook function definitions."""
import ast
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd
import polars as pl
from sklearn.ensemble import IsolationForest
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import Ridge

ROOT = Path(__file__).resolve().parents[1]


def load_function(name, namespace):
    notebook = json.loads((ROOT / "notebooks/kaggle_submission.ipynb").read_text())
    for cell in notebook["cells"]:
        if cell["cell_type"] != "code":
            continue
        for node in ast.parse("".join(cell["source"])).body:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                exec(compile(ast.Module(body=[node], type_ignores=[]), name, "exec"), namespace)
                return namespace[name]
    raise AssertionError(f"Missing function: {name}")


class NotebookFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng = np.random.default_rng(23)
        raw = pd.DataFrame(rng.normal(size=(80, 2)), columns=["M0", "M1"])
        raw.loc[0, "M1"] = np.nan
        imputer = IterativeImputer(estimator=Ridge(), random_state=42, keep_empty_features=True)
        filled = pd.DataFrame(imputer.fit_transform(raw), columns=raw.columns)
        forest = IsolationForest(random_state=42).fit(filled)
        cls.models = {
            "raw_feature_names": list(raw.columns), "imputer": imputer,
            "raw_feature_medians": raw.median(),
            "feature_names": ["M0", "M1", "is_anomaly", "anomaly_score"],
            "iso_forest": forest, "winsorize_bounds": {"M0": (-1.0, 1.0), "M1": (-1.0, 1.0)},
        }
        cls.namespace = {"np": np, "pd": pd, "models": cls.models}
        cls.preprocess = staticmethod(load_function("preprocess_test_data", cls.namespace))
        cls.weights = staticmethod(load_function("convert_to_weights", {"np": np}))

    def test_missing_values_features_and_nondefault_index(self):
        sample = pd.DataFrame({"M0": [0.2, 100.0, np.inf], "row_id": [1, 2, 3]}, index=[10, 20, 30])
        before = sample.copy(deep=True)
        result = self.preprocess(sample)
        self.assertEqual(result.shape, (3, 4))
        self.assertEqual(list(result.columns), self.models["feature_names"])
        self.assertTrue(np.isfinite(result.to_numpy()).all())
        self.assertEqual(result.loc[1, "M0"], 1.0)
        pd.testing.assert_frame_equal(sample, before)

    def test_missing_values_without_fitted_imputer(self):
        previous = self.models["imputer"]
        try:
            self.models["imputer"] = None
            result = self.preprocess(pd.DataFrame({"M0": [np.nan], "M1": [np.nan]}))
            self.assertTrue(np.isfinite(result.to_numpy()).all())
        finally:
            self.models["imputer"] = previous

    def test_polars_batch(self):
        result = self.preprocess(pl.DataFrame({"M0": [0.1], "M1": [None]}))
        self.assertEqual(result.shape, (1, 4))
        self.assertTrue(np.isfinite(result.to_numpy()).all())

    def test_all_weight_methods_are_finite_and_bounded(self):
        for method in ("enhanced_sigmoid", "adaptive", "percentile", "threshold"):
            with self.subTest(method=method):
                result = self.weights(np.array([-0.1, 0.0, 0.05, 0.2]), method)
                self.assertTrue(np.isfinite(result).all())
                self.assertTrue(((result >= 0) & (result <= 2)).all())

    def test_single_and_constant_sigmoid_predictions_are_neutral(self):
        for values in (np.array([0.03]), np.full(3, 0.02)):
            np.testing.assert_array_equal(self.weights(values), np.ones_like(values))

    def test_unknown_weight_method_is_rejected(self):
        with self.assertRaises(ValueError):
            self.weights(np.array([0.0, 0.1]), "unknown")


if __name__ == "__main__":
    unittest.main()
