#!/usr/bin/env python3
"""Run the working notebook using explicitly selected local input files."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def execute_notebook(train: Path, test: Path, output_dir: Path,
                     kernel: str = "hull-tactical", timeout: int = 1800):
    train, test, output_dir = train.resolve(), test.resolve(), output_dir.resolve()
    for label, path in (("training", train), ("test", test)):
        if not path.is_file():
            raise FileNotFoundError(f"Missing {label} CSV: {path}. See README.md.")
    output_dir.mkdir(parents=True, exist_ok=True)
    notebook = nbformat.read(ROOT / "notebooks/kaggle_submission.ipynb", as_version=4)
    overrides = {
        "HULL_TRAIN_PATH": str(train), "HULL_TEST_PATH": str(test),
        "HULL_OUTPUT_DIR": str(output_dir), "HULL_RUN_KAGGLE_SERVER": "0",
        # A local batch run never loads a pickle or starts a competition server.
        "HULL_MODEL_PATH": "", "HULL_ALLOW_PICKLE": "0",
        "KAGGLE_IS_COMPETITION_RERUN": "",
    }
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        os.environ.update(overrides)
        NotebookClient(notebook, timeout=timeout, kernel_name=kernel,
                       resources={"metadata": {"path": str(ROOT)}}).execute()
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
    executed = output_dir / "kaggle_submission.executed.ipynb"
    nbformat.write(notebook, executed)
    return output_dir / "submission.csv", executed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--train", type=Path, default=ROOT / "data/train.csv")
    parser.add_argument("--test", type=Path, default=ROOT / "data/test.csv")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts")
    parser.add_argument("--kernel", default="hull-tactical")
    parser.add_argument("--timeout", type=int, default=1800, help="Per-cell timeout in seconds")
    args = parser.parse_args()
    try:
        csv, notebook = execute_notebook(args.train, args.test, args.output_dir,
                                         args.kernel, args.timeout)
    except FileNotFoundError as exc:
        parser.exit(2, f"{exc}\n")
    print(f"CSV: {csv}\nExecuted notebook: {notebook}")


if __name__ == "__main__":
    main()
