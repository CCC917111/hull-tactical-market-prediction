# Reproduction guide

## Environment

Python 3.12 is the tested target. `requirements.in` lists direct dependencies; `requirements.txt` pins the complete resolved environment. Create the virtual environment and install the kernel as shown in the root README. JupyterLab is included for interactive use. No service credentials or `.env` file is needed for local execution.

On macOS, LightGBM and XGBoost require the OpenMP runtime (`libomp`). If either import fails with a missing-library error, install that library through Homebrew (`brew install libomp`). The verification record describes the temporary OpenMP path used for this run. This environment was tested on macOS arm64; the lock file and other platforms have not been independently tested.

## Working notebook configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `HULL_TRAIN_PATH` | Repository `data/train.csv`, or exact competition path on Kaggle | Explicit training CSV |
| `HULL_TEST_PATH` | Repository `data/test.csv`, or exact competition path on Kaggle | Explicit inference CSV |
| `HULL_OUTPUT_DIR` | Repository `artifacts`, or `/kaggle/working` | Generated files |
| `HULL_TARGET_COLUMN` | First recognized target | Optional explicit target |
| `HULL_MODEL_PATH` | Empty | Explicit path to an optional trusted pickle |
| `HULL_ALLOW_PICKLE` | `0` | Set to `1` only to load that trusted pickle |
| `HULL_RUN_KAGGLE_SERVER` | `0`; automatically enabled for competition reruns | Enable competition gateway/server |
| `HULL_N_JOBS` | `1` | CPU threads for the forest and boosting models |

Paths are absolute in the runner; notebook defaults are derived from the repository root, so launching Jupyter from `notebooks/` also works. The exact Kaggle input path takes precedence when present. Ambiguous recursive file discovery was removed.

Pickle deserialization can execute code. Automatic discovery of arbitrary input pickles is disabled. Loading requires both an explicit model path and an opt-in. A supplied model must contain the model dictionary, raw feature names, imputer (or `None`), raw training medians, selected feature names, scaler, anomaly detector and winsorization bounds. Legacy pickle schemas may fail loudly rather than silently substituting a model. The notebook trains before the optional model-loading cell, preserving the historical execution order.

## Local batch run

```bash
python scripts/run_notebook.py --train data/train.csv --test data/test.csv
```

Optional arguments: `--output-dir`, `--kernel` (default `hull-tactical`), and `--timeout` per cell (default 1800 seconds). The runner fails before kernel execution if CSVs are missing and restores the caller's environment variables after execution. The working notebook contains no automatic package installation; its environment must be prepared first.

The generated `submission.csv` uses `row_id,prediction`. IDs come from `row_id`, then `batch_id`, then row positions. The output should be inspected against the competition's required schema; it is not independently validated as an accepted submission.

## Kaggle execution

1. Upload the **working** notebook, attach the authorized competition data, and ensure its Python dependencies are available. For offline competition reruns, prepare packages ahead of time in an authorized Kaggle environment rather than installing during inference.
2. The notebook accepts pandas input and Polars batches (converted through `to_dicts`) and other objects exposing `to_pandas`. The competition-provided `kaggle_evaluation` package is not a PyPI dependency here and was not bundled in the archive.
3. For a local Kaggle gateway check, set `HULL_RUN_KAGGLE_SERVER=1` before the final cell. For `KAGGLE_IS_COMPETITION_RERUN`, the server is enabled automatically and calls `serve()`.
4. Confirm the latest competition API and scoring contract in the [official competition](https://www.kaggle.com/competitions/hull-tactical-market-prediction). Its description requires the evaluation API. A standalone CSV is insufficient evidence of accepted submission.

The Kaggle gateway and private evaluation were not run during packaging. The local smoke test substitutes deterministic synthetic numeric CSVs, not competition records.

## Dependency maintenance

The working notebook moves XGBoost `early_stopping_rounds` into `XGBRegressor(...)`, matching the [official estimator API](https://xgboost.readthedocs.io/en/stable/python/python_api.html#xgboost.XGBRegressor). If dependencies change, regenerate the resolved requirements and rerun all three checks in the README. Never infer leaderboard equivalence from a successful import or synthetic run.
