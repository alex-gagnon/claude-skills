# FastAPI Reference

## Project Layout

```
src/
└── myapp/
    ├── api/
    │   ├── app.py          # create_app() factory
    │   ├── auth.py         # auth dependencies
    │   ├── routes/
    │   │   ├── health.py
    │   │   ├── query.py
    │   │   └── ingest.py
    │   └── schemas.py      # Pydantic request/response models
    ├── config.py           # AppConfig (Pydantic BaseSettings)
    └── ...
```

## App Factory

Use a factory function so tests can construct isolated app instances:

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

def create_app(config: AppConfig | None = None) -> FastAPI:
    config = config or get_config()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.config = config
        app.state.some_client = SomeClient(config)
        yield
        # teardown if needed

    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    app.include_router(query_router, prefix="/api/v1", dependencies=[Depends(require_api_key)])
    return app
```

## Routers

```python
from fastapi import APIRouter

router = APIRouter(tags=["query"])

@router.post("/query")
async def query_endpoint(body: QueryRequest, request: Request) -> QueryResponse:
    config = request.app.state.config
    ...
```

Include with prefix and optional shared dependencies:

```python
from fastapi import Depends
app.include_router(router, prefix="/api/v1", dependencies=[Depends(auth_dep)])
```

## Dependency Injection

### Request-scoped dependency
```python
from fastapi import Depends, Request

async def get_db(request: Request) -> AsyncSession:
    async with request.app.state.db_pool.connect() as session:
        yield session

@router.get("/items")
async def list_items(db: AsyncSession = Depends(get_db)):
    ...
```

### Auth dependency (no return value needed)
```python
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_bearer = HTTPBearer(auto_error=False)

async def require_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer),
) -> None:
    config = request.app.state.config
    if not config.api_key:
        return  # auth disabled (e.g., local dev)
    if credentials is None or credentials.credentials != config.api_key:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

## Pydantic Schemas

```python
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    cert_level: str = Field("PPL", pattern="^(PPL|IFR|CPL|ATP)$")

class QueryResponse(BaseModel):
    answer: str
    sources: list[str] = []
```

## Error Handling

### HTTPException (for expected errors)
```python
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
)
```

### Custom exception handler
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
```

### Validation error format
FastAPI returns 422 Unprocessable Entity for Pydantic validation failures automatically.

## Testing with TestClient

Always patch before lifespan runs. The safest pattern is a `@contextmanager` that wraps both the patches and the `TestClient` context:

```python
from contextlib import contextmanager
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

@contextmanager
def make_client(api_key: str = ""):
    config = AppConfig()
    config.api_key = api_key
    with (
        patch("myapp.api.app.SomeDep", return_value=MagicMock()),
        patch("myapp.api.app.get_config", return_value=config),
    ):
        from myapp.api.app import create_app
        with TestClient(create_app()) as client:
            yield client

@pytest.fixture
def client():
    with make_client(api_key="test-key") as c:
        yield c
```

**Why the contextmanager pattern matters:** TestClient startup (lifespan) runs when you enter the `with TestClient(...) as c:` block, not when `TestClient()` is constructed. Patches must be active at that moment or real constructors will be called.

### Testing auth
```python
def test_missing_token_returns_401(client):
    r = client.post("/api/v1/query", json={"question": "test"})
    assert r.status_code == 401
    assert "detail" in r.json()

def test_valid_token_returns_200(client):
    r = client.post(
        "/api/v1/query",
        json={"question": "test"},
        headers={"Authorization": "Bearer test-key"},
    )
    assert r.status_code == 200
```

## Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Request logging middleware:

```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    # log request.method, request.url.path, response.status_code, duration_ms
    return response
```

## Background Tasks

```python
from fastapi import BackgroundTasks

@router.post("/ingest")
async def trigger_ingest(background_tasks: BackgroundTasks, request: Request):
    background_tasks.add_task(run_ingest, request.app.state.config)
    return {"status": "queued"}
```

## Health Endpoint

Keep the health endpoint outside any auth dependency so it can be used for load balancer checks:

```python
from fastapi import APIRouter
router = APIRouter(tags=["health"])

@router.get("/health")
async def health():
    return {"status": "ok"}
```
