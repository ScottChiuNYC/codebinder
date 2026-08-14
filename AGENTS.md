# AI Agent Guide

Before changing CodeBinder, read `README.md` and `docs/architecture.md`, then inspect the focused implementation and tests for the behavior being changed.

## Feature completeness

A user-visible or developer-facing feature is not complete unless the same pull request also updates the documentation that explains the new behavior. Documentation may live in `README.md`, `docs/architecture.md`, or a focused document under `docs/`, depending on scope. Do not leave a new behavior discoverable only from source code or tests.

Behavioral changes also require focused tests. When discovery, conversion, RST generation, or the Sphinx extension changes, run the repository test suite and preserve the maintenance contract in `docs/architecture.md`.

Keep changes narrow and reviewable. Do not change generated consumer artifacts in this repository to compensate for undocumented behavior; update the CodeBinder contract and its tests instead.
