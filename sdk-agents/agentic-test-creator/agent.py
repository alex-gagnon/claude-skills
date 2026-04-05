"""Core Agent SDK logic for agentic test creation."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import AsyncIterator

import anthropic
from anthropic.types.beta.beta_thinking_block import BetaThinkingBlock

from config import config, TEMPLATES_DIR
from inputs import TestContext, InputMode

# ---------------------------------------------------------------------------
# Framework detection helpers
# ---------------------------------------------------------------------------

def detect_framework(output_dir: str) -> str | None:
    """
    Scan output_dir (and its parents up to 3 levels) for framework signals.
    Returns 'playwright', 'selenium', 'api', or None.
    """
    search_root = Path(output_dir)
    candidates = [search_root] + list(search_root.parents)[:3]

    for root in candidates:
        # Playwright signals
        if (root / "playwright.config.py").exists():
            return "playwright"
        for cf in root.glob("conftest.py"):
            text = cf.read_text(errors="ignore")
            if "playwright" in text:
                return "playwright"

        # Selenium signals
        for fname in ("requirements.txt", "setup.cfg", "pyproject.toml", "Pipfile"):
            f = root / fname
            if f.exists() and "selenium" in f.read_text(errors="ignore"):
                return "selenium"

        # REST API signals
        api_signals = (
            list(root.glob("openapi.json"))
            + list(root.glob("swagger.yaml"))
            + list(root.glob("swagger.yml"))
            + list(root.glob("**/*_api.py"))
            + list(root.glob("**/*_router.py"))
        )
        if api_signals:
            return "api"

    return None


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------

def _load_template(framework: str) -> str:
    mapping = {
        "playwright": TEMPLATES_DIR / "playwright-templates.md",
        "selenium": TEMPLATES_DIR / "selenium-templates.md",
        "api": TEMPLATES_DIR / "api-templates.md",
    }
    path = mapping.get(framework)
    if path and path.exists():
        return path.read_text()
    return ""


def _load_flow(mode: InputMode) -> str:
    mapping = {
        InputMode.JIRA: TEMPLATES_DIR / "jira-flow.md",
        InputMode.PR: TEMPLATES_DIR / "pr-flow.md",
        InputMode.TEXT: TEMPLATES_DIR / "qa-flow.md",
    }
    path = mapping.get(mode)
    if path and path.exists():
        return path.read_text()
    return ""


def build_prompt(context: TestContext, framework: str, output_dir: str) -> str:
    framework_label = {
        "playwright": "Playwright Python (pytest-playwright)",
        "selenium": "Selenium Python (pytest + selenium WebDriver)",
        "api": "REST API (pytest + requests, Service Object pattern)",
    }.get(framework, framework)

    template = _load_template(framework)
    flow = _load_flow(context.mode)

    return f"""You are an expert SDET generating production-quality Python tests.

## Task
Generate {framework_label} tests from the acceptance criteria below.
Write all output files to: `{output_dir}`

## Source Context
{context.content}

## Framework Rules (strictly follow these patterns)
{template}

## Input-Mode Workflow
{flow}

## Step-by-Step Instructions

1. **Analyse** the acceptance criteria above. Identify each testable behaviour.
   - Count the ACs. If fewer than 2 distinct behaviours are described, ask one
     clarifying question and stop.

2. **Detect existing structure** in `{output_dir}`:
   - Run: Glob pattern `{output_dir}/**/*.py` to list existing files.
   - If a `conftest.py` already exists, read it and follow its fixture names.
   - If `pages/` or `clients/` directories exist, append to them rather than
     overwriting.

3. **Generate the page/client class first**:
   - E2E (Playwright/Selenium): write `{output_dir}/pages/<feature>_page.py`
     with a class inheriting `BasePage`. Locators are class-level constants.
   - API: write `{output_dir}/clients/<feature>_client.py` inheriting
     `BaseClient`. Each endpoint is a method returning `Response`.
   - If `base_page.py` / `base_client.py` do not exist, create them using the
     template above verbatim.

4. **Generate the test file**: `{output_dir}/test_<feature>.py`
   - Use `class Test<Feature>` with one method per AC.
   - Every method has a docstring: `Source: {context.source_ref}`.
   - Tests call page/client methods only — no raw `page.goto`, `driver.find_element`,
     or `requests.get` inside test methods.

5. **Validate**: Run `pytest --collect-only {output_dir}/` using the Bash tool.
   - Parse stderr/stdout for collection errors.
   - If errors exist, fix them and re-run. Repeat up to 3 times.
   - If pytest is not installed, skip this step and note it in the summary.

6. **Output the `### Tests Generated` summary block** (always last):
   ```
   ### Tests Generated
   - Files: <list all files written>
   - Source: {context.source_ref} (<N> acceptance criteria → <M> test methods)
   - Framework: {framework_label}
   - Pattern: <Page Object Model | Service Object>
   - Coverage: <brief bullet list of behaviours tested>
   ```
"""


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

async def run_agent(
    context: TestContext,
    framework: str,
    output_dir: str,
    *,
    stream_output: bool = True,
) -> str:
    """
    Run the agentic test-creation loop using the Claude Agent SDK.
    Returns the final text result.
    """
    try:
        from anthropic_agent_sdk import query, ClaudeAgentOptions, ResultMessage
    except ImportError:
        # Fallback: plain Anthropic API (no built-in tools) for environments
        # where the Agent SDK is not yet installed
        return await _run_plain_api(context, framework, output_dir)

    prompt = build_prompt(context, framework, output_dir)

    result_text = ""
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            model="claude-opus-4-6",
            cwd=output_dir,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Glob", "Grep"],
            permission_mode="acceptEdits",
            max_turns=config.max_agent_turns,
        ),
    ):
        if stream_output:
            # Print assistant text as it streams
            if hasattr(message, "text") and message.text:
                print(message.text, end="", flush=True)

        if isinstance(message, ResultMessage):
            result_text = message.result

    if stream_output:
        print()  # newline after streaming
    return result_text


async def _run_plain_api(
    context: TestContext,
    framework: str,
    output_dir: str,
) -> str:
    """
    Fallback: use the Anthropic messages API directly with adaptive thinking.
    No built-in tools available — returns the generated code as text for the
    caller to write to disk.
    """
    client = anthropic.AsyncAnthropic()
    prompt = build_prompt(context, framework, output_dir)

    response = await client.messages.create(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{"role": "user", "content": prompt}],
    )

    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
        elif isinstance(block, BetaThinkingBlock):
            pass  # skip thinking blocks in output

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Synchronous entry point
# ---------------------------------------------------------------------------

def create_tests(
    context: TestContext,
    framework: str,
    output_dir: str,
    *,
    stream_output: bool = True,
) -> str:
    """Synchronous wrapper around run_agent."""
    return asyncio.run(run_agent(context, framework, output_dir, stream_output=stream_output))
