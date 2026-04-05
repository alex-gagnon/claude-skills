# Tests: agentic-test-creator

## Scenarios

### 1. Jira epic → Playwright E2E tests
**Input:** User says "Generate tests for PROJ-1" and provides ACs for a login feature with 3 acceptance criteria.
**Framework detected:** playwright.config.py present in repo.
**Expected:** Agent loads jira-flow.md, uses Jira MCP or prompts for ACs, generates `test_login.py` with 3+ test functions using playwright.sync_api.Page. Output ends with `### Tests Generated` summary block.

### 2. PR number → REST API tests
**Input:** User says "Write tests for PR #42" where PR modifies a `/auth/login` route handler.
**Framework detected:** `swagger.yaml` found in repo root.
**Expected:** Agent loads pr-flow.md, runs `gh pr view 42`, identifies changed API file, generates `test_login_api.py` with happy path + error tests using `requests`. Docstrings cite PR #42.

### 3. QA engineer text → Selenium tests
**Input:** User pastes: "1. User can log in with valid credentials. 2. Invalid password shows error. 3. Locked account shows support message."
**Framework detected:** `selenium` in requirements.txt.
**Expected:** Agent loads qa-flow.md, parses 3 ACs, asks for base_url, generates `test_login.py` with 3 test functions using WebDriverWait. Each has `# QA:` traceability comment.

### 4. No framework detected → agent asks
**Input:** Fresh repo with no test config. User says "Create tests from these ACs: [paste]".
**Expected:** Agent detects no framework, asks exactly one question: "Which test type? (1) Playwright E2E  (2) Selenium E2E  (3) REST API". After user answers, proceeds with correct template.

## Rubric

| Criterion | Pass | Fail |
|-----------|------|------|
| Correct flow loaded | Agent loads the flow file matching the input type | Agent uses wrong flow or skips flow files |
| Framework detection | Correctly identifies framework from repo signals or asks | Silently picks wrong framework |
| Test function structure | Each test has a clear name, docstring citing source, and at least one assertion | Missing docstrings, vague names, or no assertions |
| Template fidelity | Generated code matches the loaded template patterns | Mixes frameworks, wrong API used (e.g. JS Playwright) |
| Output summary | Ends with `### Tests Generated` block with file, source, framework, coverage | Missing or incomplete summary |
| One question rule | If info is missing, asks exactly one focused question | Asks multiple questions at once or proceeds without needed info |

## Golden Set

### Golden 1 — Playwright E2E from QA text
**Input:** "1. User can log in with valid email and password — redirected to /dashboard. 2. Invalid password shows error message."

**Ideal output:**
```python
# test_login.py
import pytest
from playwright.sync_api import Page, expect

def test_valid_credentials_redirect_to_dashboard(page: Page):
    # QA: User can log in with valid email and password — redirected to /dashboard
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_label("Password").fill("ValidPass123!")
    page.get_by_role("button", name="Log in").click()
    expect(page).to_have_url("/dashboard")

def test_invalid_password_shows_error(page: Page):
    # QA: Invalid password shows error message
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_label("Password").fill("wrongpassword")
    page.get_by_role("button", name="Log in").click()
    expect(page.get_by_role("alert")).to_be_visible()
```

### Tests Generated
- File: `test_login.py`
- Source: QA input (2 acceptance criteria → 2 test functions)
- Framework: Playwright Python (pytest-playwright)
- Assumptions made: base_url configured in conftest.py, login form uses label="Email" and label="Password"
