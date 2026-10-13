"""Run the frozen Agent regression against the selected, hash-pinned wheel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parent
TEST_SHA256 = "3134cb219d5016f5eff7f968d3893ada2788d1cd0ea8c5c1d75e590c7634367e"
WHEELS = {
    "24.1": "5b8f2217dbdbd2f7f384c41c628544e6d52f2d0f53c6d0c3ea61aa5d1d7ff124",
    "24.2": "09abb1bccd265c01f4a3aa3f7a7db064b36514d2cba19a2f694fe6150451a759",
}


def verify_hash(path: Path, expected: str) -> None:
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError(f"SHA-256 mismatch: {path.name}")


def run(version: str) -> dict:
    if version not in WHEELS:
        raise ValueError("Only reviewed packaging 24.1 and 24.2 are supported")
    wheel = ROOT / "wheels" / f"packaging-{version}-py3-none-any.whl"
    test = ROOT / "test_agent_candidate.py"
    verify_hash(wheel, WHEELS[version])
    verify_hash(test, TEST_SHA256)
    with tempfile.TemporaryDirectory(prefix="reguard-ci-") as directory:
        work = Path(directory)
        source = work / "source"
        with ZipFile(wheel) as archive:
            # Extract only the package; reject paths outside this isolated source root.
            for entry in archive.infolist():
                if entry.is_dir() or not entry.filename.startswith("packaging/"):
                    continue
                target = source / entry.filename
                target.resolve().relative_to(source.resolve())
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(entry))
        frozen_test = work / test.name
        shutil.copyfile(test, frozen_test)
        config = work / "pytest.ini"
        config.write_text("[pytest]\n", encoding="utf-8")
        env = dict(os.environ)
        env.update(
            PYTHONPATH=str(source),
            PYTHONUTF8="1",
            PYTHONDONTWRITEBYTECODE="1",
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
        )
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", str(frozen_test), "-c", str(config),
             "-q", "-p", "no:cacheprovider"],
            cwd=work, env=env, capture_output=True, text=True, encoding="utf-8",
            stdin=subprocess.DEVNULL, timeout=60, check=False,
        )
    return {
        "fixture_id": "packaging-788",
        "candidate_id": "3134cb219d5016f5",
        "source_version": version,
        "wheel_sha256": WHEELS[version],
        "test_sha256": TEST_SHA256,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", choices=tuple(WHEELS))
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    try:
        version = args.version or (ROOT / "source-version.txt").read_text(encoding="utf-8").strip()
        result = run(version)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        result = {"fixture_id": "packaging-788", "exit_code": 2, "error": str(exc)}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write(
                f"### ReGuard packaging #788\n\n"
                f"Version: `{result.get('source_version', 'invalid')}`; "
                f"exit code: `{result['exit_code']}`.\n\n"
                f"Frozen Agent test: `{TEST_SHA256}`.\n"
            )
    # Preserve pytest failure: a known buggy version must make the CI job red.
    return result["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
