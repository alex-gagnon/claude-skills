# pages/home_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage


class HomePage(BasePage):
    """Encapsulates all interactions and assertions on the home page (/)."""

    PATH = "/"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading: Locator = page.get_by_role("heading", name="Welcome to Portside Behavior Consulting")
        self.book_consultation_link: Locator = page.get_by_role("link", name="Book a Consultation")
        self.testimonials_section: Locator = page.get_by_role("blockquote")

    def navigate(self) -> None:  # type: ignore[override]
        super().navigate(self.PATH)

    def expect_title(self) -> None:
        expect(self.page).to_have_title("Portside Behavior Consulting")

    def expect_heading_visible(self) -> None:
        expect(self.heading).to_be_visible()

    def expect_book_consultation_link_visible(self) -> None:
        expect(self.book_consultation_link).to_be_visible()

    def click_book_consultation(self) -> None:
        self.book_consultation_link.click()

    def expect_at_least_two_testimonials(self) -> None:
        """Assert that at least 2 client testimonial quotes are present."""
        count = self.testimonials_section.count()
        assert count >= 2, f"Expected at least 2 testimonials, found {count}"
