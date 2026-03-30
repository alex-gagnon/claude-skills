# CLAUDE.md — SDET Marketplace

This repository is a marketplace of Claude Code plugins — skills, agents, and MCP servers. All plugins are registered in `.claude-plugin/marketplace.json` and each has a `plugin.json` with metadata. Skills live in `skills/<name>/`, agents in `agents/<name>/`, and MCPs in `mcps/<name>/`. For the full catalog, see README.md.

## Plugin Types

| Type | Directory | Entrypoint | Description |
|------|-----------|------------|-------------|
| **Skill** | `skills/<name>/` | `SKILL.md` | Prompt-based capability invoked via slash command. Stateless, single-turn. |
| **Agent** | `agents/<name>/` | `AGENT.md` | Autonomous multi-step workflow that orchestrates tools and sub-tasks. |
| **MCP** | `mcps/<name>/` | `MCP.md` | External tool server exposing callable functions over the Model Context Protocol. |

## Naming Conventions

| Convention | Rule |
|---|---|
| Plugin folder name | lowercase, hyphens only (e.g., `review-pr`) |
| Slash command (skills) | matches folder name exactly |
| `name` in plugin.json and frontmatter | must match folder name exactly |
| Tags | use category tags: `git`, `review`, `quality`, `docs`, `special`, `design`, `testing` |

## Adding a New Plugin

1. **Check for overlap first** — read `.claude-plugin/marketplace.json` and scan existing plugin descriptions. If a plugin with similar purpose exists:
   - Extend the existing plugin if the new behavior is a variant of the same trigger
   - Merge into the existing plugin if both trigger on nearly identical user intent AND the combined entrypoint body stays under ~400 tokens
   - Only create a new plugin if the purpose, trigger, and output are clearly distinct
2. Create the plugin directory (`skills/<name>/`, `agents/<name>/`, or `mcps/<name>/`)
3. Create `plugin.json` with all required fields (see existing plugins for examples)
4. Create the entrypoint file (`SKILL.md`, `AGENT.md`, or `MCP.md`) using existing plugins as templates
5. Create `tests.md` with scenarios, a rubric, and a golden set (see existing `tests.md` files for format)
6. Add the plugin entry to `.claude-plugin/marketplace.json`
7. Update README.md with the new plugin
8. For skills: add promptfoo assertions to `promptfoo.yaml`
9. Commit: `add <plugin-name> <plugin-type>`

**Tip:** Use the **plugin-architect** agent to interactively design and scaffold new plugins.

## Key Conventions for AI Assistants

- Do not create new plugin files unless explicitly requested
- Before creating a plugin, always check `.claude-plugin/marketplace.json` for overlap (see Adding a New Plugin above)
- Prefer editing existing plugins over creating new ones
- When two plugins have nearly identical triggers, merge them rather than maintaining duplicates
- Never rename a plugin folder without updating `.claude-plugin/marketplace.json`, README.md, and all cross-references
- If a plugin's purpose is unclear, read its entrypoint before invoking or editing it

## Git Practices

- Branch format: `claude/<description>-<id>`
- Push: `git push -u origin <branch-name>`
- Never force-push, never skip hooks (`--no-verify`)
- Keep commits atomic: one logical change per commit
