# Skills

A collection of Claude Code skills for common development workflows. Skills are invoked as slash commands in any Claude Code session where this repository is configured as the skills directory.

## Available Skills

| Skill | Command | Description | Sub-behaviors / Support Files |
|---|---|---|---|
| source-control | `/source-control` | Handles git workflow — routes to commit, branch, or diff summary based on context. | commit, branch, summarize-diff |
| review-pr | `/review-pr` | Reviews a pull request for logic errors, security issues, test coverage, and style — producing structured inline feedback. | `checklist.md` |
| simplify | `/simplify` | Refactors a code block or file to reduce complexity, improve readability, and eliminate redundancy without changing behavior. | `patterns.md` |
| add-tests | `/add-tests` | Generates tests for an existing function or module, covering happy paths, edge cases, and error conditions. | `test-strategies.md` |
| document | `/document` | Adds or improves inline documentation, docstrings, and README sections for a function, module, or project. | `templates.md` |
| explain | `/explain` | Explains a piece of code, architecture decision, or technical concept in plain language calibrated to the user's apparent expertise level. | — |
| grill | `/grill` | Challenges a design, plan, or idea using Socratic questioning and devil's-advocate critique to surface hidden assumptions and weaknesses. | `question-bank.md` |
| test | `/test` | Runs quality evaluations against one or all skills using their tests.md fixture files, scoring format compliance and semantic correctness. | — |

## Testing Skills

Each skill has a `tests.md` file with scenarios, rubrics, and golden outputs. There are two ways to run tests:

**Semantic quality (LLM-as-judge)** — run the `/test` skill to evaluate all skills:
```
/test                  # evaluate all skills
/test source-control   # evaluate one skill
```

**Format/schema assertions (CI)** — run promptfoo for deterministic checks:
```bash
npx promptfoo eval           # run all format assertions
npx promptfoo eval --ci      # CI mode (exits non-zero on failure)
```

Promptfoo requires Node.js. Install it with `npm install -g promptfoo` or use `npx`.

## Installation

### npm

```bash
npm install claude-skills
```

```js
const { skillsDir } = require('claude-skills');
// use skillsDir as skillsDirectory in ~/.claude/settings.json
```

### pip

```bash
pip install claude-skills
```

```python
from claude_skills import skills_dir
# use skills_dir as skillsDirectory in ~/.claude/settings.json
```

### Git (manual)

Clone the repo and point Claude Code's `skillsDirectory` at the `skills/` folder:

```jsonc
// ~/.claude/settings.json
{
  "skillsDirectory": "/path/to/this/repo/skills"
}
```

Or symlink:

```bash
ln -s /path/to/this/repo/skills ~/.claude/skills
```

## Publishing

Releases are published to npm and PyPI automatically when a version tag is pushed:

```bash
git tag v1.0.0
git push origin v1.0.0
```

Requires `NPM_TOKEN` and `PYPI_API_TOKEN` secrets set in GitHub repo settings.

## Adding a Skill

See [CLAUDE.md](./CLAUDE.md) for conventions and the `skills/source-control/SKILL.md` file as a template for skills with Tier 3 sub-behaviors.
