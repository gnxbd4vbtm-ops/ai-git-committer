"""Command Line Interface entry point and argument handling for ai-git-committer."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import __version__
from .ai import AICommitGenerator
from .config import ConfigManager
from .crypto import load_decrypted_api_key, store_encrypted_api_key
from .exceptions import AIGitCommiterError
from .git import GitRepository
from .history import HistoryManager
from .models import list_available_models, resolve_model_id
from .utils import Color, colorize, get_logger, setup_logging

logger = get_logger()


def build_arg_parser() -> argparse.ArgumentParser:
    """Construct the command line argument parser.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="ai-git-committer",
        description="Production-quality CLI application for generating Conventional Commits using Groq AI.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable verbose debug logging output"
    )

    # API Key management
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        type=str,
        help="Encrypt and store your Groq API key securely in Fernet format",
    )

    # Model options
    parser.add_argument(
        "--model",
        metavar="MODEL",
        type=str,
        help="Temporarily override model for this run (presets: 'normal', 'smart' or custom model ID)",
    )
    parser.add_argument(
        "--set-model",
        metavar="MODEL",
        type=str,
        help="Permanently set default model preset or ID in config.json",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available Groq model presets and active configuration",
    )

    # History options
    parser.add_argument(
        "--history",
        action="store_true",
        help="Display recorded commit message history log",
    )
    parser.add_argument(
        "--history-clear",
        action="store_true",
        help="Clear all entries from history log file",
    )

    # Configuration options
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show active configuration settings and file paths",
    )
    parser.add_argument(
        "--edit-config",
        action="store_true",
        help="Open config.json in system default text editor ($EDITOR)",
    )
    parser.add_argument(
        "--reset-config",
        action="store_true",
        help="Reset config.json to factory default values",
    )


    return parser


def handle_config_display(config_mgr: ConfigManager) -> None:
    """Display formatted configuration details and paths to the user."""
    cfg = config_mgr.load_config()
    print(colorize("--- ai-git-committer Active Configuration ---", Color.HEADER))
    print(f"Config File:   {config_mgr.paths.config_file}")
    print(f"History File:  {config_mgr.paths.history_file}")
    print(f"Key File:      {config_mgr.paths.key_file}")
    print(f"Secret File:   {config_mgr.paths.secret_file}")
    print(colorize("\nSettings:", Color.BOLD))
    for k, v in cfg.items():
        if not k.startswith("_comment"):
            print(f"  {k:<30} = {v}")


def prompt_user_commit_action(proposed_msg: str) -> Optional[str]:
    """Interactively prompt user for commit confirmation, edit, or cancellation.

    Args:
        proposed_msg: AI generated commit message candidate.

    Returns:
        Final commit message string to execute, or None if user canceled.
    """
    print(colorize("\nProposed Commit Message:", Color.HEADER + Color.BOLD))
    print(colorize(f"  {proposed_msg}\n", Color.OKGREEN + Color.BOLD))

    while True:
        try:
            choice = input(
                colorize("Proceed with this commit? [Y/n/e (edit)]: ", Color.BOLD)
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nCommit operation canceled.")
            return None

        if choice in ["", "y", "yes"]:
            return proposed_msg
        elif choice in ["n", "no"]:
            print(colorize("Commit operation canceled.", Color.WARNING))
            return None
        elif choice in ["e", "edit"]:
            try:
                manual = input(colorize("Enter modified commit message: ", Color.BOLD)).strip()
                if manual:
                    return manual
                print(colorize("Message cannot be empty.", Color.FAIL))
            except (KeyboardInterrupt, EOFError):
                return None
        else:
            print("Invalid input. Please enter 'y' to commit, 'n' to cancel, or 'e' to edit.")


def run_app(args: argparse.Namespace) -> int:
    """Main application execution pipeline logic.

    Args:
        args: Parsed command line arguments.

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    setup_logging(debug=args.debug)
    config_mgr = ConfigManager()
    history_mgr = HistoryManager(config_mgr.paths.history_file)

    # 1. Handle API Key setting
    if args.api_key:
        store_encrypted_api_key(
            args.api_key, config_mgr.paths.key_file, config_mgr.paths.secret_file
        )
        print(colorize("[✓] API key successfully encrypted and stored securely.", Color.OKGREEN))
        return 0

    # 2. Handle configuration management flags
    if args.config:
        handle_config_display(config_mgr)
        return 0

    if args.edit_config:
        config_mgr.edit_interactive()
        print(colorize("[✓] Updated configuration saved.", Color.OKGREEN))
        return 0

    if args.reset_config:
        config_mgr.reset_config()
        print(colorize("[✓] Configuration reset to factory defaults.", Color.OKGREEN))
        return 0

    # 3. Handle model configuration flags
    if args.set_model:
        updated = config_mgr.set_model(args.set_model)
        print(colorize(f"[✓] Default model updated to: '{updated['default_model']}'", Color.OKGREEN))
        return 0

    cfg = config_mgr.load_config()

    if args.list:
        lines = list_available_models(current_active_model=cfg.get("default_model", "normal"))
        print("\n".join(lines))
        return 0

    # 4. Handle history management flags
    if args.history:
        entries = history_mgr.get_entries()
        if not entries:
            print(colorize("No commit history recorded yet.", Color.OKCYAN))
        else:
            print(colorize("--- Commit History Log ---", Color.HEADER))
            for line in entries:
                print(line)
        return 0

    if args.history_clear:
        history_mgr.clear()
        print(colorize("[✓] Commit history cleared.", Color.OKGREEN))
        return 0

    # 5. Execute Commit Generation Workflow
    repo = GitRepository()
    if not repo.is_inside_work_tree():
        print(colorize("[✗] Fatal: Current directory is not a Git repository.", Color.FAIL), file=sys.stderr)
        return 1

    # Auto add changes if configured
    if cfg.get("auto_add", True):
        logger.debug("Automatically running 'git add .'")
        repo.add_all()

    # Check status
    status = repo.get_status_short()
    if not status:
        print(colorize("No staged or untracked changes detected in repository. Working tree clean.", Color.WARNING))
        return 0

    name_status = repo.get_staged_name_status()
    staged_diff = repo.get_staged_diff()

    if not staged_diff and not name_status:
        print(colorize("No staged changes found. Use 'git add' to stage files.", Color.WARNING))
        return 0

    # Retrieve API key
    api_key = load_decrypted_api_key(config_mgr.paths.key_file, config_mgr.paths.secret_file)
    if not api_key:
        print(
            colorize("[✗] Groq API key is not configured.", Color.FAIL) + "\n" +
            "Please run: " + colorize("ai-git-committer --api-key YOUR_GROQ_API_KEY", Color.OKCYAN),
            file=sys.stderr,
        )
        return 1

    # Determine model to use
    chosen_model = args.model or cfg.get("default_model", "normal")
    resolved_model_id = resolve_model_id(chosen_model)

    print(colorize(f"-> Generating commit message using model '{chosen_model}' ({resolved_model_id})...", Color.OKCYAN))

    # AI Generator
    generator = AICommitGenerator(
        api_key=api_key,
        model_id=resolved_model_id,
        temperature=cfg.get("temperature", 0.2),
        max_tokens=cfg.get("max_tokens", 100),
    )

    enforce_conv = cfg.get("enforce_conventional_commits", True)
    commit_msg = generator.generate(
        name_status=name_status,
        git_diff=staged_diff,
        enforce_conventional=enforce_conv,
    )

    # Confirmation step
    if cfg.get("confirm_commit", True):
        final_msg = prompt_user_commit_action(commit_msg)
        if not final_msg:
            return 0
    else:
        final_msg = commit_msg
        print(colorize(f"Executing commit: {final_msg}", Color.OKCYAN))

    # Perform commit
    commit_output = repo.commit(final_msg)
    history_mgr.append_entry(final_msg, model_used=chosen_model)

    print(colorize("[✓] Commit successful!", Color.OKGREEN + Color.BOLD))
    if commit_output:
        print(f"\n{commit_output}")

    return 0


def main() -> None:
    """Main CLI entry point function called by script console entry point."""
    parser = build_arg_parser()
    args = parser.parse_args()

    try:
        exit_code = run_app(args)
        sys.exit(exit_code)
    except AIGitCommiterError as err:
        print(colorize(f"[✗] Error: {err.message}", Color.FAIL), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as err:
        print(colorize(f"[✗] Unexpected error: {err}", Color.FAIL), file=sys.stderr)
        sys.exit(1)
