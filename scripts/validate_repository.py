#!/usr/bin/env python3
"""Validate notebook syntax and inspect only publishable repository files."""
import ast
from pathlib import Path
import re
import subprocess

import nbformat

ROOT = Path(__file__).resolve().parents[1]
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
    # Ignore artifacts/data just as Git does. Also works before git add.
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, check=True, capture_output=True)
    names = sorted(set(result.stdout.decode().split("\0")) - {""})
    problems = []
    for name in names:
        path = ROOT / name
        if path.is_symlink():
            problems.append(f"Symlink: {name}")
            continue
        if path.stat().st_size > 10 * 1024 * 1024:
            problems.append(f"File exceeds 10 MiB: {name}")
        if (name.startswith(("__MACOSX/", ".venv/")) or path.name.startswith("._")
                or path.suffix in {".csv", ".pkl", ".pickle", ".pem", ".key"}
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
    print("No saved working-notebook outputs, common credential patterns or large artifacts found.")


if __name__ == "__main__":
    main()
