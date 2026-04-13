# Personal Marketplace

A marketplace of Claude Code plugins organized as domain toolkits — skills, agents, Agent SDK loops, and MCP servers for software development and testing workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add https://github.com/alex-gagnon/personal-marketplace
```

Or for local development:

```bash
/plugin marketplace add ./path/to/personal-marketplace
```

## Toolkits

### code-review-tools

Skills for reviewing, simplifying, and understanding code.

| Skill | Command | Description |
|-------|---------|-------------|
| review-pr | `/review-pr` | Reviews a pull request for logic errors, security issues, test coverage, and style. |
| simplify | `/simplify` | Refactors code to reduce complexity and improve readability without changing behavior. |
| source-control | `/source-control` | Git workflow — routes to commit, branch, or diff summary based on context. |
| explain | `/explain` | Explains code or concepts in plain language calibrated to the user's expertise level. |

### dev-tools

Developer productivity skills.

| Skill | Command | Description |
|-------|---------|-------------|
| add-unit-tests | `/add-unit-tests` | Generates unit tests for an existing function or module, covering happy paths, edge cases, and error conditions. |

### sdet-tools

E2E and API test generation from Jira epics, PRs, or QA acceptance criteria. The `test-generator` ships as both a Claude Code agent (human-in-the-loop) and an autonomous Agent SDK loop — both share the same flows and templates so updates to one are immediately reflected in the other.

| Component | Type | Description |
|-----------|------|-------------|
| test-generator | Agent | Human-in-the-loop Claude Code agent. Generates Playwright, Selenium, or REST API tests from Jira/PR/AC input. |
| test-generator | Agent SDK | Autonomous loop implementation. Reads flows and templates from the `agents/` directory. |
| jira | MCP | Exposes Jira epics and stories as callable tools (`get_epic`, `list_stories`, `get_story`, `search_issues`). |

### plugin-tools

Tools for building and maintaining Claude Code marketplace plugins.

| Component | Type | Command | Description |
|-----------|------|---------|-------------|
| plugin-architect | Agent | — | Designs and scaffolds new marketplace plugins following official conventions. |
| document | Skill | `/document` | Adds or improves inline documentation, docstrings, and README sections. |

### grill-me

Challenges designs, plans, and ideas with Socratic questioning and devil's-advocate critique to surface hidden assumptions and weaknesses.

| Skill | Command | Description |
|-------|---------|-------------|
| grill | `/grill` | Challenge a design, plan, or idea and stress-test your assumptions. |

## Repository Structure

```
personal-marketplace/
├── .claude-plugin/
│   └── marketplace.json          # Top-level toolkit catalog
├── plugins/
│   ├── code-review-tools/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/
│   │       ├── review-pr/
│   │       ├── simplify/
│   │       ├── source-control/
│   │       └── explain/
│   ├── dev-tools/
│   │   ├── .claude-plugin/plugin.json
│   │   └── skills/add-unit-tests/
│   ├── sdet-tools/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── .mcp.json
│   │   ├── agents/test-generator/
│   │   ├── sdk/
│   │   └── mcps/jira/
│   ├── plugin-tools/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── agents/plugin-architect/
│   │   └── skills/document/
│   └── grill-me/
│       ├── .claude-plugin/plugin.json
│       └── skills/grill/
├── scripts/
│   └── plugin-test/              # Internal plugin test runner (not user-facing)
└── test-apps/                    # Local test targets
```

## Adding a Plugin

See [CLAUDE.md](./CLAUDE.md) for conventions, or invoke the **plugin-architect** agent to interactively design and scaffold a new plugin.
