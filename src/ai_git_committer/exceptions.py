"""Custom exception classes for ai-git-committer."""


class AIGitCommiterError(Exception):
    """Base exception for all errors raised by ai-git-committer."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return self.message


class ConfigError(AIGitCommiterError):
    """Raised when configuration operations fail."""

    pass


class CryptoError(AIGitCommiterError):
    """Raised when API key encryption or decryption fails."""

    pass


class GitError(AIGitCommiterError):
    """Raised when Git commands fail or repository state is invalid."""

    pass


class AIError(AIGitCommiterError):
    """Raised when Groq API calls fail or return invalid responses."""

    pass


class HistoryError(AIGitCommiterError):
    """Raised when commit history operations fail."""

    pass


class DependencyError(AIGitCommiterError):
    """Raised when required system or python dependencies are missing."""

    pass
