# SDET Marketplace

A marketplace of Claude Code plugins — skills, agents, and MCP servers — for common software development and testing workflows.

## Installation

Add this marketplace to Claude Code:

```bash
/plugin marketplace add https://github.com/alex-gagnon/sdet-marketplace
```

Or for local development:

```bash
/plugin marketplace add ./path/to/sdet-marketplace
```

## Available Plugins

### Skills

| Skill | Command | Description | Support Files |
|-------|---------|-------------|---------------|
| source-control | `/source-control` | Git workflow — routes to commit, branch, or diff summary based on context. | commit, branch, summarize-diff |
| review-pr | `/review-pr` | Reviews a pull request for logic errors, security issues, test coverage, and style. | checklist.md |
| simplify | `/simplify` | Refactors code to reduce complexity and improve readability without changing behavior. | patterns.md |
| add-tests | `/add-tests` | Generates tests covering happy paths, edge cases, and error conditions. | test-strategies.md |
| document | `/document` | Adds or improves inline documentation, docstrings, and README sections. | templates.md |
| explain | `/explain` | Explains code or concepts in plain language calibrated to the user's expertise level. | — |
| grill | `/grill` | Challenges a design using Socratic questioning to surface hidden assumptions. | question-bank.md |
| test | `/test` | Runs quality evaluations against plugins using their tests.md fixture files. | — |

### Agents

| Agent | Description |
|-------|-------------|
| plugin-architect | Designs and scaffolds new marketplace plugins following official conventions. |
| agentic-test-creator | Generates Playwright, Selenium, or REST API tests in Python from Jira epics, PRs, or QA acceptance criteria. |

### MCP Servers

| MCP | Description | Support Files |
|-----|-------------|---------------|
| jira | Exposes Jira epics and stories as callable tools (`get_epic`, `list_stories`, `get_story`, `search_issues`). | server.py, jira_client.py, mock_jira_server.py |

## Repository Structure

```
sdet-marketplace/
├── .claude-plugin/
│   └── marketplace.json     # Marketplace catalog (all plugins registered here)
├── skills/
│   └── <name>/
│       ├── SKILL.md         # Entrypoint
│       ├── plugin.json      # Plugin metadata
│       ├── tests.md         # Test scenarios and rubric
│       └── *.md             # Support files
├── agents/
│   └── <name>/
│       ├── AGENT.md
│       ├── plugin.json
│       └── tests.md
└── mcps/
    └── <name>/
        ├── MCP.md
        ├── plugin.json
        └── tests.md
```

## Testing

Each plugin has a `tests.md` with scenarios, rubrics, and golden outputs.

**Semantic quality (LLM-as-judge):**
```
/test                  # evaluate all skills
/test source-control   # evaluate one skill
```

**Format assertions (CI):**
```bash
npx promptfoo eval
npx promptfoo eval --ci
```

## Adding a Plugin

See [CLAUDE.md](./CLAUDE.md) for conventions, or invoke the **plugin-architect** agent to interactively design and scaffold a new plugin.
