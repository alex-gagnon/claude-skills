"""Pytest configuration and shared fixtures for the Jira MCP server tests."""

from __future__ import annotations

import os
import sys
import threading
import time

import httpx
import pytest
import uvicorn

# Ensure the server package is importable regardless of where pytest is invoked.
_SERVER_DIR = os.path.join(os.path.dirname(__file__), "..")
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

_TESTS_DIR = os.path.dirname(__file__)
if _TESTS_DIR not in sys.path:
    sys.path.insert(0, _TESTS_DIR)

from jira_client import JiraClient  # noqa: E402 — must come after sys.path tweak
from mock_jira_server import app as mock_app  # noqa: E402


_MOCK_HOST = "127.0.0.1"
_MOCK_PORT = 8765
_MOCK_BASE_URL = f"http://{_MOCK_HOST}:{_MOCK_PORT}"
_PROBE_URL = f"{_MOCK_BASE_URL}/rest/api/3/issue/PROJ-1"
_STARTUP_TIMEOUT = 10  # seconds


class _UvicornServer(uvicorn.Server):
    """Uvicorn server subclass that can be stopped from another thread."""

    def install_signal_handlers(self) -> None:  # type: ignore[override]
        # Disable signal handlers so the server can run in a background thread.
        pass


@pytest.fixture(scope="session")
def mock_server():
    """Start the FastAPI mock Jira server in a background thread for the test session.

    Yields after the server is confirmed ready, then shuts it down.
    """
    config = uvicorn.Config(
        app=mock_app,
        host=_MOCK_HOST,
        port=_MOCK_PORT,
        log_level="warning",
    )
    server = _UvicornServer(config=config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Poll until the server responds or we time out.
    deadline = time.monotonic() + _STARTUP_TIMEOUT
    last_exc: Exception = RuntimeError("Mock server never started")
    while time.monotonic() < deadline:
        try:
            resp = httpx.get(_PROBE_URL, timeout=1.0)
            if resp.status_code < 500:
                break
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
        time.sleep(0.1)
    else:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError(f"Mock Jira server failed to start: {last_exc}") from last_exc

    yield

    server.should_exit = True
    thread.join(timeout=5)


@pytest.fixture()
def jira_client(mock_server):  # noqa: ARG001 — ensures server is running
    """Return a JiraClient pointed at the local mock server."""
    os.environ["JIRA_BASE_URL"] = _MOCK_BASE_URL
    os.environ["JIRA_EMAIL"] = "test@test.com"
    os.environ["JIRA_API_TOKEN"] = "test"

    return JiraClient(
        base_url=_MOCK_BASE_URL,
        email="test@test.com",
        api_token="test",
    )
