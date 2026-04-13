# CLAUDE.md — Personal Marketplace

This repository is a marketplace of Claude Code plugins organized as domain toolkits. All toolkits are registered in `.claude-plugin/marketplace.json`. Each toolkit lives under `plugins/<toolkit-name>/` and has its own `.claude-plugin/plugin.json`. Within a toolkit, capabilities are organized by type: `skills/`, `agents/`, `sdk/`, `mcps/`. For the full catalog, see README.md.

## Structure

```
plugins/<toolkit-name>/
├── .claude-plugin/
│   └── plugin.json          # Toolkit metadata (name, description, author)
├── .mcp.json                # MCP server config (if toolkit includes an MCP)
├── skills/
│   └── <name>/
│       ├── SKILL.md         # Entrypoint
│       ├── plugin.json      # Skill metadata
│       └── tests.md
├── agents/
│   └── <name>/
│       ├── AGENT.md         # Entrypoint
│       ├── plugin.json
│       └── tests.md
├── sdk/                     # Agent SDK implementation (if applicable)
│   └── *.py
└── mcps/
    └── <name>/
        ├── MCP.md
        └── server/
```

## Plugin Types

| Type | Entrypoint | Description |
|------|------------|-------------|
| **Skill** | `SKILL.md` | Prompt-based capability invoked via slash command. Stateless, single-turn. |
| **Agent** | `AGENT.md` | Claude Code agent workflow. Human-in-the-loop, orchestrates tools and sub-tasks. |
| **SDK Agent** | `sdk/*.py` | Autonomous Agent SDK loop. Reads flows/templates from the sibling `agents/` directory. |
| **MCP** | `MCP.md` | External tool server exposing callable functions over the Model Context Protocol. |

## Naming Conventions

| Convention | Rule |
|---|---|
| Toolkit folder name | lowercase, hyphens only (e.g., `code-review-tools`) |
| Skill/agent folder name | lowercase, hyphens only (e.g., `review-pr`) |
| Slash command (skills) | matches skill folder name exactly |
| `name` in plugin.json and frontmatter | must match folder name exactly |
| Tags | use category tags: `git`, `review`, `quality`, `docs`, `special`, `design`, `testing` |

## Adding a New Plugin

1. **Check for overlap first** — read `.claude-plugin/marketplace.json` and scan existing toolkit descriptions. If a toolkit with similar purpose exists, add to it rather than creating a new one.
2. Choose the right toolkit (or create one if clearly distinct)
3. Create the capability directory under the appropriate type subfolder
4. Create `plugin.json` with all required fields (see existing plugins for examples)
5. Create the entrypoint file (`SKILL.md`, `AGENT.md`, or `MCP.md`) using existing plugins as templates
6. Create `tests.md` with scenarios, a rubric, and a golden set
7. Update the toolkit's `.claude-plugin/plugin.json` description if needed
8. Update `.claude-plugin/marketplace.json` if a new toolkit was created
9. Update README.md
10. Commit: `add <toolkit>/<capability> <type>`

**Tip:** Use the **plugin-architect** agent in `plugin-tools` to interactively design and scaffold new plugins.

## Key Conventions for AI Assistants

- Do not create new plugin files unless explicitly requested
- Before creating a plugin, always check `.claude-plugin/marketplace.json` for overlap
- Prefer adding to an existing toolkit over creating a new one
- When two plugins have nearly identical triggers, merge them rather than maintaining duplicates
- Never rename a toolkit or plugin folder without updating `.claude-plugin/marketplace.json`, README.md, and all cross-references
- If a plugin's purpose is unclear, read its entrypoint before invoking or editing it
- The `scripts/` directory contains internal tooling (not user-facing plugins)

## Git Practices

- Branch format: `claude/<description>-<id>`
- Push: `git push -u origin <branch-name>`
- Never force-push, never skip hooks (`--no-verify`)
- Keep commits atomic: one logical change per commit
