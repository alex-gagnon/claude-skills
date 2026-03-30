"""Integration tests for JiraClient against the mock Jira server."""

from __future__ import annotations

import pytest
import requests


# ---------------------------------------------------------------------------
# get_epic
# ---------------------------------------------------------------------------


def test_get_epic_returns_title_and_stories(jira_client, mock_server):
    result = jira_client.get_epic("PROJ-1")
    assert result["title"] == "User Authentication"
    assert "PROJ-2" in result["stories"]
    assert "PROJ-3" in result["stories"]


def test_get_epic_returns_required_keys(jira_client, mock_server):
    result = jira_client.get_epic("PROJ-1")
    for key in ("key", "title", "description", "status", "stories"):
        assert key in result, f"Missing key: {key}"


def test_get_epic_key_matches_input(jira_client, mock_server):
    result = jira_client.get_epic("PROJ-1")
    assert result["key"] == "PROJ-1"


def test_get_epic_description_is_plain_string(jira_client, mock_server):
    result = jira_client.get_epic("PROJ-1")
    assert isinstance(result["description"], str), "description must be a plain string, not ADF"


def test_get_epic_status_is_nonempty_string(jira_client, mock_server):
    result = jira_client.get_epic("PROJ-1")
    assert isinstance(result["status"], str)
    assert result["status"] != ""


def test_get_epic_not_found_raises_http_error(jira_client, mock_server):
    with pytest.raises(requests.HTTPError):
        jira_client.get_epic("PROJ-9999")


# ---------------------------------------------------------------------------
# list_stories
# ---------------------------------------------------------------------------


def test_list_stories_returns_acceptance_criteria(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    assert len(stories) == 2
    assert any("dashboard" in s["acceptance_criteria"].lower() for s in stories)


def test_list_stories_returns_two_stories(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    assert len(stories) == 2


def test_list_stories_required_keys(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    required = ("key", "summary", "acceptance_criteria", "priority", "labels", "status")
    for story in stories:
        for key in required:
            assert key in story, f"Story {story.get('key', '?')} missing key: {key}"


def test_list_stories_labels_are_lists(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    for story in stories:
        assert isinstance(story["labels"], list), f"labels should be a list for {story['key']}"


def test_list_stories_acceptance_criteria_are_strings(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    for story in stories:
        assert isinstance(
            story["acceptance_criteria"], str
        ), f"acceptance_criteria should be a string for {story['key']}"


def test_list_stories_proj2_has_nonempty_ac(jira_client, mock_server):
    stories = jira_client.list_stories("PROJ-1")
    proj2 = next((s for s in stories if s["key"] == "PROJ-2"), None)
    assert proj2 is not None
    assert proj2["acceptance_criteria"] != ""


# ---------------------------------------------------------------------------
# get_story
# ---------------------------------------------------------------------------


def test_get_story_returns_full_detail(jira_client, mock_server):
    story = jira_client.get_story("PROJ-2")
    assert story["summary"] == "Login with valid credentials"
    assert story["acceptance_criteria"] != ""


def test_get_story_required_keys(jira_client, mock_server):
    story = jira_client.get_story("PROJ-2")
    required = ("key", "summary", "acceptance_criteria", "priority", "labels", "status", "story_points")
    for key in required:
        assert key in story, f"Missing key: {key}"


def test_get_story_key_matches_input(jira_client, mock_server):
    story = jira_client.get_story("PROJ-3")
    assert story["key"] == "PROJ-3"


def test_get_story_summary_proj3(jira_client, mock_server):
    story = jira_client.get_story("PROJ-3")
    assert story["summary"] == "Login API returns JWT"


def test_get_story_acceptance_criteria_is_plain_string(jira_client, mock_server):
    story = jira_client.get_story("PROJ-2")
    assert isinstance(story["acceptance_criteria"], str)


def test_get_story_not_found_raises_http_error(jira_client, mock_server):
    with pytest.raises(requests.HTTPError):
        jira_client.get_story("PROJ-9999")


# ---------------------------------------------------------------------------
# search_issues
# ---------------------------------------------------------------------------


def test_search_issues_by_jql(jira_client, mock_server):
    results = jira_client.search_issues("project = PROJ")
    assert len(results) > 0
    assert all("key" in r for r in results)


def test_search_issues_returns_all_fixture_issues(jira_client, mock_server):
    results = jira_client.search_issues("project = PROJ")
    keys = {r["key"] for r in results}
    assert "PROJ-1" in keys
    assert "PROJ-2" in keys
    assert "PROJ-3" in keys


def test_search_issues_required_keys(jira_client, mock_server):
    results = jira_client.search_issues("project = PROJ")
    required = ("key", "summary", "status", "priority", "labels")
    for item in results:
        for key in required:
            assert key in item, f"Issue {item.get('key', '?')} missing key: {key}"


def test_search_issues_labels_are_lists(jira_client, mock_server):
    results = jira_client.search_issues("project = PROJ")
    for item in results:
        assert isinstance(item["labels"], list)


def test_search_issues_epic_link_jql(jira_client, mock_server):
    results = jira_client.search_issues('"Epic Link" = PROJ-1')
    keys = {r["key"] for r in results}
    assert "PROJ-2" in keys
    assert "PROJ-3" in keys
