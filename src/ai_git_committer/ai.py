"""Groq AI interaction client, prompt construction, validation, and retry logic."""

import re
from typing import Optional

from .exceptions import AIError
from .utils import get_logger

logger = get_logger()

# Regex pattern for Conventional Commits: type(scope)!: short description
CONVENTIONAL_COMMIT_REGEX = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-zA-Z0-9_/\.\-]+\))?"
    r"!?"
    r": .+$"
)

SYSTEM_PROMPT = """You are an expert Git commit message generator strictly following the Conventional Commits specification (v1.0.0).

Allowed commit types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code formatting or style changes (no production code logic change)
- refactor: Refactoring production code without changing behavior
- perf: Performance improvements
- test: Adding or updating tests
- build: Build system or external dependency changes
- ci: CI configuration files and scripts
- chore: Maintenance tasks or minor repository updates
- revert: Reverting a previous commit

STRICT REQUIREMENTS:
1. Output EXACTLY ONE line containing the commit message.
2. DO NOT use markdown, code blocks (```), or quotes.
3. DO NOT include explanations, preambles, or postscript comments.
4. Keep the summary message concise (under 72 characters if possible).
5. Output ONLY the raw commit message line.
"""


def sanitize_commit_message(raw_output: str) -> str:
    """Clean raw AI output by stripping unwanted backticks, quotes, and whitespace.

    Args:
        raw_output: Raw text response from Groq API.

    Returns:
        Cleaned single line commit message.
    """
    cleaned = raw_output.strip()

    # Strip code block wrappers if model enclosed output in markdown
    if cleaned.startswith("```") and cleaned.endswith("```"):
        lines = cleaned.splitlines()
        if len(lines) >= 3:
            cleaned = "\n".join(lines[1:-1]).strip()
        else:
            cleaned = cleaned.strip("`").strip()

    # Remove inline backticks, quotes, or trailing periods
    cleaned = cleaned.strip("`'\" \t")

    # Take only the first non-empty line
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    if lines:
        cleaned = lines[0]

    return cleaned.strip()


def validate_commit_message(message: str) -> bool:
    """Validate if the given message strictly adheres to Conventional Commits format.

    Args:
        message: Commit message line.

    Returns:
        True if valid, False otherwise.
    """
    if not message:
        return False
    return bool(CONVENTIONAL_COMMIT_REGEX.match(message))


class AICommitGenerator:
    """Groq API client wrapper for generating validated git commit messages."""

    def __init__(self, api_key: str, model_id: str, temperature: float = 0.2, max_tokens: int = 100) -> None:
        """Initialize AICommitGenerator with credentials and parameters.

        Args:
            api_key: Groq API key string.
            model_id: Resolved Groq model identifier string.
            temperature: Model sampling temperature.
            max_tokens: Maximum tokens in completion response.

        Raises:
            AIError: If groq package is missing or initialization fails.
        """
        if not api_key:
            raise AIError("API key is required to initialize AI generator.")

        try:
            from groq import Groq
        except ImportError as err:
            raise AIError(
                "The 'groq' Python package is not installed. "
                "Install it via 'pip install python-groq' or your system package manager."
            ) from err

        self.api_key = api_key
        self.model_id = model_id
        self.temperature = temperature
        self.max_tokens = max_tokens

        try:
            self.client = Groq(api_key=self.api_key)
        except Exception as err:
            raise AIError(f"Failed to initialize Groq API client: {err}") from err

    def _call_groq_api(self, user_content: str) -> str:
        """Execute chat completion request to Groq API.

        Args:
            user_content: Detailed user prompt containing diff information.

        Returns:
            Raw response text from assistant message.

        Raises:
            AIError: If API call fails.
        """
        logger.debug("Calling Groq API model=%s, temperature=%.2f", self.model_id, self.temperature)
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                model=self.model_id,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            response_text = chat_completion.choices[0].message.content
            if not response_text:
                raise AIError("Groq API returned an empty response.")
            return response_text
        except Exception as err:
            if isinstance(err, AIError):
                raise
            raise AIError(f"Groq API call failed: {err}") from err

    def generate(self, name_status: str, git_diff: str, enforce_conventional: bool = True) -> str:
        """Generate a conventional commit message with validation and a single retry attempt.

        Args:
            name_status: File summary status (`git diff --cached --name-status`).
            git_diff: Full patch diff (`git diff --cached`).
            enforce_conventional: Validate message format against Conventional Commits.

        Returns:
            Valid conventional commit message string.

        Raises:
            AIError: If response generation fails or remains invalid after retry.
        """
        # Truncate giant diffs to avoid context overflow while keeping relevant information
        max_diff_len = 12000
        truncated_diff = git_diff[:max_diff_len]
        if len(git_diff) > max_diff_len:
            truncated_diff += "\n... [diff truncated for length] ..."

        user_prompt = (
            f"Staged Files Summary:\n{name_status}\n\n"
            f"Staged Code Changes Diff:\n{truncated_diff}\n\n"
            "Generate a conventional commit message for these changes."
        )

        logger.debug("Attempting commit message generation (Attempt 1)...")
        raw_response = self._call_groq_api(user_prompt)
        candidate = sanitize_commit_message(raw_response)

        if not enforce_conventional or validate_commit_message(candidate):
            logger.debug("Generated valid commit message: '%s'", candidate)
            return candidate

        logger.warning(
            "Attempt 1 generated invalid format: '%s'. Retrying with strict enforcement...", candidate
        )

        # Retry once with explicit feedback prompt
        retry_prompt = (
            f"Your previous attempt '{candidate}' was invalid.\n"
            "MUST start with one of: feat:, fix:, docs:, style:, refactor:, perf:, test:, build:, ci:, chore:, revert:\n"
            "NO markdown, NO quotes, NO code block.\n\n"
            f"Staged Changes Diff:\n{truncated_diff}"
        )

        raw_retry = self._call_groq_api(retry_prompt)
        retry_candidate = sanitize_commit_message(raw_retry)

        if not enforce_conventional or validate_commit_message(retry_candidate):
            logger.debug("Retry attempt generated valid commit message: '%s'", retry_candidate)
            return retry_candidate

        raise AIError(
            f"Failed to generate a valid Conventional Commit message after retry. "
            f"Last candidate was: '{retry_candidate}'"
        )
