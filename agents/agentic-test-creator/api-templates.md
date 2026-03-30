# REST API Test Templates

Reference these patterns when generating REST API tests in Python using `pytest` and `requests`.

---

## 1. Basic Test Function Pattern

```python
import pytest
import requests


def test_descriptive_behavior_name(base_url, auth_headers):
    """
    Source: <Jira key AC-N | PR #N | QA: original AC text>
    Verifies: <brief one-line description of the behavior under test>
    """
    response = requests.post(
        f"{base_url}/api/endpoint",
        json={"key": "value"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "expected_field" in data
```

---

## 2. conftest.py — base_url and auth_token Fixtures

```python
# conftest.py
import os
import pytest
import requests


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the API under test."""
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def auth_token(base_url: str) -> str:
    """
    Obtain a bearer token by logging in once per test session.
    Reads credentials from environment variables.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={
            "email": os.environ.get("TEST_USER_EMAIL", "user@example.com"),
            "password": os.environ.get("TEST_USER_PASSWORD", "ValidPass123!"),
        },
    )
    assert response.status_code == 200, f"Login failed: {response.text}"
    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(auth_token: str) -> dict:
    """Return HTTP headers containing the Authorization bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}
```

---

## 3. Auth Header Helper

```python
def make_auth_headers(token: str) -> dict:
    """Build a headers dict with a bearer token for authenticated requests."""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
```

---

## 4. Assertion Patterns

```python
# Status code
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 400
assert response.status_code == 401
assert response.status_code == 404

# Field presence in JSON body
data = response.json()
assert "access_token" in data
assert "user" in data
assert data["user"]["email"] == "user@example.com"

# Nested field
assert data["user"]["role"] == "admin"

# List response
assert isinstance(data["items"], list)
assert len(data["items"]) > 0

# Error message shape
assert "error" in data
assert "message" in data["error"]

# Content-Type header
assert "application/json" in response.headers["Content-Type"]

# Response time (optional performance check)
assert response.elapsed.total_seconds() < 2.0
```

---

## 5. Parametrize Pattern — Testing Multiple Inputs

```python
import pytest
import requests


@pytest.mark.parametrize("email,password,expected_status", [
    ("user@example.com", "ValidPass123!", 200),
    ("user@example.com", "wrongpassword", 401),
    ("notanemail", "ValidPass123!", 400),
    ("", "ValidPass123!", 400),
    ("user@example.com", "", 400),
])
def test_login_input_validation(base_url, email, password, expected_status):
    """
    Source: QA AC — login endpoint validates inputs and returns correct status codes.
    Verifies: The /auth/login endpoint returns the correct HTTP status for each input combination.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == expected_status
```

---

## 6. Complete Example — Login API

```python
# test_login_api.py
import pytest
import requests


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

def test_valid_credentials_return_access_token(base_url):
    """
    Source: QA AC-1
    Verifies: POST /auth/login with valid credentials returns HTTP 200 and a non-empty access_token.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "user@example.com", "password": "ValidPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_response_includes_user_object(base_url):
    """
    Source: QA AC-2
    Verifies: A successful login response body contains a user object with id and email fields.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "user@example.com", "password": "ValidPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "id" in data["user"]
    assert "email" in data["user"]
    assert data["user"]["email"] == "user@example.com"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_invalid_password_returns_401(base_url):
    """
    Source: QA AC-3
    Verifies: POST /auth/login with a wrong password returns HTTP 401.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "user@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    data = response.json()
    assert "error" in data or "message" in data


def test_unknown_email_returns_401(base_url):
    """
    Source: QA AC-4
    Verifies: POST /auth/login with an unrecognised email returns HTTP 401.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "nobody@example.com", "password": "ValidPass123!"},
    )
    assert response.status_code == 401


def test_missing_email_field_returns_400(base_url):
    """
    Source: QA AC-5
    Verifies: POST /auth/login without the email field returns HTTP 400.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"password": "ValidPass123!"},
    )
    assert response.status_code == 400


def test_missing_password_field_returns_400(base_url):
    """
    Source: QA AC-6
    Verifies: POST /auth/login without the password field returns HTTP 400.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "user@example.com"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# Schema check
# ---------------------------------------------------------------------------

def test_successful_login_response_schema(base_url):
    """
    Source: QA AC-7
    Verifies: The login response body conforms to the expected schema.
    """
    response = requests.post(
        f"{base_url}/auth/login",
        json={"email": "user@example.com", "password": "ValidPass123!"},
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("Content-Type", "")

    data = response.json()
    # Top-level keys
    assert set(data.keys()) >= {"access_token", "token_type", "user"}
    # Token type
    assert data["token_type"].lower() == "bearer"
    # User sub-object keys
    assert set(data["user"].keys()) >= {"id", "email", "role"}
```
