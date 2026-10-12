# Hull Tactical Market Prediction

DDA3020 course project exploring a stacking ensemble for the Kaggle **Hull Tactical - Market Prediction** competition. The supplied implementation trains Ridge, LightGBM, and XGBoost regressors, combines their predictions with a Ridge meta-learner, and maps predicted returns to exposure in `[0, 2]`.

This repository packages the original submission with a portable working notebook, a tested Python environment, and reproduction notes. **Competition data and trained models were not included in the source archive.** The historical screenshot shows a public score of **0.461**; this result has not been independently reproduced.

![Historical Kaggle score](docs/assets/public_score.png)

## My contribution

In this team course project, I was responsible for the XGBoost and LightGBM modeling components.

## Input data

The repository includes a fixed public copy of the Kaggle competition's `train.csv` and example `test.csv`, sourced from [warun7/HullTacticalMarketPrediction](https://github.com/warun7/HullTacticalMarketPrediction/tree/dec25acbb7172b0b74efc1adf8a7c0425c36cfc7). The training file was committed there on 26 November 2025. It contains **9,021 rows and 98 columns**; the example test file contains **10 rows and 99 columns**.

Each row represents a trading day, with 94 financial indicators covering market dynamics, macroeconomics, interest rates, valuation, sentiment, volatility and binary signals. The notebook's default target is `forward_returns`, the next-day S&P 500 return. This reference copy was obtained during repository preparation and has not been confirmed as the team's exact historical input. See [data provenance and field descriptions](data/README.md) and [the new preprocessing record](docs/DATA_RECOMPUTATION.md).

## Repository layout

```text
notebooks/
  kaggle_submission.ipynb           Working notebook: local paths and runtime fixes
  original/kaggle_submission.ipynb  Unmodified historical notebook
scripts/
  run_notebook.py                   Execute the working notebook on your own CSVs
  smoke_test.py                     End-to-end check using temporary synthetic data
  validate_repository.py            Notebook syntax and repository hygiene checks
tests/test_notebook_functions.py    Missing-data, feature-alignment and weight checks
docs/
  submission.pdf                   Original report with student IDs redacted
  assets/public_score.png           Unmodified historical score screenshot
  REPRODUCIBILITY.md                Execution, Kaggle and environment details
  KNOWN_LIMITATIONS.md              Modeling and validation caveats
  ORGANIZATION.md                   Archive inventory and change record
  VALIDATION.md                    Recorded verification and its boundaries
  DATA_RECOMPUTATION.md            Reference-snapshot preprocessing results
data/
  train.csv                        Fixed public reference copy (9,021 rows)
  test.csv                         Example inference input (10 rows)
  README.md                        Source, fields and usage
  PROVENANCE.json                  Source commits, hashes and file metadata
  RECOMPUTED_FEATURES.txt           61 columns from the new preprocessing run
artifacts/                         Generated CSVs and executed notebooks (ignored)
requirements.in                    Direct dependency ranges
requirements.txt                   Resolved dependencies tested with Python 3.12
```

## Local setup

Use **Python 3.12**. From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m ipykernel install --prefix .venv --name hull-tactical --display-name "Hull Tactical (Python 3.12)"
```

On Windows, activate with `.venv\Scripts\activate` and use the installed Python 3.12 executable. On macOS, a LightGBM or XGBoost import error mentioning `libomp` requires installing OpenMP with `brew install libomp`; see [reproduction notes](docs/REPRODUCIBILITY.md). Verification used macOS arm64; other platforms have not been tested.

### Check the installation without competition data

```bash
python scripts/validate_repository.py
python -m unittest discover -s tests -v
python scripts/smoke_test.py
```

The smoke test trains all three base models and the meta-learner on synthetic data, runs inference, and checks the generated CSV. It verifies execution only and does not measure competition performance.

### Run the included reference data

The reference CSVs are already present at `data/train.csv` and `data/test.csv`; no data download or API key is needed for this local run. Training rows are in chronological `date_id` order.

```bash
python scripts/run_notebook.py --train data/train.csv --test data/test.csv
```

Outputs are `artifacts/submission.csv` and `artifacts/kaggle_submission.executed.ipynb`. You can instead open `notebooks/kaggle_submission.ipynb` in JupyterLab using the environment above. The first configuration cell accepts paths through environment variables; see [REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md).

For another authorized snapshot from the [competition data page](https://www.kaggle.com/competitions/hull-tactical-market-prediction/data), pass its CSV paths with `--train` and `--test`. Only the two documented reference CSVs are tracked; other local datasets and generated outputs remain ignored.

## Method and evidence

The notebook implements iterative missing-value imputation, variance and correlation filtering, target-aware feature selection, Isolation Forest anomaly indicators, conditional winsorization, an 80/20 sequential split, and a Ridge + LightGBM + XGBoost stack. A separate sigmoid mapping is used by the optional Kaggle inference callback.

The [course report](docs/submission.pdf) discusses additional standalone LightGBM and Random Forest experiments. Their training scripts, raw results, original environment, and data were absent from the archive. The uploaded notebook has no saved execution outputs.

**The working notebook retains the historical research design. Its preprocessing and feature selection happen before the split, its meta-learner uses in-sample base predictions, and target-derived fields may be used as features.** An 80/20 sequential split therefore does not establish leakage-free validation. Read [KNOWN_LIMITATIONS.md](docs/KNOWN_LIMITATIONS.md) before interpreting any metric. This is a course project, not a validated trading system.

For Kaggle, the competition-provided evaluation API is required; the local CSV is a debugging artifact rather than a verified competition submission. Enable the inference server only in the Kaggle environment as described in the reproduction notes.

## Credits and usage

Project authors credited in the report: Luo TianCheng, Wan Qianhua, Hng Cherng Khai, Chan Kee Qing, and Chen Yike. The repository report removes their student identifiers while preserving the research content. No software license was supplied, so none has been assigned on the authors' behalf. The included data copy retains its source attribution and is subject to the original provider's [data terms](https://www.kaggle.com/competitions/hull-tactical-market-prediction/rules); this repository does not grant a separate data license.
