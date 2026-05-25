---
name: Phase Task
about: Implementation task for a specific phase from gasbot_build_plan.md
title: "[Phase X.Y] <short title>"
labels: ["phase-task"]
assignees: []
---

## Phase reference
- **Phase:** <e.g. 1.2 — Backend Foundation with Security>
- **Build plan section:** <line range or section heading in gasbot_build_plan.md>

## Scope (what to build)
<Bullet list of concrete deliverables. Pulled from the build plan, refined by Claude during planning.>

- [ ] Deliverable 1
- [ ] Deliverable 2

## Out of scope
<Things explicitly NOT part of this task. Prevents Codex from over-building.>

## Acceptance criteria
<How we verify this phase is done. Must be objectively checkable.>

- [ ] All listed deliverables implemented
- [ ] Tests added and passing locally
- [ ] `ruff check .` and `mypy app/` pass (backend) OR `npm run lint` and `npm run type-check` pass (frontend)
- [ ] No new files outside the agreed scope

## Branch
`phase-X.Y-<short-name>`

## Notes from Claude (planning)
<Architectural notes, edge cases, gotchas. Filled in by Claude before Codex starts.>
