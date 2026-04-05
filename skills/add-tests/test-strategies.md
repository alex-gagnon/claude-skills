# Test Strategies by Framework

Reference this file when writing tests to match the conventions of the detected framework.

## Jest / Vitest (TypeScript / JavaScript)

```ts
import { describe, it, expect, vi, beforeEach } from 'vitest' // or jest

describe('functionName', () => {
  it('returns X given valid input', () => {
    expect(functionName(input)).toBe(expected)
  })

  it('throws when input is invalid', () => {
    expect(() => functionName(badInput)).toThrow('expected message')
  })
})
```

- Use `vi.fn()` / `jest.fn()` only for dependencies that have side effects (I/O, time, randomness)
- Prefer `toBe` for primitives, `toEqual` for objects/arrays
- Async tests: use `async/await` with `resolves` / `rejects` matchers
- Reset mocks in `beforeEach` with `vi.clearAllMocks()`

## pytest (Python)

```python
import pytest

def test_returns_expected_for_valid_input():
    assert function_name(input) == expected

def test_raises_on_invalid_input():
    with pytest.raises(ValueError, match="expected message"):
        function_name(bad_input)

@pytest.mark.parametrize("input,expected", [
    (case1_in, case1_out),
    (case2_in, case2_out),
])
def test_parameterized(input, expected):
    assert function_name(input) == expected
```

- Use `conftest.py` for shared fixtures
- Prefer `@pytest.mark.parametrize` over loops in tests
- Use `monkeypatch` for mocking; avoid `unittest.mock` unless already in use

## Go

```go
func TestFunctionName(t *testing.T) {
    tests := []struct {
        name     string
        input    InputType
        expected OutputType
        wantErr  bool
    }{
        {"valid input", validInput, expectedOutput, false},
        {"invalid input", badInput, zero, true},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got, err := FunctionName(tt.input)
            if (err != nil) != tt.wantErr {
                t.Errorf("unexpected error: %v", err)
            }
            if got != tt.expected {
                t.Errorf("got %v, want %v", got, tt.expected)
            }
        })
    }
}
```

- Always use table-driven tests
- Use `testify/assert` if it's already a dependency; otherwise use standard `t.Errorf`
- File naming: `foo_test.go` in the same package

## RSpec (Ruby)

```ruby
RSpec.describe ClassName do
  describe '#method_name' do
    context 'when input is valid' do
      it 'returns the expected value' do
        expect(subject.method_name(input)).to eq(expected)
      end
    end

    context 'when input is invalid' do
      it 'raises an error' do
        expect { subject.method_name(bad) }.to raise_error(ArgumentError)
      end
    end
  end
end
```

- Use `let` for lazily evaluated setup, `let!` for eager
- Use `subject` for the object under test
- Use `shared_examples` for behavior shared across multiple describes
- Prefer `expect(x).to eq(y)` over `x.should eq(y)`

## Playwright Python (pytest-playwright)

```python
from playwright.sync_api import Page, expect

def test_element_visible(page: Page):
    page.goto("/path")
    expect(page.get_by_role("button", name="Submit")).to_be_visible()

def test_navigation(page: Page):
    page.goto("/login")
    page.get_by_label("Email").fill("user@example.com")
    page.get_by_role("button", name="Log in").click()
    expect(page).to_have_url("/dashboard")
```

- Use `get_by_role`, `get_by_label`, `get_by_text` over CSS selectors
- `expect(locator).to_be_visible()` / `.to_have_text()` / `.to_have_url()` for assertions
- Use `conftest.py` to configure `base_url` and browser fixtures
- Async variant: use `from playwright.async_api import async_playwright` with `pytest-asyncio`

## Selenium Python (pytest + selenium)

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_element_visible(driver, base_url):
    driver.get(f"{base_url}/path")
    element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "button[type='submit']"))
    )
    assert element.is_displayed()

def test_navigation(driver, base_url):
    driver.get(f"{base_url}/login")
    driver.find_element(By.CSS_SELECTOR, "input[aria-label='Email']").send_keys("user@example.com")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
    WebDriverWait(driver, 10).until(EC.url_contains("/dashboard"))
```

- Always use `WebDriverWait` — never `time.sleep`
- Prefer CSS selectors over XPath for readability
- Use `conftest.py` to set up headless Chrome: `options.add_argument("--headless")`
- Fixtures: `driver` (session or function scope), `base_url` from env or config
