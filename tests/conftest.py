# conftest.py
import os
import pytest
from playwright.sync_api import Playwright, BrowserContext, Page


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://127.0.0.1:5001")


@pytest.fixture(scope="session")
def browser_context(playwright: Playwright, base_url: str) -> BrowserContext:
    """Single browser context shared across the test session."""
    browser = playwright.chromium.launch(
        headless=True,
        executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    )
    context = browser.new_context(base_url=base_url)
    yield context
    context.close()
    browser.close()


@pytest.fixture()
def page(browser_context: BrowserContext) -> Page:
    """Fresh page per test; closed automatically after the test."""
    p = browser_context.new_page()
    yield p
    p.close()
