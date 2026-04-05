"""Configuration loaded from environment variables."""
import os
from pathlib import Path

# Repository root — two levels up from this file (sdk-agents/agentic-test-creator/)
REPO_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = REPO_ROOT / "agents" / "agentic-test-creator"


class Config:
    jira_base_url: str = os.getenv("JIRA_BASE_URL", "")
    jira_email: str = os.getenv("JIRA_EMAIL", "")
    jira_api_token: str = os.getenv("JIRA_API_TOKEN", "")
    webhook_secret: str = os.getenv("WEBHOOK_SECRET", "")
    max_agent_turns: int = int(os.getenv("MAX_AGENT_TURNS", "25"))
    webhook_port: int = int(os.getenv("WEBHOOK_PORT", "8080"))


config = Config()
