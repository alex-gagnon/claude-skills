"""
FastAPI webhook server — receives Jira and GitHub events and triggers the
agentic test creator autonomously.

Start with:
    uvicorn webhook:app --host 0.0.0.0 --port 8080

Supported events:
    Jira:   issue_created (issuetype: Story, Epic)
    GitHub: pull_request (action: opened, synchronize)
"""
from __future__ import annotations

import hashlib
import hmac
import logging
import re
import threading
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from agent import create_tests, detect_framework
from config import config
from inputs import JiraFetcher, build_pr_context, InputMode

log = logging.getLogger("webhook")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = FastAPI(title="agentic-test-creator webhook", version="1.0.0")

# ---------------------------------------------------------------------------
# Signature verification
# ---------------------------------------------------------------------------

def _verify_github_signature(payload: bytes, signature_header: str | None) -> bool:
    if not config.webhook_secret:
        return True  # no secret configured → skip verification
    if not signature_header:
        return False
    algorithm, _, sig = signature_header.partition("=")
    mac = hmac.new(config.webhook_secret.encode(), payload, hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), sig)


def _verify_jira_signature(payload: bytes, signature_header: str | None) -> bool:
    """Jira uses HMAC-SHA256 in a custom header."""
    if not config.webhook_secret:
        return True
    if not signature_header:
        return False
    expected = hmac.new(config.webhook_secret.encode(), payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature_header.lstrip("sha256="))


# ---------------------------------------------------------------------------
# Background runner
# ---------------------------------------------------------------------------

def _run_in_background(context_fn, framework: str, output_dir: str) -> None:
    """Fetch context and run the agent in a daemon thread."""
    def _task():
        try:
            ctx = context_fn()
            log.info("Starting agent: source=%s framework=%s output=%s", ctx.raw, framework, output_dir)
            result = create_tests(ctx, framework, output_dir, stream_output=False)
            log.info("Agent finished for %s:\n%s", ctx.raw, result[-500:] if result else "(no output)")
        except Exception as exc:
            log.error("Agent failed: %s", exc, exc_info=True)

    t = threading.Thread(target=_task, daemon=True)
    t.start()


def _resolve_framework(output_dir: str, default: str = "playwright") -> str:
    detected = detect_framework(output_dir)
    return detected or default


# ---------------------------------------------------------------------------
# Jira webhook
# ---------------------------------------------------------------------------

@app.post("/webhooks/jira")
async def jira_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
):
    body = await request.body()
    if not _verify_jira_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: dict[str, Any] = await request.json()
    event_type = payload.get("webhookEvent", "")
    issue = payload.get("issue", {})
    issue_key = issue.get("key")
    issue_type = issue.get("fields", {}).get("issuetype", {}).get("name", "").lower()

    if not issue_key:
        return JSONResponse({"status": "ignored", "reason": "no issue key"})

    # Only react to story and epic creation
    if event_type not in ("jira:issue_created", "jira:issue_updated"):
        return JSONResponse({"status": "ignored", "event": event_type})
    if issue_type not in ("story", "epic", "task"):
        return JSONResponse({"status": "ignored", "issue_type": issue_type})

    output_dir = str(Path("tests/e2e").resolve())
    framework = _resolve_framework(output_dir)

    fetcher = JiraFetcher()
    _run_in_background(
        lambda key=issue_key: fetcher.build_context(key),
        framework,
        output_dir,
    )
    log.info("Queued agent run for Jira issue %s", issue_key)
    return JSONResponse({"status": "accepted", "issue": issue_key, "framework": framework})


# ---------------------------------------------------------------------------
# GitHub webhook
# ---------------------------------------------------------------------------

@app.post("/webhooks/github")
async def github_webhook(
    request: Request,
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
):
    body = await request.body()
    if not _verify_github_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload: dict[str, Any] = await request.json()
    action = payload.get("action", "")
    pr = payload.get("pull_request", {})
    pr_number = str(pr.get("number", ""))

    if x_github_event != "pull_request":
        return JSONResponse({"status": "ignored", "event": x_github_event})
    if action not in ("opened", "synchronize"):
        return JSONResponse({"status": "ignored", "action": action})
    if not pr_number:
        return JSONResponse({"status": "ignored", "reason": "no PR number"})

    output_dir = str(Path("tests").resolve())
    framework = _resolve_framework(output_dir)

    _run_in_background(
        lambda num=pr_number: build_pr_context(num),
        framework,
        output_dir,
    )
    log.info("Queued agent run for GitHub PR #%s", pr_number)
    return JSONResponse({"status": "accepted", "pr": pr_number, "framework": framework})


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok"}
