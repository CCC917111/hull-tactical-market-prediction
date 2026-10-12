# Private input data

The archive contains no data. Obtain authorized `train.csv` and `test.csv` from the [Hull Tactical competition](https://www.kaggle.com/competitions/hull-tactical-market-prediction/data), then place them here. Keep training rows in chronological order; the notebook splits by position, not by sorting dates.

The default target is `forward_returns`. The notebook also recognizes `market_forward_excess_returns`, `target`, and `lagged_forward_returns` in that order if the default is absent. Explicitly select a target with `HULL_TARGET_COLUMN` if needed. Input features must be numeric, with at least one nonconstant feature and enough rows for a nonempty 80/20 split. See the documented leakage concerns before using target-derived columns.

CSV files and other datasets are ignored. Do not commit competition data, credentials, or personal records.
