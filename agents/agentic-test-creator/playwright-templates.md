# Playwright Python Templates

Reference these patterns when generating Playwright E2E tests in Python using `playwright.sync_api`.

---

## 1. Basic Test Function Pattern

```python
import pytest
from playwright.sync_api import Page, expect


def test_descriptive_behavior_name(page: Page):
    """
    Source: <Jira key AC-N | PR #N | QA: original AC text>
    Verifies: <brief one-line description of the behavior under test>
    """
    page.goto("/target-path")
    page.get_by_role("button", name="Submit").click()
    expect(page).to_have_url("/expected-path")
```

---

## 2. conftest.py — base_url and page Fixture

```python
# conftest.py
import pytest
from playwright.sync_api import Playwright, BrowserContext, Page


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the application under test."""
    return "http://localhost:3000"


@pytest.fixture(scope="session")
def browser_context(playwright: Playwright):
    """Create a single browser context shared across the test session."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    yield context
    context.close()
    browser.close()


@pytest.fixture()
def page(browser_context: BrowserContext, base_url: str) -> Page:
    """Open a new page and navigate to the base URL before each test."""
    p = browser_context.new_page()
    p.goto(base_url)
    yield p
    p.close()
```

---

## 3. Login Flow Helper — Authenticated State Fixture

```python
# conftest.py (add to existing conftest.py)
import os
import pytest
from playwright.sync_api import BrowserContext, Page


@pytest.fixture(scope="session")
def auth_state(browser_context: BrowserContext, base_url: str):
    """
    Perform login once per session and store browser state.
    Reuse this fixture in any test that requires an authenticated user.
    """
    page = browser_context.new_page()
    page.goto(f"{base_url}/login")
    page.get_by_label("Email").fill(os.environ.get("TEST_USER_EMAIL", "user@example.com"))
    page.get_by_label("Password").fill(os.environ.get("TEST_USER_PASSWORD", "ValidPass123!"))
    page.get_by_role("button", name="Log in").click()
    page.wait_for_url("**/dashboard")
    storage = browser_context.storage_state()
    page.close()
    return storage


@pytest.fixture()
def authenticated_page(playwright, base_url: str, auth_state) -> Page:
    """Return a page already logged in via stored auth state."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(storage_state=auth_state, base_url=base_url)
    page = context.new_page()
    yield page
    context.close()
    browser.close()
```

---

## 4. Locator Strategies

Prefer these locators in the following order:

```python
# 1. By role (most robust — matches accessible name)
page.get_by_role("button", name="Submit")
page.get_by_role("textbox", name="Search")
page.get_by_role("link", name="Sign up")
page.get_by_role("heading", name="Welcome")

# 2. By label (for form inputs)
page.get_by_label("Email")
page.get_by_label("Password")

# 3. By visible text content
page.get_by_text("Success! Your order was placed.")
page.get_by_text("Invalid credentials", exact=True)

# 4. By placeholder (when no label is present)
page.get_by_placeholder("Search for products...")

# 5. By test ID (when the app exposes data-testid attributes)
page.get_by_test_id("submit-button")

# Avoid CSS selectors and XPath unless none of the above work:
# page.locator("button.submit-btn")       # CSS — last resort
# page.locator("//button[@type='submit']") # XPath — avoid
```

---

## 5. Assertion Patterns

```python
from playwright.sync_api import Page, expect

# Page-level assertions
expect(page).to_have_url("/dashboard")
expect(page).to_have_url("https://example.com/dashboard")
expect(page).to_have_title("Dashboard — MyApp")

# Locator-level assertions
locator = page.get_by_role("alert")
expect(locator).to_be_visible()
expect(locator).to_be_hidden()
expect(locator).to_contain_text("Invalid credentials")
expect(locator).to_have_text("Invalid credentials")  # exact match
expect(locator).to_have_value("user@example.com")    # for inputs
expect(locator).to_be_enabled()
expect(locator).to_be_disabled()
expect(locator).to_be_checked()                      # for checkboxes/radios

# Count assertion
expect(page.get_by_role("listitem")).to_have_count(5)
```

---

## 6. Complete Example — Login Feature

```python
# test_login.py
import pytest
from playwright.sync_api import Page, expect


def test_valid_credentials_redirect_to_dashboard(page: Page):
    """
    Source: QA AC-1
    Verifies: A user with valid credentials is redirected to /dashboard after login.
    """
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_label("Password").fill("ValidPass123!")
    page.get_by_role("button", name="Log in").click()
    expect(page).to_have_url("/dashboard")


def test_invalid_password_shows_error_alert(page: Page):
    """
    Source: QA AC-2
    Verifies: An incorrect password causes a visible error alert to appear.
    """
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_label("Password").fill("wrongpassword")
    page.get_by_role("button", name="Log in").click()
    expect(page.get_by_role("alert")).to_be_visible()
    expect(page.get_by_role("alert")).to_contain_text("Invalid credentials")


def test_empty_email_field_keeps_user_on_login_page(page: Page):
    """
    Source: QA AC-3
    Verifies: Submitting the login form without an email keeps the user on /login.
    """
    page.goto("/login")
    page.get_by_label("Password").fill("SomePassword1!")
    page.get_by_role("button", name="Log in").click()
    expect(page).to_have_url("/login")
```
