#!/usr/bin/env python3
"""Validate notebook syntax and inspect only publishable repository files."""
import ast
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess

import nbformat

ROOT = Path(__file__).resolve().parents[1]
REFERENCE_CSVS = {"data/train.csv", "data/test.csv"}
PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{40,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{32,}"),
    re.compile(r"(?i)(?:api_key|access_token|password|client_secret)\s*[=:]\s*['\"][^'\"]{8,}['\"]"),
)


def main():
    nb = nbformat.read(ROOT / "notebooks/kaggle_submission.ipynb", as_version=4)
    nbformat.validate(nb)
    code_count = 0
    for index, cell in enumerate(nb.cells):
        if cell.cell_type == "code":
            ast.parse(cell.source, filename=f"working notebook cell {index}")
            assert cell.execution_count is None and not cell.outputs, "Saved outputs present"
            code_count += 1
    for script in list((ROOT / "scripts").glob("*.py")) + list((ROOT / "tests").glob("*.py")):
        ast.parse(script.read_text(), filename=str(script.relative_to(ROOT)))
    # Inspect versioned files and untracked files that Git would include.
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, check=True, capture_output=True)
    names = sorted(set(result.stdout.decode().split("\0")) - {""})
    problems = []
    provenance = json.loads((ROOT / "data/PROVENANCE.json").read_text())
    for name in sorted(REFERENCE_CSVS):
        path = ROOT / name
        if not path.is_file():
            problems.append(f"Missing reference CSV: {name}")
            continue
        record = provenance["files"][path.name]
        if (path.stat().st_size != record["size_bytes"]
                or hashlib.sha256(path.read_bytes()).hexdigest() != record["sha256"]):
            problems.append(f"Reference CSV does not match its source metadata: {name}")
            continue
        with path.open(newline="") as stream:
            reader = csv.reader(stream)
            columns = next(reader)
            if columns != record["column_names"] or len(columns) != record["columns"]:
                problems.append(f"Reference CSV columns differ from source metadata: {name}")
            date_column = columns.index("date_id")
            target_column = columns.index("forward_returns") if path.name == "train.csv" else None
            row_count, previous_date = 0, None
            for row in reader:
                row_count += 1
                if len(row) != len(columns):
                    problems.append(f"Invalid reference CSV row width: {name}, row {row_count}")
                    break
                date_id = int(row[date_column])
                if previous_date is not None and date_id <= previous_date:
                    problems.append(f"Reference dates are not strictly increasing: {name}")
                    break
                previous_date = date_id
                if target_column is not None and not math.isfinite(float(row[target_column])):
                    problems.append(f"Non-finite target: {name}, row {row_count}")
                    break
            if row_count != record["rows"]:
                problems.append(f"Reference CSV row count differs from metadata: {name}")
    expected_features = provenance["recalculation"]["final_feature_names"]
    actual_features = (ROOT / "data/RECOMPUTED_FEATURES.txt").read_text().splitlines()
    if (actual_features != expected_features or len(set(actual_features)) != len(actual_features)
            or len(actual_features) != provenance["recalculation"]["final_feature_count_including_anomaly_features"]):
        problems.append("Recomputed feature list differs from provenance metadata")
    for name in names:
        path = ROOT / name
        if path.is_symlink():
            problems.append(f"Symlink: {name}")
            continue
        if path.stat().st_size > 10 * 1024 * 1024 and name not in REFERENCE_CSVS:
            problems.append(f"File exceeds 10 MiB: {name}")
        if (name.startswith(("__MACOSX/", ".venv/")) or path.name.startswith("._")
                or (path.suffix == ".csv" and name not in REFERENCE_CSVS)
                or path.suffix in {".pkl", ".pickle", ".pem", ".key"}
                or path.name.startswith(".env")):
            problems.append(f"Private/generated artifact: {name}")
        if path.suffix in {".py", ".md", ".ipynb", ".txt", ".in", ".json", ".yml", ".yaml"}:
            text = path.read_text()
            if any(pattern.search(text) for pattern in PATTERNS):
                # Report paths only; never echo a possible secret.
                problems.append(f"Possible credential pattern: {name}")
    if problems:
        raise SystemExit("\n".join(problems))
    print(f"PASS: {code_count} notebook code cells parse; {len(names)} publishable files checked.")
    print("Reference CSV hashes, dimensions, date order, target and feature list verified.")
    print("No saved working-notebook outputs, common credential patterns or unexpected artifacts found.")


if __name__ == "__main__":
    main()
