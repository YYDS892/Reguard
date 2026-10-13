"""Black-box failure gates for the portable CI entry point."""

import os
from pathlib import Path
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def invoke(directory: Path):
    return subprocess.run(
        [sys.executable, str(directory / "run_regression.py")],
        env=dict(os.environ, PYTHONUTF8="1"),
        capture_output=True, text=True, encoding="utf-8", timeout=60,
    )


def test_ci_rejects_unreviewed_dependency_selection(tmp_path):
    shutil.copyfile(ROOT / "ci/packaging-788/run_regression.py", tmp_path / "run_regression.py")
    (tmp_path / "source-version.txt").write_text("99.0\n", encoding="utf-8")
    result = invoke(tmp_path)
    assert result.returncode == 2
    assert "Only reviewed" in result.stdout


def test_ci_rejects_modified_frozen_test_before_execution(tmp_path):
    source = ROOT / "ci/packaging-788"
    shutil.copytree(source, tmp_path / "ci")
    (tmp_path / "ci/test_agent_candidate.py").write_text("def test_always_pass(): pass\n")
    result = invoke(tmp_path / "ci")
    assert result.returncode == 2
    assert "SHA-256 mismatch: test_agent_candidate.py" in result.stdout
