# packaging #788 CI proof

This directory reuses ReGuard's verified Agent candidate `3134cb219d5016f5`
without changing its bytes. Its three tests cover prerelease boundaries and a
negative control. The original Agent run proved buggy 24.1 fails 3/3 times and
fixed 24.2 passes 3/3 times; the CI job runs the frozen test once per commit.

`source-version.txt` selects the reviewed wheel: `24.2` passes and `24.1` fails.
Changing that tracked file triggers the workflow, demonstrating that a real
dependency regression makes the check fail. The runner verifies the wheel and
test hashes, uses an isolated temporary package tree, and preserves pytest's
exit code. It does not convert the expected buggy failure into CI success.

Run from the repository root with Python 3.13.5:

```sh
python -m pip install -r ci/packaging-788/requirements.txt
python ci/packaging-788/run_regression.py
python ci/packaging-788/run_regression.py --version 24.1
```

The second run should exit 1 with two failed tests and one passed control.
Restore `source-version.txt` to `24.2` after a deliberate regression demo.

This is one reviewed public fixture integrated into CI. It does not yet
install generated tests into arbitrary repositories or protect unrelated code.
The workflow needs no model credentials or Docker. GitHub Actions and its pip
installation need network access; the two upstream wheels are included locally.

Upstream: [Issue #788](https://github.com/pypa/packaging/issues/788),
[fix PR #794](https://github.com/pypa/packaging/pull/794).
The wheels retain their upstream Apache-2.0 OR BSD-2-Clause license files.
`provenance.json` records the verified candidate and wheel hashes.

Workflow references: [checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python),
[GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
