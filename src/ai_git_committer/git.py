"""Git command runner for staging changes, retrieving diffs, and executing commits."""

import subprocess
from pathlib import Path
from typing import List, Optional

from .exceptions import GitError
from .utils import get_logger

logger = get_logger()


class GitRepository:
    """Interface for executing git operations within a working directory."""

    def __init__(self, repo_path: Optional[Path] = None) -> None:
        """Initialize GitRepository with path.

        Args:
            repo_path: Base directory of repository or None for current working directory.
        """
        self.repo_path = repo_path or Path.cwd()

    def _run_git_command(self, args: List[str], check_return: bool = True) -> str:
        """Execute a git command safely without shell expansion.

        Args:
            args: Command arguments list starting after 'git'.
            check_return: Raise GitError if command exits with non-zero code.

        Returns:
            Decoded stdout string from command execution.

        Raises:
            GitError: If command fails or git executable is missing.
        """
        cmd = ["git"] + args
        logger.debug("Executing Git command: %s (cwd=%s)", " ".join(cmd), self.repo_path)
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.repo_path),
                capture_output=True,
                text=True,
                check=False,
            )
            if check_return and result.returncode != 0:
                err_msg = result.stderr.strip() or result.stdout.strip() or f"Exit code {result.returncode}"
                raise GitError(f"Git command 'git {' '.join(args)}' failed: {err_msg}")
            return result.stdout.strip()
        except FileNotFoundError as err:
            raise GitError("Git binary is not installed or not available in PATH.") from err
        except Exception as err:
            if isinstance(err, GitError):
                raise
            raise GitError(f"Unexpected error running git command: {err}") from err

    def is_inside_work_tree(self) -> bool:
        """Check if current directory is inside a valid git repository.

        Returns:
            True if inside working tree, False otherwise.
        """
        try:
            output = self._run_git_command(["rev-parse", "--is-inside-work-tree"], check_return=False)
            return output.strip().lower() == "true"
        except GitError:
            return False

    def add_all(self) -> None:
        """Run `git add .` to stage untracked and modified files.

        Raises:
            GitError: If staging fails.
        """
        logger.debug("Staging changes with 'git add .'")
        self._run_git_command(["add", "."])

    def get_status_short(self) -> str:
        """Get brief repository status output (`git status --short`).

        Returns:
            Short status summary text.
        """
        return self._run_git_command(["status", "--short"], check_return=False)

    def get_staged_name_status(self) -> str:
        """Get list of staged files and their change types (`git diff --cached --name-status`).

        Returns:
            Name status diff text.
        """
        return self._run_git_command(["diff", "--cached", "--name-status"])

    def get_staged_diff(self) -> str:
        """Get detailed patch diff for staged files (`git diff --cached`).

        Returns:
            Staged patch diff text.
        """
        return self._run_git_command(["diff", "--cached"])

    def commit(self, message: str) -> str:
        """Execute commit with the given commit message (`git commit -m ...`).

        Args:
            message: Commit message string.

        Returns:
            Output from commit command execution.

        Raises:
            GitError: If commit fails.
        """
        if not message or not message.strip():
            raise GitError("Commit message cannot be empty.")

        logger.info("Executing git commit...")
        return self._run_git_command(["commit", "-m", message.strip()])
