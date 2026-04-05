# Tests: jira MCP

## Scenarios

### 1. Fetch epic with linked stories

**Input:** Agent calls `get_epic("PROJ-1")` against a Jira project that has epic PROJ-1 ("User Authentication") with child stories PROJ-2 and PROJ-3.

**Expected behavior:**
- Returns a dict with keys: `key`, `title`, `description`, `status`, `stories`
- `title` is `"User Authentication"`
- `stories` is a list containing `"PROJ-2"` and `"PROJ-3"`
- `status` is a non-empty string (e.g. `"In Progress"` or `"To Do"`)
- `description` is a string (may be empty if no description set)

**Pass criteria:** All five keys present; `stories` contains both child keys; no exception raised.

---

### 2. List stories with acceptance criteria

**Input:** Agent calls `list_stories("PROJ-1")` for the same epic.

**Expected behavior:**
- Returns a list of 2 dicts, one per story
- Each dict contains: `key`, `summary`, `acceptance_criteria`, `priority`, `labels`, `status`
- At least one story has `acceptance_criteria` containing the word `"dashboard"` (from the "Login with valid credentials" story)
- `priority` is a non-empty string
- `labels` is a list

**Pass criteria:** List length is 2; all required keys present in each item; acceptance criteria text is non-empty for PROJ-2.

---

### 3. Search issues by JQL

**Input:** Agent calls `search_issues("project = PROJ")` to retrieve all issues in the PROJ project.

**Expected behavior:**
- Returns a non-empty list of dicts
- Each dict contains: `key`, `summary`, `status`, `priority`, `labels`
- All three fixture issues (PROJ-1, PROJ-2, PROJ-3) appear in results
- `labels` is a list on every result item

**Pass criteria:** Result list length >= 3; all required keys present on every item; no exception raised.

---

## Rubric

| Criterion | Pass | Fail |
|-----------|------|------|
| Response shape correctness | All required keys present in every returned dict / list item | Any required key missing from any result |
| Acceptance criteria extraction | ADF description fields are converted to readable plain text strings | Raw ADF dict objects returned instead of strings |
| Epic-to-story linking | `get_epic` returns child story keys via JQL epic-link query | `stories` list is empty or missing when children exist |
| JQL search filtering | `search_issues` returns only issues matching the provided JQL | Returns all issues regardless of JQL, or raises an error on valid JQL |
| Error handling | Non-existent issue key raises `requests.HTTPError` with a descriptive message | Server crashes, returns `None`, or silently returns empty dict |

---

## Golden Set

### Golden 1 — get_epic response shape

**Tool call:**
```python
jira_client.get_epic("PROJ-1")
```

**Expected response (exact shape, approximate values):**
```json
{
  "key": "PROJ-1",
  "title": "User Authentication",
  "description": "Epic covering all user authentication flows including login, logout, and token management.",
  "status": "In Progress",
  "stories": ["PROJ-2", "PROJ-3"]
}
```

**Constraints:**
- `key` must equal `"PROJ-1"` exactly
- `title` must equal `"User Authentication"` exactly
- `stories` must be a list; order is not significant but both keys must be present
- `description` must be a plain string, not an ADF dict
- `status` must be a non-empty string
