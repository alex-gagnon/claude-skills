"""Jira MCP server — exposes Jira Cloud data as callable MCP tools via FastMCP."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from jira_client import JiraClient

load_dotenv()

mcp = FastMCP("jira")
_client: JiraClient | None = None


def get_client() -> JiraClient:
    """Return the shared JiraClient, initialising it on first call."""
    global _client
    if _client is None:
        _client = JiraClient(
            base_url=os.environ["JIRA_BASE_URL"],
            email=os.environ["JIRA_EMAIL"],
            api_token=os.environ["JIRA_API_TOKEN"],
        )
    return _client


@mcp.tool()
def get_epic(epic_key: str) -> dict:
    """Fetch an epic by key: title, description, linked story keys, status.

    Parameters
    ----------
    epic_key:
        The Jira issue key of the epic, e.g. ``PROJ-1``.

    Returns
    -------
    dict
        ``{ key, title, description, status, stories: [str] }``
    """
    return get_client().get_epic(epic_key)


@mcp.tool()
def list_stories(epic_key: str) -> list[dict]:
    """List all stories in an epic with summary, acceptance_criteria, priority, labels, status.

    Parameters
    ----------
    epic_key:
        The Jira issue key of the parent epic, e.g. ``PROJ-1``.

    Returns
    -------
    list[dict]
        Each item: ``{ key, summary, acceptance_criteria, priority, labels, status }``
    """
    return get_client().list_stories(epic_key)


@mcp.tool()
def get_story(story_key: str) -> dict:
    """Fetch full detail for a single story.

    Parameters
    ----------
    story_key:
        The Jira issue key of the story, e.g. ``PROJ-2``.

    Returns
    -------
    dict
        ``{ key, summary, acceptance_criteria, priority, labels, status, story_points }``
    """
    return get_client().get_story(story_key)


@mcp.tool()
def search_issues(jql: str) -> list[dict]:
    """Execute a JQL query and return matching issues.

    Parameters
    ----------
    jql:
        A valid Jira Query Language expression,
        e.g. ``project = PROJ AND status = "In Progress"``.

    Returns
    -------
    list[dict]
        Each item: ``{ key, summary, status, priority, labels }``
    """
    return get_client().search_issues(jql)


if __name__ == "__main__":
    mcp.run()
