# REST API Test Templates — Service Object Pattern

Reference these patterns when generating REST API tests in Python using `pytest` and `requests`.
Tests follow the **Service Object pattern** — API clients are classes, not bare `requests.get()` calls.

---

## Directory Structure

```
tests/
├── conftest.py
├── clients/
│   ├── __init__.py
│   ├── base_client.py
│   └── auth_client.py
├── schemas/
│   ├── __init__.py
│   └── auth_schema.py
└── test_login_api.py
```

---

## 1. BaseClient Class

```python
# clients/base_client.py
import requests
from requests import Response, Session


class BaseClient:
    """Base HTTP client. Subclass per service/domain (auth, users, orders, etc.)."""

    def __init__(self, base_url: str, headers: dict | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.session: Session = requests.Session()
        if headers:
            self.session.headers.update(headers)

    def get(self, path: str, **kwargs) -> Response:
        return self.session.get(f"{self.base_url}{path}", **kwargs)

    def post(self, path: str, **kwargs) -> Response:
        return self.session.post(f"{self.base_url}{path}", **kwargs)

    def put(self, path: str, **kwargs) -> Response:
        return self.session.put(f"{self.base_url}{path}", **kwargs)

    def patch(self, path: str, **kwargs) -> Response:
        return self.session.patch(f"{self.base_url}{path}", **kwargs)

    def delete(self, path: str, **kwargs) -> Response:
        return self.session.delete(f"{self.base_url}{path}", **kwargs)

    def set_auth_token(self, token: str) -> None:
        """Inject a bearer token into all subsequent requests from this client."""
        self.session.headers.update({"Authorization": f"Bearer {token}"})
```

---

## 2. Service Client — AuthClient

```python
# clients/auth_client.py
from requests import Response
from .base_client import BaseClient


class AuthClient(BaseClient):
    """Client for all /auth endpoints."""

    def login(self, email: str, password: str) -> Response:
        """POST /auth/login — returns the raw response for assertion."""
        return self.post("/auth/login", json={"email": email, "password": password})

    def login_and_get_token(self, email: str, password: str) -> str:
        """Log in and return the access_token string. Raises on non-200."""
        response = self.login(email, password)
        response.raise_for_status()
        return response.json()["access_token"]

    def logout(self, token: str) -> Response:
        """POST /auth/logout with the given bearer token."""
        return self.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})

    def refresh(self, refresh_token: str) -> Response:
        """POST /auth/refresh with a refresh token."""
        return self.post("/auth/refresh", json={"refresh_token": refresh_token})
```

---

## 3. Schema Validation — TypedDict / Dataclass

```python
# schemas/auth_schema.py
from typing import TypedDict


class UserSchema(TypedDict):
    id: str
    email: str
    role: str


class LoginResponseSchema(TypedDict):
    access_token: str
    token_type: str
    user: UserSchema


def assert_login_response_schema(data: dict) -> None:
    """Assert the login response matches the expected schema."""
    assert set(data.keys()) >= {"access_token", "token_type", "user"}, (
        f"Missing top-level keys. Got: {list(data.keys())}"
    )
    assert data["token_type"].lower() == "bearer"
    assert isinstance(data["access_token"], str) and len(data["access_token"]) > 0

    user = data["user"]
    assert set(user.keys()) >= {"id", "email", "role"}, (
        f"Missing user keys. Got: {list(user.keys())}"
    )
```

---

## 4. conftest.py — Fixtures

```python
# conftest.py
import os
import pytest
from clients.auth_client import AuthClient


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("API_BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def auth_client(base_url: str) -> AuthClient:
    """Unauthenticated auth client — use for login/registration tests."""
    return AuthClient(base_url=base_url)


@pytest.fixture(scope="session")
def authenticated_client(base_url: str) -> AuthClient:
    """Auth client pre-loaded with a valid bearer token for the session."""
    client = AuthClient(base_url=base_url)
    token = client.login_and_get_token(
        email=os.environ.get("TEST_USER_EMAIL", "user@example.com"),
        password=os.environ.get("TEST_USER_PASSWORD", "ValidPass123!"),
    )
    client.set_auth_token(token)
    return client
```

---

## 5. Assertion Patterns

```python
# Status codes
assert response.status_code == 200
assert response.status_code == 201
assert response.status_code == 400
assert response.status_code == 401
assert response.status_code == 403
assert response.status_code == 404

# JSON body — field presence
data = response.json()
assert "access_token" in data
assert "user" in data

# Nested fields
assert data["user"]["email"] == "user@example.com"
assert data["user"]["role"] == "admin"

# Types
assert isinstance(data["access_token"], str)
assert isinstance(data["items"], list)
assert len(data["items"]) > 0

# Error shape
assert "error" in data or "message" in data

# Headers
assert "application/json" in response.headers.get("Content-Type", "")

# Response time
assert response.elapsed.total_seconds() < 2.0
```

---

## 6. Parametrize Pattern

```python
import pytest
from clients.auth_client import AuthClient


@pytest.mark.parametrize("email,password,expected_status", [
    ("user@example.com", "ValidPass123!", 200),
    ("user@example.com", "wrongpassword",  401),
    ("notanemail",       "ValidPass123!", 400),
    ("",                 "ValidPass123!", 400),
    ("user@example.com", "",              400),
])
class TestLoginInputValidation:
    def test_login_status_code(
        self, auth_client: AuthClient, email, password, expected_status
    ):
        """
        Source: QA AC — /auth/login validates all input combinations.
        Verifies: Correct HTTP status for each email/password combination.
        """
        response = auth_client.login(email, password)
        assert response.status_code == expected_status, (
            f"Expected {expected_status} for ({email!r}, {password!r}), "
            f"got {response.status_code}: {response.text}"
        )
```

---

## 7. Complete Example — Login API (Service Object Pattern)

```python
# test_login_api.py
import pytest
from clients.auth_client import AuthClient
from schemas.auth_schema import assert_login_response_schema


class TestLoginHappyPath:
    """QA AC-1, AC-2: Successful login returns token and user object."""

    def test_valid_credentials_return_access_token(self, auth_client: AuthClient):
        """
        Source: QA AC-1
        Verifies: POST /auth/login with valid credentials returns HTTP 200 and a non-empty access_token.
        """
        response = auth_client.login("user@example.com", "ValidPass123!")
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_response_includes_user_object(self, auth_client: AuthClient):
        """
        Source: QA AC-2
        Verifies: A successful login response body contains a user object with id and email.
        """
        response = auth_client.login("user@example.com", "ValidPass123!")
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "id" in data["user"]
        assert data["user"]["email"] == "user@example.com"

    def test_login_response_conforms_to_schema(self, auth_client: AuthClient):
        """
        Source: QA AC-3
        Verifies: The login response body conforms to the LoginResponseSchema.
        """
        response = auth_client.login("user@example.com", "ValidPass123!")
        assert response.status_code == 200
        assert_login_response_schema(response.json())


class TestLoginErrorCases:
    """QA AC-4 through AC-6: Authentication errors return correct status codes."""

    def test_invalid_password_returns_401(self, auth_client: AuthClient):
        """
        Source: QA AC-4
        Verifies: POST /auth/login with a wrong password returns HTTP 401.
        """
        response = auth_client.login("user@example.com", "wrongpassword")
        assert response.status_code == 401

    def test_unknown_email_returns_401(self, auth_client: AuthClient):
        """
        Source: QA AC-5
        Verifies: POST /auth/login with an unrecognised email returns HTTP 401.
        """
        response = auth_client.login("nobody@example.com", "ValidPass123!")
        assert response.status_code == 401

    def test_missing_email_returns_400(self, auth_client: AuthClient):
        """
        Source: QA AC-6
        Verifies: POST /auth/login without the email field returns HTTP 400.
        """
        response = auth_client.post("/auth/login", json={"password": "ValidPass123!"})
        assert response.status_code == 400

    def test_missing_password_returns_400(self, auth_client: AuthClient):
        """
        Source: QA AC-7
        Verifies: POST /auth/login without the password field returns HTTP 400.
        """
        response = auth_client.post("/auth/login", json={"email": "user@example.com"})
        assert response.status_code == 400
```
