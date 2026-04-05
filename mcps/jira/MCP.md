---
name: jira
version: 1.0.0
description: MCP server that exposes Jira epics and stories as callable tools for test generation agents.
tags: [testing]
---

## Overview

The `jira` MCP server connects Claude Code agents to a Jira Cloud project via the Jira REST API v3. It exposes four tools that let agents fetch epics, list stories, retrieve full story details, and run arbitrary JQL searches. This enables test generation workflows to pull acceptance criteria and labels directly from Jira without manual copy-paste.

## Prerequisites

- Python 3.11+
- A Jira Cloud account with API token access
- `pip install -r server/requirements.txt`

## Setup

1. Copy the example environment file and fill in your credentials:

```bash
cp mcps/jira/server/.env.example mcps/jira/server/.env
```

2. Edit `mcps/jira/server/.env`:

```
JIRA_BASE_URL=https://your-org.atlassian.net
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token-here
```

3. Install dependencies:

```bash
cd mcps/jira/server
pip install -r requirements.txt
```

4. Run the MCP server:

```bash
python server.py
```

5. Register it in your Claude Code `settings.json` under `mcpServers`:

```json
{
  "mcpServers": {
    "jira": {
      "command": "python",
      "args": ["/absolute/path/to/mcps/jira/server/server.py"],
      "env": {
        "JIRA_BASE_URL": "https://your-org.atlassian.net",
        "JIRA_EMAIL": "your-email@example.com",
        "JIRA_API_TOKEN": "your-api-token-here"
      }
    }
  }
}
```

## Tools

| Tool | Signature | Description |
|------|-----------|-------------|
| `get_epic` | `(epic_key: str) -> dict` | Fetch epic title, description, linked story keys, and status |
| `list_stories` | `(epic_key: str) -> list[dict]` | List all stories in an epic with summary, acceptance_criteria, priority, labels, and status |
| `get_story` | `(story_key: str) -> dict` | Full story detail: summary, acceptance_criteria, priority, labels, status, story_points |
| `search_issues` | `(jql: str) -> list[dict]` | Execute a JQL query returning key, summary, status, priority, and labels per issue |

## Usage Examples

**Fetch an epic to understand scope:**
```
Use the jira tool to get_epic("PROJ-42") and then list_stories("PROJ-42") so I can generate acceptance tests.
```

**Get full story detail before writing tests:**
```
Call get_story("PROJ-55") and generate pytest test cases covering each acceptance criterion.
```

**Search for high-priority open bugs:**
```
Run search_issues("project = PROJ AND issuetype = Bug AND priority = High AND status != Done") and summarize what needs test coverage.
```

**End-to-end test generation workflow:**
```
1. Call get_epic("PROJ-10") to get the epic and its child story keys
2. Call list_stories("PROJ-10") to retrieve acceptance criteria for all stories
3. Generate a pytest test file with one test function per acceptance criterion
```

## Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `JIRA_BASE_URL` | Yes | Base URL of your Jira Cloud instance, e.g. `https://your-org.atlassian.net` |
| `JIRA_EMAIL` | Yes | Email address associated with the Jira account |
| `JIRA_API_TOKEN` | Yes | API token generated from https://id.atlassian.com/manage-profile/security/api-tokens |

The server uses HTTP Basic Auth with email + API token as required by Jira Cloud REST API v3. API tokens are scoped to the generating user's permissions — ensure the account has read access to the relevant Jira projects.
