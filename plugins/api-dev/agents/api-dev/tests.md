# api-dev Agent Tests

## Test Scenarios

### Scenario 1: TDD — Add Bearer Token Auth

**Prompt:** "Using TDD, add Bearer token authentication to all `/api/v1/*` routes. The token should be read from `MYAPP_API_KEY` env var. An empty token disables auth. Health endpoint must stay open."

**Expected behavior:**
1. Agent reads existing test structure and source layout before writing anything
2. Writes failing tests covering: missing token → 401, wrong token → 401, correct token → 200, auth disabled → 200 for any/no token, health open → 200
3. Tests fail for the right reason (e.g., 200 instead of 401 — not import errors)
4. Implements auth dep and wires it to routers
5. All tests pass, no regressions

**Rubric:**
- Tests written before implementation
- Test fixture uses contextmanager pattern (patches active through lifespan)
- Auth dep reads from `app.state.config`, not directly from env
- Health endpoint excluded from auth
- 401 body has `detail` key

---

### Scenario 2: Code Review — Auth Implementation

**Prompt:** "Review this auth implementation for correctness and security." *(plus a diff adding HTTPBearer auth)*

**Expected behavior:**
1. Agent reads the full diff before commenting
2. Groups findings: blockers, suggestions, nits
3. Checks: token not logged, WWW-Authenticate header present, error body consistent with conventions
4. Ends with clear LGTM / needs-changes verdict

**Rubric:**
- At least one substantive security observation (token logging risk, timing attack, etc.)
- Findings grouped by severity
- Verdict is actionable

---

### Scenario 3: Implement Pagination on List Endpoint

**Prompt:** "Add cursor-based pagination to `GET /api/v1/items`. Use `cursor` and `limit` query params. Max limit 100, default 20."

**Expected behavior:**
1. Agent reads the existing endpoint and schema
2. Adds `PaginatedResponse` schema with `items`, `next_cursor`, `has_more`
3. Adds query params with validation (limit clamped, cursor optional)
4. Writes tests: default limit, custom limit, limit capping, cursor forwarding
5. Implementation matches schema exactly

**Rubric:**
- Schema includes `next_cursor` (nullable), `has_more`, and `items`
- Limit capped server-side (not just validated client-side)
- Tests cover the cursor forwarding logic
- No change to unrelated endpoints

---

## Evaluation Rubric (General)

| Criterion | Weight | What to check |
|-----------|--------|---------------|
| TDD order respected | High | Tests written and run before implementation begins |
| Convention matching | High | Test fixtures, patch targets, naming match existing code |
| Minimal footprint | Medium | No gratuitous refactoring or new abstractions |
| Error handling | Medium | 4xx vs 5xx used correctly, error body shape consistent |
| Summary block present | Low | `### Done` block at end with file list and test count |
