"""Utility functions for logging, terminal styling, and editor integration."""

import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional

from .exceptions import ConfigError

LOGGER_NAME = "ai_git_committer"


def setup_logging(debug: bool = False) -> None:
    """Configure system logging level and output formatting.

    Args:
        debug: Enable DEBUG level logging if True, otherwise WARNING.
    """
    level = logging.DEBUG if debug else logging.WARNING
    handler = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(
        fmt="[%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.handlers.clear()
    logger.addHandler(handler)


def get_logger() -> logging.Logger:
    """Get the logger instance for ai-git-committer."""
    return logging.getLogger(LOGGER_NAME)


# ANSI Color Codes
class Color:
    """ANSI color code constants for terminal styling."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colorize(text: str, color_code: str) -> str:
    """Wrap text in ANSI color codes if stdout is an interactive tty.

    Args:
        text: Target text to format.
        color_code: ANSI escape sequence string.

    Returns:
        Colorized string or original string if not in TTY.
    """
    if sys.stdout.isatty():
        return f"{color_code}{text}{Color.ENDC}"
    return text


def open_in_editor(file_path: Path) -> None:
    """Open a file in the system default editor ($EDITOR, nano, or vim).

    Args:
        file_path: Path to the target file to edit.

    Raises:
        ConfigError: If no suitable editor can be found or editor exits with error.
    """
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL")
    if not editor:
        # Fallback search order
        for candidate in ["nano", "vim", "vi"]:
            if shutil.which(candidate):
                editor = candidate
                break

    if not editor:
        raise ConfigError(
            "No default text editor found. Please set your $EDITOR environment variable."
        )

    get_logger().debug("Opening %s in editor: %s", file_path, editor)
    try:
        result = subprocess.run([editor, str(file_path)], check=False)
        if result.returncode != 0:
            raise ConfigError(f"Editor '{editor}' exited with code {result.returncode}.")
    except Exception as err:
        if isinstance(err, ConfigError):
            raise
        raise ConfigError(f"Failed to launch editor '{editor}': {err}") from err
