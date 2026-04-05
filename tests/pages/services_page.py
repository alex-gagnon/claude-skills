# pages/services_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage


class ServicesPage(BasePage):
    """Encapsulates all interactions and assertions on the /services page."""

    PATH = "/services"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.heading: Locator = page.get_by_role("heading", name="Our Services")
        # Service cards are expected to carry a common class or landmark;
        # falling back to a CSS selector scoped to an article or section role.
        self.service_cards: Locator = page.locator(".service-card")

    def navigate(self) -> None:  # type: ignore[override]
        super().navigate(self.PATH)

    def expect_heading_visible(self) -> None:
        expect(self.heading).to_be_visible()

    def expect_exactly_three_service_cards(self) -> None:
        """Assert that exactly 3 service cards are rendered."""
        expect(self.service_cards).to_have_count(3)

    def expect_each_card_displays_price(self) -> None:
        """Assert that every service card contains price text (e.g. '$')."""
        card_count = self.service_cards.count()
        for i in range(card_count):
            card = self.service_cards.nth(i)
            # Prices are expected to contain a currency symbol
            price_locator = card.locator("text=/$|price|\\$/i")
            # Use a broader assertion: card text must contain a dollar sign
            card_text = card.inner_text()
            assert "$" in card_text, f"Service card {i + 1} does not display a price (no '$' found)"

    def expect_each_card_has_book_now_link_to_contact(self) -> None:
        """Assert that every service card has a 'Book Now' link pointing to /contact."""
        card_count = self.service_cards.count()
        for i in range(card_count):
            card = self.service_cards.nth(i)
            book_now = card.get_by_role("link", name="Book Now")
            expect(book_now).to_be_visible()
            href = book_now.get_attribute("href")
            assert href is not None and "/contact" in href, (
                f"Service card {i + 1} 'Book Now' link href '{href}' does not point to /contact"
            )
