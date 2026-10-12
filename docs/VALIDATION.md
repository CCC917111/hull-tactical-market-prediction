# Validation record

Initial packaging checked on **2026-10-12**, on macOS arm64 using **CPython 3.12.14**. The environment was resolved from `requirements.in`, installed into an isolated temporary virtual environment, and recorded in `requirements.txt`.

Key versions: NumPy 2.5.4, pandas 2.3.3, scikit-learn 1.9.1, LightGBM 4.7.0, XGBoost 3.4.1, Polars 1.44.2, nbformat 5.11.1, nbclient 0.11.0, ipykernel 7.4.0 and JupyterLab 4.6.4. These are packaging-time versions, not the unknown historical submission environment.

| Check | Result | What it establishes |
| --- | --- | --- |
| Dependency imports | Passed after local OpenMP path setup | Installed Python and native packages can load |
| Notebook format and syntax | Passed, 12 code cells | Working notebook is valid nbformat and parses as Python |
| Function regression tests | 6 passed | Missing values/features, non-default indexes, outlier clipping, no-imputer fallback, Polars input and weight mapping |
| Full notebook smoke test | Passed, 320 training and 24 inference rows | All base learners, meta-learner, preprocessing, inference and CSV generation execute |
| Synthetic output checks | Passed | Exact `row_id,prediction` columns, preserved IDs, correct row count, finite weights in `[0, 2]` |
| Source preservation | Passed | Original notebook and screenshot SHA-256 hashes match source archive |
| PDF privacy and rendering | Passed | Eight pages, student ID text absent; pages 2-8 render identically |
| Publishable-file inspection | Passed | No common credential patterns, saved working-notebook outputs, datasets, model artifacts or files over 10 MiB detected |

Commands from the repository root:

```bash
python scripts/validate_repository.py
python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

The six test methods cover: bounded weights for four mappings; missing values/features with arbitrary indexes and clipping; training-median fallback; Polars batches; neutral single/constant sigmoid predictions; and invalid-method rejection.

## Local native dependency detail

This Mac did not have a system OpenMP installation, so initial LightGBM/XGBoost imports failed. For verification, the existing `libomp.dylib` shipped with the installed scikit-learn wheel was reused by setting `DYLD_LIBRARY_PATH` to that environment's `sklearn/.dylibs` directory. No system library or global setting was changed, and no native library is committed. A typical macOS installation should use `brew install libomp` as described in the setup notes.

Notebook execution also needed permission for the Jupyter kernel's temporary local communication ports in the sandbox. The full test then completed successfully. Synthetic inputs and executed notebooks were kept in temporary folders and removed after the test; no competition data was used.

## Limits of this verification

- Real competition CSVs, their schema, original data hashes and trained models were not supplied.
- The Kaggle evaluation package/gateway, hidden data and competition submission acceptance were not tested.
- The reported leaderboard score and report's baseline/ensemble comparisons were not reproduced.
- Synthetic execution cannot establish predictive quality or repair the temporal leakage described in `KNOWN_LIMITATIONS.md`.
- Credential scanning uses common patterns and manual inspection; it is not an exhaustive secret-detection guarantee. PDF text and image content were reviewed separately.
- Other operating systems and Python versions were not tested.

## Later reference-data checks

The owner-requested reference CSV addition was checked separately from the initial synthetic run. The two exact source files are an explicit exception to the generic dataset and 10 MiB exclusions: training is 12,365,421 bytes, and test is 16,751 bytes. Their hashes, dimensions, ordered date IDs, finite training target and feature-list consistency are checked against `data/PROVENANCE.json` by the repository validator. The separately recorded preprocessing results are in `docs/DATA_RECOMPUTATION.md`. They do not establish the historical leaderboard result.

The working notebook was subsequently executed end-to-end with the included 9,021-row training CSV and 10-row example test CSV. All three prediction models and the stacking model trained, inference completed, and the generated CSV passed row-count, unique-ID, finite-weight and [0, 2] bound checks. The executed notebook and generated predictions remain under ignored `artifacts/`. This is a new local reference-snapshot run; the Kaggle gateway and historical leaderboard score were not reproduced. The exact command and check summary are recorded in `data/PROVENANCE.json`.
