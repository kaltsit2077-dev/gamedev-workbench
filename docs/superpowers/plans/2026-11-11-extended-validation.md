# Extended validation implementation plan

**Goal:** Deliver a deeper, executable 0.5 preview across the five user-selected workstreams, retaining evidence gaps when hardware, licensed editors or billing records are unavailable.

**Architecture:** Extend the self-contained skill with conservative source resolution and small domain tools. Keep the new native Godot menu/VFX fixture independent of the user's game. Keep evaluation orchestration in the full project; two fresh A/B pairs use identical frozen task inputs and a prewritten grader.

**Tech Stack:** Python 3.11+ standard library; Godot 4.7.2 official; optional Unity/Unreal editor adapters.

**Spec:** User's five-item continuation request; DESIGN.md; existing CAPABILITIES and ROADMAP. The user has selected keyboard/mouse for manual verification. Continue implementation in this session; independent agents are used only for the explicitly requested paired evaluations.

## Workstreams and acceptance

1. **Native UI/VFX:** original menu with a scrollable long-text settings panel, nested confirmation and focus restoration; shader flash/rings/sparks driven by one effect clock. Test five viewports, large text, repeated open/close, replay/pause/cleanup, and typed synthetic key/mouse/gamepad events. Capture actual frames. Separately collect an operator keyboard/mouse session; do not label injected events as hardware verification.
2. **Analysis precision:** index source UID declarations/sidecars/import descriptors without engine/cache execution; report duplicate/unknown/conflicting UIDs. Resolve a bounded grammar of literal constant concatenations and substitutions; retain runtime/shadowed expressions as unknown. Freeze labeled positive/negative cases and report precision/recall only for that finite set.
3. **Cross-engine cases:** inspect normal installation locations and configured executables. Supply original Unity/Unreal smoke cases plus explicit run plans; execute only if the corresponding editor exists. No large download, license activation or MCP installation by inference.
4. **Domain tools:** finite-boolean narrative reachability/softlock/ending checks, deterministic integer-currency economy simulation, manifest-bounded asset dependency/metadata preflight. Original examples and meaningful invalid-input/negative tests; no implication that a preflight proves engine import or gameplay quality.
5. **Repeated comparisons:** freeze transaction-settings task and common grader before two A/B runs, keep fresh contexts isolated, same inherited model configuration, no overrides. Collect actual wall timers and shared grading; billing remains null unless a traceable provider record exists. Add a ledger summarizer that distinguishes missing/estimated/measured costs.

## Release gate

Run local tests, engine fixtures, actual rendering and release audit. Preserve private reports/manual raw logs outside public source unless sanitized. Update support matrix, package/install the verified preview, push changes, observe cross-platform CI, then publish a matching tag and prerelease under the existing authorization.

## Review focus

- Missing editors or hardware cannot become successful evidence through mocked runners.
- UID ambiguity and name shadowing must degrade resolution instead of guessing.
- Narrative cycles need state-aware termination analysis; reaching a node once does not cover its other flag states.
- Economy conservation, valid domains and bounded output are explicit; license metadata is a declaration, not rights verification.
- Trial graders and task requirements are frozen before agent execution; tool tests and fixture success are not productivity claims.
