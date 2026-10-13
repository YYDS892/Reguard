# ReGuard CI integration

This repository contains the first CI integration of a regression test generated and independently verified by ReGuard. It currently covers the reviewed public packaging #788 defect.

The selected dependency version is tracked in `ci/packaging-788/source-version.txt`. Version 24.2 passes; reverting to 24.1 makes the GitHub Actions check fail. The frozen test retains SHA-256 `3134cb219d5016f5eff7f968d3893ada2788d1cd0ea8c5c1d75e590c7634367e`.

See [the CI fixture guide](ci/packaging-788/README.md) for local commands, upstream provenance, limitations, and the deliberate regression demonstration.

The complete local ReGuard project has four reviewed AgentTeams loops. This repository currently publishes only the minimal portable CI integration, not that full runtime.
