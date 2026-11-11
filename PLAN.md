# GameDev Workbench Implementation Plan

> For agentic workers: Execute the following tasks sequentially and review the complete package before release.

**Goal:** Deliver a portable open-source-ready skill and local toolbox for small-team game development.
**Architecture:** One self-contained installable skill holds task workflows, references, catalog, and a standard-library CLI. Project-level entry points delegate to that skill. This packaging keeps individual installations free of broken shared references.
**Tech Stack:** Python 3.11+, Markdown, JSON, optional engine CLIs.
**Spec:** DESIGN.md (approved 2026-11-10).

## Global Constraints

- Do not modify current game source or publish remotely.
- Prioritize architecture, native UI, effects and feature implementation; retain the broader design disciplines.
- Third-party material is indexed, not mirrored. External execution evidence remains distinct from local verification.
- Runtime examples and tool tests must record actual outcomes; no fabricated rendering or player evidence.

## Review Focus

- Offline operation and Unicode search.
- Missing or wrong engine versions cannot become successful verification.
- Source IDs, local references, and packaged skill must remain usable after extraction.
- User-supplied paths and search terms are data, never shell expressions.
- Installation must not overwrite existing skills or run remote installers.

### Task 1: Portable skill and knowledge base

- [x] Create a self-contained skills/gamedev-workbench/SKILL.md and detailed references/workflows for ten task modes.
- [x] Add templates, engine mappings, curated source metadata and independent original examples.
- [x] Verify references and source IDs.

### Task 2: Local toolbox

- [x] Implement scripts/workbench.py: search, inspect, route, doctor, validate, install-plan, install.
- [x] Test Unicode and filters, missing/incorrect engine, schema errors, safe copy and duplicate refusal in temporary directories.
- [x] Use argument arrays for version probes; never execute code from catalog records.

### Task 3: Examples, evaluation and release

- [x] Add isolated Godot architecture, UI and effect examples plus reproducible commands and manual visual checks.
- [x] Run available engine checks; record unavailable or untested dimensions explicitly.
- [x] Validate skill using the provided skill validator, run toolbox tests, inspect extracted archive.
- [x] Add license, contribution and release documents, package ZIP and checksum. No remote publication in this phase.


