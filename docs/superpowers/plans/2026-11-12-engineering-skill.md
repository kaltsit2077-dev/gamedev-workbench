# Engineering Skill Reliability Implementation Plan

**Goal:** Make the skill useful for small and medium game projects in architecture, integrated implementation, debugging and team Git work; GUI remains optional.

**Architecture:** Keep the self-contained skill and its existing tools. Add focused planning/debugging/collaboration workflows, strengthen integration decisions, and provide bounded read-only Git evidence. Evaluate actual agent behavior separately from tool tests.

**Tech Stack:** Markdown instructions, existing Python 3.11+ standard-library CLI, local Git fixtures; no new UI or model-provider API.

**Spec:** User's 2026-11-12 clarification: practical AI assistance, coherent architecture/workflow, team version management and bug repair, across small/medium scope. Previous continuous execution authorization remains in effect.

## Global constraints

- Preserve project-local rules and authorized workflow; no imposed branching policy or universal framework.
- Do not modify the private game's source, index, branches or root engine cache.
- Git inspection never fetches, stages, merges or resolves conflicts; remote freshness is unknown.
- Instructions stay proportional; do not demand a full design document for a local correction.
- Behavioral trials use isolated original fixtures; model identity/configuration, timings and missing fees are disclosed. Do not infer general productivity from a pilot.

## Review focus

- A tree with no visible text markers can still contain staged conflicts, source/UID inconsistencies or collaborator changes.
- A failed Git object lookup or bounded/truncated scan must not become a clean bill of health.
- An agent may repair the visible symptom but leave alternate entry points, save failure or lifecycle behavior broken.
- A merge may remove text markers while losing one side's feature; acceptance must test both.
- Passing instructions/route validation does not prove a model followed the skill.

## Tasks

- [x] Rewrite SKILL.md routing; add project-planning, bug-fixing, git-collaboration instructions and compact optional templates. Strengthen existing architecture/feature guidance without duplicating project decisions.
- [x] Add review-git: local porcelain/index/base diff, changed-path counterpart hints, conflict markers and explicit partial/freshness states. Test actual temporary repositories, newline/space paths, merge conflicts, staged rename/UID pairs and readonly behavior.
- [x] Freeze a behavioral task and hidden grader before dispatch. Run independent forward passes under the skill-creator evaluation procedure, with equal model/tool context and an unskilled control where feasible. Inspect artifacts, do not tell agents the intended repair.
- [x] Exercise Git inspection on the actual private repository read-only; publish only a sanitized capability summary, no private paths/content.
- [x] Run relevant tests, validate extracted packages and update only an unchanged installed skill. Prepare the preview and gate publication on remote CI, with concrete results and limitations.
