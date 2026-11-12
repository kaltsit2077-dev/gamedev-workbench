# Upstream Review and Dependency Boundaries Implementation Plan

**Goal:** Turn inspected upstream practices into a bounded dependency-direction check and focused improvements to existing game-development workflows.

**Architecture:** Reuse Godot analysis snapshots; a new read-only checker consumes explicit project-selected module/path/allow rules. No source edits, new parser, model service, upstream installation or imposed folder structure. Keep research evidence separate from runtime claims.

**Tech Stack:** Python 3.11+ standard library, existing CLI and analyzer, JSON rules, Markdown instructions.

**Spec:** User authorizes independent GitHub research and continued practical improvement. Preserve project-local contracts, creative/native UI workflows and optional GUI. Existing continuous execution authorization applies; implement and verify in this session.

## Global constraints

- Only public workbench source changes. Private game source/index/branches stay untouched.
- Upstream stars are a dated discovery signal, not proof of effectiveness. Pin the documents actually read, note archival/renames, and retain license and non-adoption decisions. Do not bundle upstream code or instructions wholesale.
- Checker evaluates explicit observed resource dependencies in a saved Godot snapshot, not runtime calls, state writers, source freshness or the whole architecture. Unknowns never become a clean pass.
- Rule schema_version=1: modules with unique id, paths (exact file or directory ending /), allow (other module IDs). Self references allowed. Case-sensitive literal matching, no globs, absolute paths, parent traversal, ambiguous overlaps or unknown IDs. At most 64 modules / 512 selectors.
- Snapshot lists capped at 30000 files / 100000 references / 100000 uncertainty entries. Existing snapshot reader caps JSON at 20 MB; rule reader at 2 MB.
- Existing outputs are not overwritten. No network or engine execution in the checker.

## Review focus

- Literal path strings cannot prove dependencies; report review-needed rather than false violation.
- Dynamic/unknown UID, missing references, unowned paths or truncated scans must remain partial even when no forbidden edge is found.
- Badly specified or overlapping rules must fail validation rather than guess ownership.
- An explicit forbidden edge remains a finding when other parts of coverage are incomplete.
- A historical snapshot passing its declared scope does not establish that the current tree or runtime conforms.

## Tasks

- [x] Add dependency_boundaries.py, check-boundaries CLI and portable example rules. Return no-observed-violations / violations / partial plus coverage, concrete edges, unknowns and input fingerprints; CLI 0 only for observed conformance, 2 otherwise.
- [x] Test real analyzer output for allowed and forbidden edges, self references, weak strings/dynamic/unknown UID, missing files, malformed paths/rules and refused output aliases. Verify read-only behavior.
- [x] Record pinned upstream review metadata and concise adoption/defer decisions. Update workflows on independent slices, known-good comparisons, save/transient separation, cancellation and evidence scope; keep original wording and project-specific judgment.
- [x] Prepare checked tooling and the unchanged installed-skill update; validate release archives and gate publication on remote CI. Keep direct tool evidence separate from previous model trials; no new productivity claim.
