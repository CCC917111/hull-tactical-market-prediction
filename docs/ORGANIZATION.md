# Archive inventory and organization record

Source: `dda3020project.zip`, supplied with the project. It contains three substantive files and three macOS AppleDouble metadata entries. The source archive is preserved locally outside this Git repository; no source file was deleted.

| Original file | Bytes | Repository destination | Treatment |
| --- | ---: | --- | --- |
| `kaggle_submission.ipynb` | 40,990 | `notebooks/original/kaggle_submission.ipynb` | Byte-identical historical copy |
| `public_score.png` | 87,448 | `docs/assets/public_score.png` | Byte-identical evidence image |
| `submission.pdf` | 173,180 | `docs/submission.pdf` | Five student IDs removed from page 1; metadata cleared |
| Three `__MACOSX/._*` entries | 628 total | Outside repository | Finder metadata, not project source |

Original SHA-256 checksums:

```text
44f468c0197fc8071a67c09a188196e9bf5c2f417e87afab38ad9b9fb644573e  kaggle_submission.ipynb
580839d98b26cf486070d3743e5b1f52bc05998c6051299d6f508c0a6d8e9367  public_score.png
87821275b40d624a55df4bad8f374b16370f4025df00d53b3ea01d2d0e476d4b  submission.pdf
```

The working notebook is derived from the original, with these changes:

- Explicit configurable paths replace recursive selection of the first matching Kaggle input. Local defaults work when Jupyter starts from either the repository root or `notebooks/`.
- Automatic unpinned package installation is removed. Direct dependencies and a resolved Python 3.12 environment are recorded.
- XGBoost early stopping is configured in the estimator constructor for the tested API.
- Training saves the imputer, original feature order and training medians; prediction reuses them before feature selection and Isolation Forest inference. An all-empty training feature retains its position in the imputer before variance filtering.
- Missing test features and values are filled from fitted training preprocessing. Infinite test values are treated as missing. Batch medians no longer determine inference imputation.
- Boolean anomaly masks replace positional values used as label-based indexes, fixing inference for non-default DataFrame indexes. Polars batches are supported without adding a PyArrow dependency.
- Pickle loading requires an explicit trusted path, an opt-in and the working model schema. Automatically discovered models are never loaded.
- The Kaggle gateway/server is opt-in outside a competition rerun. The local runner disables the server and pickle loading regardless of ambient settings.
- Generated CSVs use the configured output directory, with checks for finite bounded weights and unique nonmissing IDs. The inference sigmoid clips its exponent to avoid overflow.
- Working-notebook outputs and private metadata are absent. A consistent kernelspec and cell IDs were added. Warnings remain visible.

The base learners, hyperparameter search, preprocessing-before-split research design, in-sample stacking and distinct CSV/server allocation mappings remain recognizable from the original. Their methodological shortcomings are documented in `KNOWN_LIMITATIONS.md`; packaging does not establish an unbiased model.

New supporting files include the README, data/output folder instructions, dependency files, `.gitignore`, `.gitattributes`, local notebook runner, synthetic smoke test, function regression tests and verification record. No license was chosen without the authors' decision. The initial organization commit included no data, fitted model, credential or generated notebook.

The PDF was checked for remaining student ID text and visually reviewed after redaction. Pages 2-8 render pixel-identically to the original. Author attribution and research text remain.

## Later reference-data addition

At the repository owner's request, a fixed public copy of `train.csv` and example `test.csv` was subsequently added with source commits, SHA-256 hashes, field descriptions and a new preprocessing record. These files were not in the original upload and are not asserted to be the exact historical team inputs. Other local datasets and generated outputs remain excluded. See `data/README.md` and `docs/DATA_RECOMPUTATION.md`.
