"""Jira Cloud REST API v3 client."""

from __future__ import annotations

from typing import Any

import requests
from requests.auth import HTTPBasicAuth


def _extract_text(adf_doc: Any) -> str:
    """Recursively extract plain text from an Atlassian Document Format (ADF) node.

    Jira Cloud returns description fields as ADF dicts.  This helper walks the
    node tree and concatenates all text leaf values so callers receive a plain
    string regardless of whether the field was stored as ADF or a legacy
    plain-text string.
    """
    if adf_doc is None:
        return ""
    if isinstance(adf_doc, str):
        return adf_doc
    if not isinstance(adf_doc, dict):
        return str(adf_doc)

    node_type = adf_doc.get("type", "")

    # Text leaf node
    if node_type == "text":
        return adf_doc.get("text", "")

    # Recurse into content array
    parts: list[str] = []
    for child in adf_doc.get("content", []):
        text = _extract_text(child)
        if text:
            parts.append(text)

    # Add spacing between block-level nodes
    separator = "\n" if node_type in ("paragraph", "heading", "bulletList", "listItem", "orderedList") else " "
    return separator.join(parts).strip()


class JiraClient:
    """Thin wrapper around Jira Cloud REST API v3.

    Parameters
    ----------
    base_url:
        Root URL of the Jira Cloud instance, e.g. ``https://your-org.atlassian.net``.
    email:
        Email address of the authenticating user.
    api_token:
        API token generated at https://id.atlassian.com/manage-profile/security/api-tokens.
    """

    def __init__(self, base_url: str, email: str, api_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self._auth = HTTPBasicAuth(email, api_token)
        self._session = requests.Session()
        self._session.auth = self._auth
        self._session.headers.update(
            {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """Execute a GET request and raise on non-2xx status."""
        url = f"{self.base_url}{path}"
        response = self._session.get(url, params=params)
        if not response.ok:
            raise requests.HTTPError(
                f"Jira API request failed [{response.status_code}] {response.reason}: "
                f"GET {url} — {response.text[:400]}",
                response=response,
            )
        return response.json()

    def _issue_to_story(self, issue: dict) -> dict:
        """Map a raw Jira issue payload to the standard story shape."""
        fields = issue.get("fields", {})
        return {
            "key": issue.get("key", ""),
            "summary": fields.get("summary", ""),
            "acceptance_criteria": _extract_text(
                fields.get("description") or fields.get("customfield_10016") or ""
            ),
            "priority": (fields.get("priority") or {}).get("name", ""),
            "labels": fields.get("labels", []),
            "status": (fields.get("status") or {}).get("name", ""),
            "story_points": fields.get("story_points")
            or fields.get("customfield_10016")
            if isinstance(
                fields.get("story_points") or fields.get("customfield_10016"), (int, float)
            )
            else None,
        }

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_epic(self, epic_key: str) -> dict:
        """Fetch an epic by key.

        Returns a dict with:
            key, title, description, status, stories (list of child story keys).
        """
        data = self._get(f"/rest/api/3/issue/{epic_key}")
        fields = data.get("fields", {})

        # Search for child stories linked to this epic
        jql = f'"Epic Link" = {epic_key} OR "Epic" = {epic_key}'
        search_data = self._get(
            "/rest/api/3/search",
            params={
                "jql": jql,
                "fields": "summary,status",
                "maxResults": 200,
            },
        )
        story_keys = [issue["key"] for issue in search_data.get("issues", [])]

        return {
            "key": data.get("key", epic_key),
            "title": fields.get("summary", ""),
            "description": _extract_text(fields.get("description")),
            "status": (fields.get("status") or {}).get("name", ""),
            "stories": story_keys,
        }

    def list_stories(self, epic_key: str) -> list[dict]:
        """List all stories linked to an epic.

        Returns a list of dicts, each with:
            key, summary, acceptance_criteria, priority, labels, status.
        """
        jql = f'"Epic Link" = {epic_key} OR "Epic" = {epic_key}'
        data = self._get(
            "/rest/api/3/search",
            params={
                "jql": jql,
                "fields": "summary,description,priority,labels,status,story_points,customfield_10016",
                "maxResults": 200,
            },
        )
        stories = []
        for issue in data.get("issues", []):
            story = self._issue_to_story(issue)
            # list_stories does not include story_points in its contract
            story.pop("story_points", None)
            stories.append(story)
        return stories

    def get_story(self, story_key: str) -> dict:
        """Fetch full detail for a single story.

        Returns a dict with:
            key, summary, acceptance_criteria, priority, labels, status, story_points.
        """
        data = self._get(
            f"/rest/api/3/issue/{story_key}",
        )
        return self._issue_to_story(data)

    def search_issues(self, jql: str) -> list[dict]:
        """Execute a JQL query and return matching issues.

        Returns a list of dicts, each with:
            key, summary, status, priority, labels.
        """
        data = self._get(
            "/rest/api/3/search",
            params={
                "jql": jql,
                "fields": "summary,status,priority,labels",
                "maxResults": 200,
            },
        )
        results = []
        for issue in data.get("issues", []):
            fields = issue.get("fields", {})
            results.append(
                {
                    "key": issue.get("key", ""),
                    "summary": fields.get("summary", ""),
                    "status": (fields.get("status") or {}).get("name", ""),
                    "priority": (fields.get("priority") or {}).get("name", ""),
                    "labels": fields.get("labels", []),
                }
            )
        return results
