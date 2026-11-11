# Evidence showcase implementation plan

**Goal:** Explain what the workbench can do, make first use straightforward, and present measured changes in a clear, truthful README.

**Architecture:** Reuse existing native screenshots unchanged. Generate small repo-native SVG evidence cards from recorded JSON, with a check mode to prevent stale derived figures. Add a self-contained offline HTML gallery over existing quality evidence; no engine invocation, remote assets, tracking or image modification.

**Tech Stack:** Python standard library, SVG, HTML/CSS and small local JavaScript.

**Visual plan:** Reuse the native Deep Signal fixture's navy (#101c28), blue-grey (#192b38), pale text (#e4ecee), teal (#75d6cc), amber (#ffd28b) and red (#ffaaa0). Segoe UI / Microsoft YaHei system type, left-aligned reading and two independent capture panes. Reserve color for comparison and status; no decorative charts or generic metric tiles. The strongest visual is actual engine output. Narrow screens stack panes; visible focus and no ambient animation. Review against brief: evidence navigation and provenance take precedence over a promotional landing page.

**Spec:** User requests current capabilities/use, next priorities, real before/after evidence in a more visual README, and continued execution.

## Tasks and acceptance

1. Gallery: scripts/evidence_gallery.py, CLI gallery EVIDENCE --output NEW.html. Validate report shape, image bounds/path containment, original PNG dimensions and aggregate size; refuse overwrite. Escape untrusted report strings. Browser controls select dimensions, compare two original frames, filter failed checks and download report JSON. No external requests.
2. README evidence: tools/readme_visuals.py emits SVG cards from analysis-labels-v05, quality-v03/v05 and transaction results; --check compares expected output bytes. Clearly distinguish finite regression improvements, expanded fixture coverage and unchanged/negative productivity results.
3. Documentation: Chinese-first concise README with actual images, three starting paths, task/command/output table and prioritized next steps. English summary and detailed quickstart stay linked. Every quantitative claim points to its raw snapshot or reproducible command.
4. Delivery: package an optional standalone gallery of public sample evidence as a release artifact, include its hash, update local skill only when unchanged from the previous package. Validate tools, gallery UI, figures, package extraction and remote CI, then publish 0.6 preview.

## Review focus

- Unknown or unmeasured fees and physical input stay unknown; self-authored fixture counts are not a game quality score.
- Captures and chart values come from real archived outputs, without fabricated frames or invented uplift.
- Gallery source reports/images remain unchanged, including when inputs are malformed or output aliases an input.
- Untrusted filenames/labels cannot escape the evidence root or create executable HTML/links.
- The README is usable on GitHub and at narrow widths; public material contains no private game reports.
