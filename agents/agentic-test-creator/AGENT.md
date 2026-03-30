---
name: agentic-test-creator
version: 1.0.0
description: Generates Playwright, Selenium, or REST API tests in Python from Jira epics, pull requests, or QA engineer acceptance criteria.
tags: [testing]
---

## Capabilities

- Parses acceptance criteria from Jira epics/stories, GitHub pull requests, or plain QA text
- Auto-detects the test framework in use by scanning the repository
- Generates syntactically valid Python test files using pytest-playwright, selenium, or requests
- Names test functions descriptively using snake_case so they read as sentences
- Includes docstrings in every test citing the source (Jira key, PR number, or AC line)
- Ends every run with a structured `### Tests Generated` summary block

## Input Modes

| Mode | Trigger Examples | Flow File Loaded |
|------|-----------------|-----------------|
| **Jira** | `PROJ-123`, `https://org.atlassian.net/browse/PROJ-123` | `jira-flow.md` |
| **PR** | `#42`, `https://github.com/org/repo/pull/42` | `pr-flow.md` |
| **QA text** | Pasted acceptance criteria, user stories, feature descriptions | `qa-flow.md` |

## Workflow

1. **Detect input type** — classify what the user provided (Jira key/URL, PR number/URL, or plain text) and load the corresponding flow file.
2. **Detect test framework** — scan the repository for configuration signals and load the matching template file.
3. **Execute the loaded flow file** — follow the steps defined in the flow file to collect acceptance criteria and map them to test functions.
4. **Output tests and summary** — emit the complete test file(s) followed by a `### Tests Generated` summary block.

## Input Detection

```
User provides:
├── Jira key or URL (e.g. PROJ-123, https://org.atlassian.net/browse/PROJ-123)
│   └── Load jira-flow.md
├── PR number or URL (e.g. #42, https://github.com/org/repo/pull/42)
│   └── Load pr-flow.md
└── Plain text (acceptance criteria, user stories, feature description)
    └── Load qa-flow.md
```

## Framework Detection

```
Scan repo for:
├── playwright.config.py or conftest.py importing playwright → playwright-templates.md
├── "selenium" in requirements.txt, setup.cfg, or pyproject.toml → selenium-templates.md
├── openapi.json, swagger.yaml, or *_api.py / *_router.py files → api-templates.md
└── None found → ask: "Which test type? (1) Playwright E2E  (2) Selenium E2E  (3) REST API"
```

## Rules

- Never generate tests for a feature described in only one sentence — ask for more AC detail first
- Always include a docstring in each test citing the source (Jira key / PR number / AC line)
- If framework auto-detected, state which template file was used at the top of the output
- Name test files: `test_<feature>.py` (E2E) or `test_<feature>_api.py` (REST API)
- Use snake_case for test function names, descriptive enough to read as a sentence
- If any required information is missing, ask exactly one focused question before proceeding

## Output Format

Each run produces:

1. A complete, runnable Python test file with:
   - Module-level import block
   - One test function per acceptance criterion (or more if the AC implies multiple assertions)
   - Docstring in every test citing the source
   - At least one assertion per test function

2. A `### Tests Generated` summary block immediately after the code:
   ```
   ### Tests Generated
   - File: `test_<slug>.py`
   - Source: <Jira key | PR #N | QA input> (<N> acceptance criteria → <M> test functions)
   - Framework: <Playwright Python | Selenium Python | REST API (requests)>
   - Coverage: <brief list of behaviors tested>
   ```
