# Reference data preprocessing record

On **12 October 2026**, the retained original notebook's preprocessing and feature-selection code was executed on the public CSV copy now included under `data/`. Source commits, file hashes and exact feature names are recorded in [PROVENANCE.json](../data/PROVENANCE.json).

The training file was committed in its source repository on 26 November 2025. It is compatible with the course notebook's input format, but has not been established as the team's exact historical input.

## Recorded results

| Stage | Result |
| --- | --- |
| Training CSV | 9,021 rows, 98 columns |
| Candidates after dropping date ID and target | 96 columns |
| Target | `forward_returns` |
| SelectKBest output after variance filtering | 61 columns |
| High-correlation columns removed | `D2`, `I9` |
| Selected original indicators | 59 columns |
| Added anomaly features | `is_anomaly`, `anomaly_score` |
| Final input width | 61 columns |
| Original 80/20 sequential split on this copy | 7,216 training / 1,805 validation rows |
| Example test CSV | 10 rows, 99 columns |

The ordered feature list is in [RECOMPUTED_FEATURES.txt](../data/RECOMPUTED_FEATURES.txt). The source CSV bytes were not reformatted or cleaned before inclusion.

## Execution and boundaries

The recomputation used the original code's iterative imputation, variance threshold, target-aware selection, correlation filtering, Isolation Forest and conditional winsorization. It used seed 42 and Python 3.12.14, NumPy 2.5.4, pandas 2.3.3 and scikit-learn 1.9.1.

IterativeImputer reached the original limit of ten iterations without meeting its convergence criterion; that warning is retained in the provenance record. Preprocessing completed and produced the feature list.

This preprocessing run did not train the Ridge/LightGBM/XGBoost prediction stack or run the Kaggle gateway. It did not reproduce a leaderboard score. The original ordering fits preprocessing before the temporal split, so the concerns in [KNOWN_LIMITATIONS.md](KNOWN_LIMITATIONS.md) still apply.

The exact historical input hashes, Kaggle input-version record, historical final features and original model environment remain unavailable. This record documents a new computation on a known public snapshot.

## Subsequent full local notebook check

After the preprocessing audit, the working notebook was also executed on the included CSVs using `python scripts/run_notebook.py --train data/train.csv --test data/test.csv`. The three base prediction models and Ridge meta-learner trained successfully with 61 input columns. Inference produced ten rows with unique IDs and finite weights in [0, 2]. Generated artifacts remain excluded from Git. This separate local run does not reproduce the historical Kaggle result or validate the historical evaluation design. See `data/PROVENANCE.json` and `docs/VALIDATION.md`.
