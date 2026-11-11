# Platform Foundation Implementation Plan

> Execution: user explicitly requested sequential autonomous implementation and verification. Continue natively in this session; do not stop for another approval of this plan.

**Goal:** Connect reliable analysis, editable creative deliverables, declared engine execution and evidence-based evaluation as a reusable local platform core.

**Architecture:** Preserve the self-contained skill layout. Add focused Python modules for creative workspaces, adapter capabilities and explicit test execution. Keep reports versioned and separate recorded evidence from unverified quality. External source labels are frozen before results are observed.

**Tech Stack:** Python 3.11+ standard library, existing native engine cases, Markdown/JSON, existing offline gallery.

**Spec:** ../specs/2026-11-11-platform-foundation-design.md

## Global constraints

- Python 3.11+ standard library; no new accounts, remote model calls or implicit installs.
- No private game writes or public redistribution of private sources/reports.
- Exclusive output creation; bounded JSON and files; paths contained in their chosen root and no symlinks.
- Missing editors/fees/model trials remain blocked/unavailable; no synthetic productivity claims.

## Review focus

- A modified external source/label must invalidate the frozen evaluation, not silently change its score.
- Creative output references and task dependencies must reject traversal, cycles and missing targets.
- A command exiting zero with absent/empty/contradictory checks must not pass.
- A timeout or unavailable editor must preserve a useful failure/blocked record.
- Tool-only defect detection must not be reported as same-model quality, rework or cost improvement.

## Tasks

### 1. External analysis evaluation

Files: evals/analysis-external/{sources,labels.json,manifest.json,LICENSE}; tools/evaluate_external_analysis.py; tests/test_external_analysis.py.

Interface: evaluate(root=fixture_root) -> JSON with per-file TP/FP/FN, initial evidence and dynamic counts; does not run engine or update labels.

- [x] Freeze pinned official-demo source bytes and independently read labels, record provenance/license/hash.
- [x] Implement frozen-file verification and label scoring over explicit call/extends edges.
- [x] Verify mutation rejection and execute initial evaluation before deciding on parser changes; retain misses and limitations.

### 2. Editable creative workspace

Files: scripts/creative_workspace.py; assets/design/brief.json; tests/test_creative_workspace.py; CLI and recipes.

Interfaces: create_workspace(brief, output) -> manifest; check_workspace(directory) -> bounded check report.

- [x] Test requirement linkage, editable outputs, refused overwrite, malformed brief, path escape, task cycles and a missing artifact.
- [x] Implement a dependency-linked original design pack using explicit brief fields; preserve draft status and existing finite checkers.
- [x] Run a sample through creation/checks and deliberately break one dependency to verify failure.

### 3. Shared capabilities and declared execution

Files: scripts/engine_adapters.py, scripts/project_runner.py; assets/project-tests.json; tests/test_project_runner.py; CLI/recipes.

Interfaces: capabilities() -> versioned manifest; plan_project(project, config) -> argv preview; run_project(project, config, output) -> versioned report. Execution requires CLI --execute; no shell.

- [x] Test fail-closed reports, changed input hash, timeout, argv spaces, missing editor and output boundary.
- [x] Implement explicit typed command records, declared effects, engine constraints and original-report envelopes.
- [x] Actually run the official Godot fixture in a disposable copy and archive sanitized common report; record Unity/Unreal blocked without simulation success.

### 4. Value experiments and delivery

Files: evals/tool-value/{protocol.json,cases.json}; tools/evaluate_tool_value.py; docs/{PLATFORM.md,VALUE-EXPERIMENTS.md}; README, release notes and VERSION.

- [x] Freeze architecture/menu/effect defect tasks; replay intact vs seeded-defect copies with common acceptance, recording bounded tool timing and explicit non-model scope.
- [x] Keep new same-model/human/billing slots pending; review whether each actual diagnostic helps locate the defect.
- [x] Document long-term platform layers/maturity gates, current commands and remaining evidence gaps.
- [x] Run focused/full checks and package/extraction; update unchanged installed skill. Publication is gated on successful remote CI; resulting state belongs to Actions/Releases.


## Execution notes

The user requested uninterrupted native execution. Added a thin offline task/artifact view and selected-task export as a concrete platform-facing slice; browser switching, file selection, download hash and 390px layout were checked. No standalone model backend was added. Human blind review, new model arms and actual billing stay pending, explicitly recorded rather than marked as achieved. Native engine process/output restrictions required a dedicated ignored scratch copy; private game source/root cache remained unchanged.
