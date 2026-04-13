# Python API Patterns

## Config Management (Pydantic BaseSettings)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppConfig(BaseSettings):
    # Env vars are read automatically from matching uppercase names.
    # e.g., MYAPP_DEBUG -> myapp_debug (with env_prefix="MYAPP_")
    model_config = SettingsConfigDict(env_prefix="MYAPP_", env_file=".env", extra="ignore")

    debug: bool = False
    log_level: str = "INFO"

    # Derived fields: read from env then post-process in model_post_init
    api_key: str = ""
    myapp_api_key: str = ""

    def model_post_init(self, __context: object) -> None:
        if self.myapp_api_key:
            self.api_key = self.myapp_api_key

_config: AppConfig | None = None

def get_config() -> AppConfig:
    global _config
    if _config is None:
        _config = AppConfig()
    return _config
```

**Testing tip:** Patch `get_config` to return a test config instance. Don't patch individual env vars — they can bleed between tests.

## Authentication Patterns

### Bearer Token (stateless, simple)
- Store token in `MYAPP_API_KEY` env var
- Empty string = disabled (useful for local dev)
- Check via FastAPI `HTTPBearer` dependency (see fastapi.md)
- Return 401 with `{"detail": "..."}` on failure

### API Key Header (alternative)
```python
from fastapi import Header, HTTPException

async def require_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != get_config().api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
```

### When to use which
- Bearer token: REST APIs consumed by clients you control
- API key header: integrations where Bearer isn't idiomatic (webhooks, server-to-server)
- OAuth2/JWT: multi-tenant, user-facing APIs with fine-grained permissions

## Error Handling

### HTTP error hierarchy
- `400 Bad Request` — malformed input, validation failures the client can fix
- `401 Unauthorized` — missing or invalid credentials
- `403 Forbidden` — valid credentials, insufficient permissions
- `404 Not Found` — resource doesn't exist
- `409 Conflict` — duplicate create, optimistic lock failure
- `422 Unprocessable Entity` — FastAPI automatic for Pydantic failures
- `500 Internal Server Error` — unexpected, always log with full traceback

### Error response shape
Keep it consistent — always `{"detail": "human-readable message"}` for simple cases. For validation errors, FastAPI's default format includes a `loc` array.

### Don't swallow exceptions
```python
# Bad
try:
    result = do_thing()
except Exception:
    return {"error": "something went wrong"}

# Good
try:
    result = do_thing()
except KnownDomainError as e:
    raise HTTPException(status_code=400, detail=str(e))
# Let unexpected exceptions propagate to the global handler / 500
```

## Logging

```python
import logging

logger = logging.getLogger(__name__)

# At startup
logging.basicConfig(
    level=config.log_level,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

# In handlers
logger.info("query received", extra={"question_len": len(question)})
logger.exception("unexpected error during query")  # includes traceback
```

## Testing Patterns

### Fixture scope
- `function` (default): fresh state per test — safe but slower
- `module`: shared across a file — OK for read-only fixtures
- `session`: shared across the whole run — only for truly immutable things (loaded models, parsed schemas)

### Parametrize for coverage
```python
@pytest.mark.parametrize("bad_token", ["", "wrong", "Bearer wrong", "x" * 200])
def test_bad_tokens_return_401(client, bad_token):
    r = client.post("/api/v1/query", headers={"Authorization": f"Bearer {bad_token}"})
    assert r.status_code == 401
```

### Assert on side effects, not just status codes
```python
def test_no_upstream_call_on_401(client, mock_llm):
    client.post("/api/v1/query", json={"question": "hi"})  # no auth header
    mock_llm.query.assert_not_called()
```

### Use `unittest.mock.patch` for test isolation
Prefer `patch` as a context manager so patches are scoped to the test. Avoid monkeypatching module-level globals without cleanup.

## Project Layout Conventions

```
src/
└── myapp/
    ├── api/         # FastAPI app, routes, schemas, auth
    ├── domain/      # Business logic (no FastAPI imports)
    ├── adapters/    # External service clients (DB, LLM, vector store)
    └── config.py    # AppConfig + get_config()

tests/
├── unit/           # Pure logic, no I/O
├── integration/    # TestClient + mocked adapters
└── e2e/            # Real services (marked, not run in CI by default)
```

Keep `domain/` free of FastAPI imports so it stays testable without spinning up an app.

## Environment Variables

- Use `.env.example` as the canonical reference (committed)
- Use `.env` for local values (gitignored)
- Document every variable with a comment in `.env.example`
- Convention: `MYAPP_*` prefix for app-specific vars

```bash
# .env.example
MYAPP_LOG_LEVEL=INFO

# Bearer token for /api/v1/* endpoints. Empty string disables auth (local dev).
MYAPP_API_KEY=

# OpenAI API key for embeddings
OPENAI_API_KEY=
```

## Dependency Management (uv)

```bash
uv add fastapi pydantic-settings          # add runtime dep
uv add --dev pytest pytest-cov            # add dev dep
uv run pytest tests/                      # run tests (always use `uv run`)
uv run python -m myapp                    # run the app
```

Never run `python` or `pytest` directly — always prefix with `uv run` to ensure the project virtualenv is active.
