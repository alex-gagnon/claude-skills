"""Input handlers for the three supported input modes."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth

from config import config


class InputMode(str, Enum):
    JIRA = "jira"
    PR = "pr"
    TEXT = "text"


@dataclass
class TestContext:
    mode: InputMode
    raw: str          # Human-readable source description (e.g. "PROJ-123", "#42", "QA text")
    content: str      # Structured text passed to the agent as prompt context
    source_ref: str   # Citation string for docstrings (e.g. "PROJ-123", "PR #42", "QA input")


# ---------------------------------------------------------------------------
# Jira input
# ---------------------------------------------------------------------------

class JiraFetcher:
    """Fetches epic/story data from Jira REST API v3."""

    def __init__(self) -> None:
        if not config.jira_base_url or not config.jira_email or not config.jira_api_token:
            raise ValueError(
                "Jira credentials are required. Set JIRA_BASE_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN environment variables."
            )
        self.base_url = config.jira_base_url.rstrip("/")
        self.auth = HTTPBasicAuth(config.jira_email, config.jira_api_token)
        self.headers = {"Accept": "application/json"}

    def _get(self, path: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        resp = requests.get(url, headers=self.headers, auth=self.auth, params=params)
        resp.raise_for_status()
        return resp.json()

    def _extract_text(self, adf: object, depth: int = 0) -> str:
        """Recursively extract plain text from Atlassian Document Format."""
        if adf is None:
            return ""
        if isinstance(adf, str):
            return adf
        if isinstance(adf, dict):
            node_type = adf.get("type", "")
            text = adf.get("text", "")
            if text:
                return text
            children = adf.get("content", [])
            parts = [self._extract_text(child, depth + 1) for child in children]
            separator = "\n" if node_type in ("paragraph", "heading", "listItem", "bulletList", "orderedList") else ""
            return separator.join(p for p in parts if p)
        if isinstance(adf, list):
            return "\n".join(self._extract_text(item, depth) for item in adf)
        return ""

    def get_issue(self, key: str) -> dict:
        return self._get(f"/rest/api/3/issue/{key}")

    def get_children(self, key: str) -> list[dict]:
        data = self._get(
            "/rest/api/3/search",
            params={"jql": f'"Epic Link" = {key} OR parent = {key}', "maxResults": 50},
        )
        return data.get("issues", [])

    def build_context(self, key: str) -> TestContext:
        """Fetch an epic or story and build a TestContext from it."""
        issue = self.get_issue(key)
        fields = issue.get("fields", {})
        issue_type = fields.get("issuetype", {}).get("name", "Issue")
        summary = fields.get("summary", key)
        description = self._extract_text(fields.get("description")) or "(no description)"

        lines = [
            f"Source: Jira {issue_type} {key}",
            f"Summary: {summary}",
            "",
            "Description:",
            description,
        ]

        if issue_type.lower() in ("epic", "initiative"):
            children = self.get_children(key)
            if children:
                lines += ["", f"Linked Stories ({len(children)}):"]
                for child in children:
                    cf = child.get("fields", {})
                    child_key = child["key"]
                    child_summary = cf.get("summary", "")
                    child_ac = self._extract_text(
                        cf.get("customfield_10016") or cf.get("description")
                    )
                    lines.append(f"\n## {child_key}: {child_summary}")
                    if child_ac:
                        lines.append("Acceptance Criteria:")
                        lines.append(child_ac)
        else:
            # Story/task — look for AC in customfield_10016 or description
            ac = self._extract_text(
                fields.get("customfield_10016") or fields.get("description")
            )
            if ac:
                lines += ["", "Acceptance Criteria:", ac]

        return TestContext(
            mode=InputMode.JIRA,
            raw=key,
            content="\n".join(lines),
            source_ref=key,
        )


# ---------------------------------------------------------------------------
# GitHub PR input
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{result.stderr}")
    return result.stdout.strip()


def build_pr_context(pr_ref: str) -> TestContext:
    """
    Fetch PR metadata and changed files via gh CLI.
    pr_ref can be a number (42), #42, or a full GitHub URL.
    """
    # Normalise to a number string
    pr_number = re.sub(r"[^0-9]", "", pr_ref.split("/")[-1])
    if not pr_number:
        raise ValueError(f"Cannot parse PR number from: {pr_ref!r}")

    # Fetch PR details
    pr_json = _run([
        "gh", "pr", "view", pr_number,
        "--json", "title,body,files,number,baseRefName,headRefName",
    ])
    pr = json.loads(pr_json)
    title = pr.get("title", "")
    body = pr.get("body") or ""
    files = pr.get("files", [])
    number = pr.get("number", pr_number)

    changed = [f["path"] for f in files]
    ui_files = [p for p in changed if _is_ui_file(p)]
    api_files = [p for p in changed if _is_api_file(p)]

    lines = [
        f"Source: GitHub PR #{number}",
        f"Title: {title}",
        "",
        "Description:",
        body or "(no description)",
        "",
        f"Changed files ({len(changed)} total):",
    ]
    for path in changed:
        lines.append(f"  - {path}")

    if ui_files:
        lines += ["", "UI-related files (candidates for E2E tests):"]
        for path in ui_files:
            lines.append(f"  - {path}")
    if api_files:
        lines += ["", "API/route files (candidates for REST API tests):"]
        for path in api_files:
            lines.append(f"  - {path}")

    # Read diffs for key changed files (first 5 to keep context bounded)
    for path in changed[:5]:
        try:
            diff = _run(["gh", "api", f"repos/{{owner}}/{{repo}}/contents/{path}"])
        except Exception:
            pass  # diff not critical

    return TestContext(
        mode=InputMode.PR,
        raw=f"PR #{number}",
        content="\n".join(lines),
        source_ref=f"PR #{number}",
    )


def _is_ui_file(path: str) -> bool:
    ui_patterns = (
        "component", "page", "view", "screen", "layout",
        ".tsx", ".jsx", ".vue", ".svelte", ".html",
    )
    return any(p in path.lower() for p in ui_patterns)


def _is_api_file(path: str) -> bool:
    api_patterns = (
        "router", "route", "controller", "handler", "endpoint",
        "_api", "api_", "views.py", "serializer",
    )
    return any(p in path.lower() for p in api_patterns)


# ---------------------------------------------------------------------------
# QA text input
# ---------------------------------------------------------------------------

def build_text_context(text: str) -> TestContext:
    """
    Parse pasted acceptance criteria / user stories into a TestContext.
    Tries to number ACs and identify Given/When/Then structure.
    """
    lines = text.strip().splitlines()
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if stripped:
            cleaned.append(stripped)

    ac_lines = _extract_acs(cleaned)
    count = len(ac_lines)

    content_parts = [
        "Source: QA engineer acceptance criteria (pasted text)",
        f"Total acceptance criteria found: {count}",
        "",
        "Acceptance Criteria:",
    ]
    content_parts.extend(ac_lines if ac_lines else cleaned)

    return TestContext(
        mode=InputMode.TEXT,
        raw="QA text input",
        content="\n".join(content_parts),
        source_ref="QA input",
    )


def _extract_acs(lines: list[str]) -> list[str]:
    """Heuristically identify and number AC lines."""
    ac_markers = ("given", "when", "then", "and ", "but ", "ac ", "ac:", "scenario")
    numbered = re.compile(r"^\s*(\d+[\.\)]|\*|-)\s+")
    result = []
    ac_num = 1
    for line in lines:
        lower = line.lower()
        if any(lower.startswith(m) for m in ac_markers) or numbered.match(line):
            result.append(f"AC-{ac_num}: {line}")
            ac_num += 1
        else:
            result.append(line)
    return result


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

_JIRA_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]+-\d+$")
_JIRA_URL_RE = re.compile(r"atlassian\.net/browse/([A-Z][A-Z0-9_]+-\d+)")
_PR_RE = re.compile(r"(#\d+|github\.com/.+/pull/\d+|\bPR\s*#?\d+)")


def detect_and_build(user_input: str) -> TestContext:
    """Auto-detect input mode and build a TestContext."""
    stripped = user_input.strip()

    # Jira URL
    m = _JIRA_URL_RE.search(stripped)
    if m:
        return JiraFetcher().build_context(m.group(1))

    # Jira key (e.g. PROJ-123)
    if _JIRA_KEY_RE.match(stripped.split()[0] if stripped.split() else ""):
        return JiraFetcher().build_context(stripped.split()[0])

    # GitHub PR reference
    if _PR_RE.search(stripped):
        return build_pr_context(stripped)

    # Fall back to plain text
    return build_text_context(stripped)
