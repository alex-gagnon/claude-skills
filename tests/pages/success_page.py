# pages/success_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage


class SuccessPage(BasePage):
    """Encapsulates all assertions on the /contact/success page."""

    PATH = "/contact/success"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.thank_you_heading: Locator = page.get_by_role("heading", name="Thank You!")
        self.in_touch_text: Locator = page.get_by_text("We'll be in touch within 1", exact=False)
        self.return_home_link: Locator = page.get_by_role("link", name="Return to Home")

    def navigate(self) -> None:  # type: ignore[override]
        super().navigate(self.PATH)

    def expect_thank_you_heading_visible(self) -> None:
        expect(self.thank_you_heading).to_be_visible()

    def expect_in_touch_text_visible(self) -> None:
        expect(self.in_touch_text).to_be_visible()

    def expect_return_home_link_visible(self) -> None:
        expect(self.return_home_link).to_be_visible()

    def click_return_home(self) -> None:
        self.return_home_link.click()
