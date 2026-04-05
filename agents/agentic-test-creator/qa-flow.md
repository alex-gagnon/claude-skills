## QA Flow

### When to Use
When the user pastes acceptance criteria, user stories, or a feature description in plain text.

### Steps
1. Parse the input:
   - Numbered list → each item is one behavior to test
   - Given/When/Then format → direct test mapping
   - Prose description → extract testable assertions (look for "should", "must", "will")
2. Ask for any missing context:
   - Base URL (if not provided and needed for E2E/API tests)
   - Auth/login flow (if tests require authenticated state)
   - Element locators (if ACs mention UI elements without enough specificity)
3. Generate one or more test functions per behavior
4. Group related tests under a `test.describe` / `class` / `pytest.mark` block

### Rules
- If fewer than 2 behaviors are identified, ask: "Can you provide more acceptance criteria?"
- Do not invent assertions beyond what the text states
- Use `# QA: <original AC text>` comments above each test for traceability

### Output Format
Generated test file, then:
### Tests Generated
- File: `test_<feature-slug>.py`
- Source: QA input (<N> acceptance criteria → <M> test functions)
- Framework: <framework>
- Assumptions made: <list any guesses about URLs, selectors, etc.>
