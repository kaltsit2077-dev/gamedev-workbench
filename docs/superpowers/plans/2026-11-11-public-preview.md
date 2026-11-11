# Public preview implementation plan

**Goal:** Publish an honest, reproducible GameDev Workbench preview in a new public repository, with practical architecture report improvements.

**Architecture:** Keep the installable skill self-contained. Add a report module that consumes existing analysis JSON rather than executing game code. Release packaging selects supported source areas, rejects local data, and verifies both archive forms independently of the checkout folder name.

**Tech Stack:** Python 3.11+ standard library, native Godot sample, Git and GitHub Actions.

**Spec:** Existing DESIGN.md and the user's authorization to improve and create a public GitHub repository. Continue natively in this session; no additional agent evaluation is necessary for this narrow increment.

## Global constraints

- Public material is original toolkit code, guidance, task fixtures and sanitized evidence; private game source and analysis remain outside this repository.
- Preserve preview status, actual evaluation limitations and per-engine support boundaries.
- No automatic editor MCP, cloud asset upload or unrelated installation.
- Existing Godot behavior evidence remains a dated sample snapshot; report/tool changes do not claim new engine behavior.

## Review focus

- Reports are untrusted input: escape Markdown control syntax and bound emitted tables; do not turn names into executable Mermaid/HTML.
- Scan limits or different scope cannot be presented as a definitive architecture regression.
- A renamed checkout must still produce the documented portable archive layout.
- Ignored profiles, secrets, caches, symlinks and arbitrary local root files must not enter packages.
- Remote publication must use the connected account and a new empty repository; no overwrite of an existing project.

## Task 1: Readable report and snapshot comparison

Files: scripts/analysis_reports.py inside the skill, scripts/workbench.py CLI, tests/test_analysis_reports.py, sample public reports and documentation.

Interfaces: render_analysis(report, max_rows=40) -> str; compare_analysis(before, after) -> dict. CLI report-analysis INPUT --output NEW.md and compare-analysis BEFORE AFTER --output NEW.json. Source reports stay unchanged; output refuses overwrite and refuses replacing inputs.

- [ ] Test changed hashes, stable reference matching across shifted lines, added missing dependencies and cycles, incomplete/mismatched scope, and hostile Markdown names.
- [ ] Implement bounded Markdown rendering and conservative structural comparison with explicit uncertainty.
- [ ] Run tests and demonstrate on original sample snapshots; make the helpers available through the skill.

## Task 2: Portable release and community entry points

Files: tools/package.py, tools/release_audit.py, tests/test_packaging.py, .github/workflows/ci.yml, issue templates, capability matrix and roadmap.

Interfaces: package.release_files(root) -> list[Path]; package.build(output_dir) -> archive hash mapping. audit(root) -> list[str] for actual release-selected files. Both installable and full packages keep fixed root gamedev-workbench/.

- [ ] Test renamed source roots, ignored local files, rejected symlinks and release path/credential detection.
- [ ] Implement deterministic ZIP metadata and an explicit release source boundary; add --output-dir.
- [ ] Add Python 3.11/3.14 Windows/Linux/macOS CI, portable package validation, precise capability/roadmap docs and useful issue forms.
- [ ] Run local tests, skill validation, release audit and archive extraction checks before any public mutation.

## Task 3: Public publication

- [ ] Confirm authenticated account, then initialize an independent toolkit Git repository with a conventional initial commit and no private history.
- [ ] Verify repository name availability; create public gamedev-workbench under the authenticated account if absent; fail instead of modifying an existing remote.
- [ ] Push main, observe CI, fix actual failures, then tag and publish preview assets with hashes and release notes.
- [ ] Update the existing installed toolkit only if it still matches the previous verified package; retain that archive for rollback.
- [ ] Verify remote public visibility, commit, release assets and final local status, then return usable links.
