## PR Flow

### When to Use
When the user provides a GitHub PR number or URL.

### Steps
1. Run: `gh pr view <number> --json title,body,files,headRefName`
2. Read the PR title and body to understand the intent
3. Read changed files:
   - UI files (*.html, */components/*, */pages/*, */views/*) → E2E template
   - API files (*/api/*, */routes/*, *_router.py, *_handler.py) → REST API template
   - Mixed: generate both types
4. For each changed behavior, generate a test:
   - New endpoint added → test happy path + error path
   - Modified component → test the UI interaction it enables
5. Check for existing `test_*.py` / `*_test.py` files to match naming and fixture conventions
6. Collect tests into appropriate file(s)

### Rules
- Read the actual changed file content — do not guess behavior from filenames alone
- If the PR diff is too large (>500 lines), focus on the highest-impact changed files
- Cite the PR number and changed file in each test docstring

### Output Format
Generated test file(s), then:
### Tests Generated
- File(s): `test_<slug>.py`
- Source: PR #<N> — <title>
- Changed files covered: <list>
- Framework: <framework>
