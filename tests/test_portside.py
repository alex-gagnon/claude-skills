# test_portside.py
# Framework: Playwright Python — Page Object Model
# Template: playwright-templates.md
import pytest
from playwright.sync_api import Page, expect

from pages.home_page import HomePage
from pages.services_page import ServicesPage
from pages.contact_page import ContactPage
from pages.success_page import SuccessPage


class TestHomePage:
    """Tests for the Portside Behavior Consulting home page (/)."""

    # QA: The page title must be "Portside Behavior Consulting"
    # QA: An <h1> heading "Welcome to Portside Behavior Consulting" must be visible
    # QA: A "Book a Consultation" link must be visible and must navigate to /contact when clicked
    # QA: A testimonials section with at least 2 client quotes must be present
    def test_home_page_content_and_navigation(self, page: Page) -> None:
        """
        Source: QA AC — Home page (all criteria)
        Verifies: Page title, h1 heading, Book a Consultation link visibility and navigation,
                  and presence of at least 2 testimonial quotes.
        All assertions share the same starting URL, so they are combined in one method.
        """
        home = HomePage(page)
        home.navigate()

        # Title check
        home.expect_title()

        # H1 heading visible
        home.expect_heading_visible()

        # "Book a Consultation" link is visible
        home.expect_book_consultation_link_visible()

        # At least 2 testimonials present
        home.expect_at_least_two_testimonials()

        # Clicking "Book a Consultation" navigates to /contact
        home.click_book_consultation()
        expect(page).to_have_url("**/contact")


class TestServicesPage:
    """Tests for the /services page."""

    # QA: The page must show an <h1> "Our Services"
    # QA: Exactly 3 service cards must be listed
    # QA: Each card must display a price
    # QA: Each card must have a "Book Now" link that navigates to /contact
    def test_services_page_content_and_cards(self, page: Page) -> None:
        """
        Source: QA AC — Services page (all criteria)
        Verifies: h1 heading, exactly 3 service cards, each card shows a price,
                  each card has a Book Now link pointing to /contact.
        All assertions share the same starting URL, so they are combined in one method.
        """
        services = ServicesPage(page)
        services.navigate()

        # H1 heading visible
        services.expect_heading_visible()

        # Exactly 3 service cards
        services.expect_exactly_three_service_cards()

        # Each card displays a price
        services.expect_each_card_displays_price()

        # Each card has a "Book Now" link to /contact
        services.expect_each_card_has_book_now_link_to_contact()


class TestContactPage:
    """Tests for the /contact page."""

    # QA: A form with labeled fields for: Full Name, Email Address, Phone Number,
    #     Service of Interest (dropdown), Dog's Name, Dog's Breed, Additional Notes
    def test_contact_form_fields_are_present(self, page: Page) -> None:
        """
        Source: QA AC — Contact page, form fields
        Verifies: All seven labeled form fields are visible on the contact page.
        """
        contact = ContactPage(page)
        contact.navigate()
        contact.expect_all_form_fields_present()

    # QA: Entering an invalid email address and leaving the field must show an inline error alert
    def test_invalid_email_shows_inline_error(self, page: Page) -> None:
        """
        Source: QA AC — Contact page, email validation
        Verifies: Entering an invalid email and blurring the field surfaces an inline error alert.
        """
        contact = ContactPage(page)
        contact.navigate()
        contact.enter_invalid_email_and_blur("this-is-not-an-email")
        contact.expect_email_error_visible()

    # QA: Submitting the fully filled form must redirect the browser to /contact/success
    def test_fully_filled_form_redirects_to_success(self, page: Page) -> None:
        """
        Source: QA AC — Contact page, form submission
        Verifies: Submitting a fully filled, valid form redirects the user to /contact/success.
        """
        contact = ContactPage(page)
        contact.navigate()
        contact.fill_full_form()
        contact.submit_form()
        expect(page).to_have_url("**/contact/success")


class TestSuccessPage:
    """Tests for the /contact/success page."""

    # QA: An <h1> "Thank You!" must be visible
    # QA: Text containing "We'll be in touch within 1" must be visible
    # QA: A "Return to Home" link must navigate back to /
    def test_success_page_content_and_return_home_navigation(self, page: Page) -> None:
        """
        Source: QA AC — Success page (all criteria)
        Verifies: "Thank You!" heading visible, response-time message present,
                  and Return to Home link navigates back to /.
        All assertions share the same starting URL, so they are combined in one method.
        """
        success = SuccessPage(page)
        success.navigate()

        # "Thank You!" h1 visible
        success.expect_thank_you_heading_visible()

        # "We'll be in touch within 1" text visible
        success.expect_in_touch_text_visible()

        # "Return to Home" link is visible
        success.expect_return_home_link_visible()

        # Clicking "Return to Home" navigates back to /
        success.click_return_home()
        expect(page).to_have_url("**/")
