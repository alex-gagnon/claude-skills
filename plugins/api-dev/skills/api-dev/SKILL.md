---
name: api-dev
version: 1.0.0
description: Kick off API development work — TDD, feature implementation, code review, or refactoring. Asks a few focused questions then hands off to the api-dev agent.
tags: [api, backend, testing, quality]
---

Ask the user the following questions, then proceed with the agent workflow described in `../../agents/api-dev/AGENT.md`.

## Questions to Ask

1. **What kind of task is this?**
   - TDD (write tests first, then implement)
   - Implement (feature already specced, skip straight to code)
   - Code review (review a diff or file)
   - Refactor (change structure, not behavior)

2. **What's the scope?** One sentence is enough — e.g. "add Bearer token auth to all `/api/v1/*` routes" or "review the pagination implementation in `routes/items.py`".

3. **Any constraints or context to know upfront?** (optional) — e.g. existing patterns to follow, things to avoid, a related file or PR to read first.

## After Collecting Answers

Load the relevant reference files from `../../agents/api-dev/references/` and begin the workflow defined in `../../agents/api-dev/AGENT.md` for the task type the user selected.

- TDD → TDD Workflow section
- Implement → Feature implementation, minimal footprint
- Code review → Code Review Workflow section
- Refactor → Refactoring, no behavior changes
