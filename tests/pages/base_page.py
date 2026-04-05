# pages/base_page.py
from playwright.sync_api import Page, expect


class BasePage:
    """Base class for all page objects. Wraps a Playwright Page instance."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def navigate(self, path: str = "/") -> None:
        """Navigate to a path relative to the application root."""
        self.page.goto(path)

    def wait_for_url(self, pattern: str) -> None:
        """Wait until the current URL matches the given glob or regex pattern."""
        self.page.wait_for_url(pattern)

    def reload(self) -> None:
        self.page.reload()
