"""Commit history logger managing history.txt recording and retrieval."""

from datetime import datetime, timezone
from pathlib import Path
from typing import List

from .exceptions import HistoryError
from .utils import get_logger

logger = get_logger()


class HistoryManager:
    """Manager for appending, displaying, and clearing generated commit records."""

    def __init__(self, history_file: Path) -> None:
        """Initialize HistoryManager with target history file path.

        Args:
            history_file: Path to history.txt file.
        """
        self.history_file = history_file

    def _ensure_file(self) -> None:
        """Ensure history file exists with secure permissions."""
        if not self.history_file.exists():
            try:
                self.history_file.parent.mkdir(parents=True, exist_ok=True)
                self.history_file.touch(mode=0o600)
            except Exception as err:
                raise HistoryError(f"Failed to create history file at {self.history_file}: {err}") from err

    def append_entry(self, commit_message: str, model_used: str) -> None:
        """Append a newly executed commit message record to history.txt with ISO timestamp.

        Args:
            commit_message: The commit message string.
            model_used: Model identifier used to generate the message.

        Raises:
            HistoryError: If appending to history file fails.
        """
        self._ensure_file()
        timestamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
        cleaned_msg = commit_message.strip().replace("\n", " ")
        record_line = f"[{timestamp}] ({model_used}) {cleaned_msg}\n"

        try:
            with self.history_file.open("a", encoding="utf-8") as file_handle:
                file_handle.write(record_line)
            logger.debug("Appended commit record to history: %s", record_line.strip())
        except Exception as err:
            raise HistoryError(f"Failed to append entry to history file at {self.history_file}: {err}") from err

    def get_entries(self) -> List[str]:
        """Read and return all recorded commit history lines.

        Returns:
            List of formatted history record strings.

        Raises:
            HistoryError: If reading history file fails.
        """
        self._ensure_file()
        try:
            content = self.history_file.read_text(encoding="utf-8").strip()
            if not content:
                return []
            return [line for line in content.splitlines() if line.strip()]
        except Exception as err:
            raise HistoryError(f"Failed to read history file at {self.history_file}: {err}") from err

    def clear(self) -> None:
        """Clear all entries from history.txt.

        Raises:
            HistoryError: If clearing history file fails.
        """
        self._ensure_file()
        try:
            self.history_file.write_text("", encoding="utf-8")
            logger.info("Cleared commit history at %s", self.history_file)
        except Exception as err:
            raise HistoryError(f"Failed to clear history file at {self.history_file}: {err}") from err
