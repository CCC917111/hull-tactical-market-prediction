# Input data and source

This directory includes a fixed public competition-format copy obtained on **12 October 2026**. The original course-project ZIP contained no CSVs. These files were added later as reference inputs; they have not been confirmed as the team's exact historical files.

## Source and version

- Original dataset: [Hull Tactical - Market Prediction on Kaggle](https://www.kaggle.com/competitions/hull-tactical-market-prediction/data).
- Copy source: [warun7/HullTacticalMarketPrediction](https://github.com/warun7/HullTacticalMarketPrediction/tree/dec25acbb7172b0b74efc1adf8a7c0425c36cfc7).
- Source repository commit: `dec25acbb7172b0b74efc1adf8a7c0425c36cfc7`.
- Training file's last source change: [commit 0f113e2](https://github.com/warun7/HullTacticalMarketPrediction/commit/0f113e217e6d293eda30d3fbc84441ef4ecea0b3), **26 November 2025**.
- File bytes and Git blob hashes were checked against the source repository. [PROVENANCE.json](PROVENANCE.json) records SHA-256 hashes, source URLs, complete column names and recomputation metadata.

| File | Rows, excluding header | Columns | `date_id` range | Purpose |
| --- | ---: | ---: | --- | --- |
| [train.csv](train.csv) | 9,021 | 98 | 0-9020 | Historical labeled input |
| [test.csv](test.csv) | 10 | 99 | 8980-8989 | Example inference input |

The included `test.csv` is a small example, not the complete leaderboard evaluation set or hidden test set. The actual competition evaluation uses its provided API.

## Rows and fields

Each row represents a trading day identified by `date_id`. The training file has **94 financial indicators**, one date identifier and three training-only return/rate fields. Individual indicator names are anonymous; the provider describes broad groups.

| Prefix | Columns in this copy | Description |
| --- | ---: | --- |
| `D` | 9 | Dummy/binary signals |
| `E` | 20 | Macroeconomic features |
| `I` | 9 | Interest-rate features |
| `M` | 18 | Market dynamics and technical features |
| `P` | 13 | Price and valuation features |
| `S` | 12 | Sentiment features |
| `V` | 13 | Volatility features |

These counts were computed from the included files. This copy has no separately named `MOM` columns, although the official description also lists a momentum group.

- `forward_returns`: the return from buying the S&P 500 and selling it one day later; the notebook's default prediction target.
- `risk_free_rate`: the federal funds rate, according to the official dataset description.
- `market_forward_excess_returns`: forward returns adjusted relative to a rolling expectation and winsorized, as defined by the competition.
- The test input uses the same indicators plus `is_scored` and one-day-lagged versions of the return/rate fields.

Descriptions are based on the [official data page](https://www.kaggle.com/competitions/hull-tactical-market-prediction/data). An available field is not automatically a valid predictor; see the feature-timing concerns in [KNOWN_LIMITATIONS.md](../docs/KNOWN_LIMITATIONS.md).

## Local use and new preprocessing results

After preparing the Python environment, run from the repository root:

```bash
python scripts/run_notebook.py --train data/train.csv --test data/test.csv
```

Rows are already in increasing `date_id` order. The original code's sequential 80/20 split gives **7,216 training rows and 1,805 validation rows** on this copy. A new preprocessing run selected **59 original indicators** and added `is_anomaly` and `anomaly_score`, producing **61 input columns**. These are recomputed results, not recovered historical records. See [DATA_RECOMPUTATION.md](../docs/DATA_RECOMPUTATION.md) and [RECOMPUTED_FEATURES.txt](RECOMPUTED_FEATURES.txt).

The default target is `forward_returns`. Other recognized targets are `market_forward_excess_returns`, `target` and `lagged_forward_returns`; choose one explicitly with `HULL_TARGET_COLUMN` if needed. Features must be numeric and rows chronological.

Only these two reference CSVs, their metadata and this feature list are tracked. Point `--train` and `--test` at other authorized local files for another snapshot. Credentials, personal records, fitted models and generated outputs remain excluded.

## Provider's current download

[Hull Tactical's website](https://hulltactical.com/approach/) supplies a daily-updated CSV. The version inspected on 12 October 2026 had 9,261 rows and 96 columns through 9 October 2026. It uses a date index and `target`, rather than the original Kaggle train/test schema, and is not the snapshot included here.

The dataset remains subject to the provider's [competition terms](https://www.kaggle.com/competitions/hull-tactical-market-prediction/rules). This repository records provenance and does not assign an independent data license.
