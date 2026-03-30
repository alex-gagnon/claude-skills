"""FastAPI mock server that mimics Jira REST API v3 for use in integration tests."""

from __future__ import annotations

from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException, Query

app = FastAPI(title="Mock Jira API v3")

# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

_ISSUES: dict[str, dict[str, Any]] = {
    "PROJ-1": {
        "id": "10001",
        "key": "PROJ-1",
        "fields": {
            "summary": "User Authentication",
            "issuetype": {"name": "Epic"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Epic covering all user authentication flows including login, logout, and token management.",
                            }
                        ],
                    }
                ],
            },
            "status": {"name": "In Progress"},
            "priority": {"name": "High"},
            "labels": ["authentication", "security"],
            "story_points": None,
            "customfield_10016": None,
            # Simulates the "Epic" parent link used by next-gen projects
            "epic": None,
        },
    },
    "PROJ-2": {
        "id": "10002",
        "key": "PROJ-2",
        "fields": {
            "summary": "Login with valid credentials",
            "issuetype": {"name": "Story"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Given valid credentials, when the user submits the login form, then they are redirected to /dashboard. Given invalid credentials, when the user submits the login form, then an error message is displayed.",
                            }
                        ],
                    }
                ],
            },
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "labels": ["login", "authentication"],
            "story_points": 3,
            "customfield_10016": 3,
            # Classic project epic link
            "customfield_10014": "PROJ-1",
        },
    },
    "PROJ-3": {
        "id": "10003",
        "key": "PROJ-3",
        "fields": {
            "summary": "Login API returns JWT",
            "issuetype": {"name": "Story"},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Given valid credentials, when POST /auth/login is called, then the response is 200 with an access_token field. Given invalid credentials, when POST /auth/login is called, then the response is 401.",
                            }
                        ],
                    }
                ],
            },
            "status": {"name": "In Progress"},
            "priority": {"name": "Medium"},
            "labels": ["api", "jwt", "authentication"],
            "story_points": 5,
            "customfield_10016": 5,
            "customfield_10014": "PROJ-1",
        },
    },
}


def _epic_children(epic_key: str) -> list[dict]:
    """Return all issues whose classic or next-gen epic link points to epic_key."""
    children = []
    for issue in _ISSUES.values():
        fields = issue["fields"]
        classic_link = fields.get("customfield_10014", "")
        epic_ref = (fields.get("epic") or {}).get("key", "")
        if classic_link == epic_key or epic_ref == epic_key:
            children.append(issue)
    return children


def _matches_jql(issue: dict, jql: str) -> bool:
    """Very simple JQL matcher sufficient for the test suite.

    Supports:
    - ``project = PROJ``  — matches all issues whose key starts with PROJ-
    - ``"Epic Link" = PROJ-1``  — matches classic epic link children
    - ``"Epic" = PROJ-1``  — same as above (next-gen)
    - Combinations joined with OR
    """
    jql_lower = jql.lower().strip()
    key: str = issue["key"]
    fields = issue["fields"]

    # Split on OR and check each clause
    clauses = [c.strip() for c in jql_lower.split(" or ")]
    for clause in clauses:
        # project = PROJ
        if clause.startswith("project"):
            parts = clause.split("=")
            if len(parts) == 2:
                project = parts[1].strip().strip('"').strip("'").upper()
                if key.startswith(f"{project}-"):
                    return True

        # "Epic Link" = PROJ-1  or  "Epic" = PROJ-1
        if "epic" in clause and "=" in clause:
            parts = clause.split("=")
            if len(parts) == 2:
                epic_key = parts[1].strip().strip('"').strip("'").upper()
                classic_link = (fields.get("customfield_10014") or "").upper()
                epic_ref = ((fields.get("epic") or {}).get("key") or "").upper()
                if classic_link == epic_key or epic_ref == epic_key:
                    return True

    return False


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/rest/api/3/issue/{key}")
def get_issue(key: str) -> dict:
    """Return a single issue by key."""
    issue = _ISSUES.get(key.upper())
    if issue is None:
        raise HTTPException(status_code=404, detail=f"Issue {key} not found")
    return issue


@app.get("/rest/api/3/search")
def search_issues(jql: str = Query(default="")) -> dict:
    """Search issues using a simplified JQL parser."""
    matched = [issue for issue in _ISSUES.values() if _matches_jql(issue, jql)]
    return {
        "total": len(matched),
        "maxResults": 200,
        "startAt": 0,
        "issues": matched,
    }


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
