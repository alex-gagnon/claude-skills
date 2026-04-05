# pages/contact_page.py
from playwright.sync_api import Page, Locator, expect
from .base_page import BasePage


class ContactPage(BasePage):
    """Encapsulates all interactions and assertions on the /contact page."""

    PATH = "/contact"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.full_name_input: Locator = page.get_by_label("Full Name")
        self.email_input: Locator = page.get_by_label("Email Address")
        self.phone_input: Locator = page.get_by_label("Phone Number")
        self.service_dropdown: Locator = page.get_by_label("Service of Interest")
        self.dog_name_input: Locator = page.get_by_label("Dog's Name")
        self.dog_breed_input: Locator = page.get_by_label("Dog's Breed")
        self.additional_notes_input: Locator = page.get_by_label("Additional Notes")
        self.submit_button: Locator = page.get_by_role("button", name="Submit")
        self.email_error_alert: Locator = page.get_by_role("alert")

    def navigate(self) -> None:  # type: ignore[override]
        super().navigate(self.PATH)

    def expect_all_form_fields_present(self) -> None:
        """Assert that all labeled form fields are visible on the page."""
        expect(self.full_name_input).to_be_visible()
        expect(self.email_input).to_be_visible()
        expect(self.phone_input).to_be_visible()
        expect(self.service_dropdown).to_be_visible()
        expect(self.dog_name_input).to_be_visible()
        expect(self.dog_breed_input).to_be_visible()
        expect(self.additional_notes_input).to_be_visible()

    def enter_invalid_email_and_blur(self, invalid_email: str = "not-an-email") -> None:
        """Type an invalid email into the email field then move focus away to trigger inline validation."""
        self.email_input.fill(invalid_email)
        # Blur by clicking the Full Name field
        self.full_name_input.click()

    def expect_email_error_visible(self) -> None:
        """Assert that an inline validation alert is visible after invalid email entry."""
        expect(self.email_error_alert).to_be_visible()

    def fill_full_form(
        self,
        full_name: str = "Jane Smith",
        email: str = "jane.smith@example.com",
        phone: str = "555-867-5309",
        dog_name: str = "Biscuit",
        dog_breed: str = "Labrador Retriever",
        notes: str = "Leash pulling and jumping.",
    ) -> None:
        """Fill every form field with valid data."""
        self.full_name_input.fill(full_name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)
        # Select the first non-placeholder option in the dropdown
        self.service_dropdown.select_option(index=1)
        self.dog_name_input.fill(dog_name)
        self.dog_breed_input.fill(dog_breed)
        self.additional_notes_input.fill(notes)

    def submit_form(self) -> None:
        self.submit_button.click()
