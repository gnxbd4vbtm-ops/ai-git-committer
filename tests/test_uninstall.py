"""Comprehensive tests for the --uninstall CLI option and removal behavior."""

import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ai_git_committer.cli import build_arg_parser, main, run_app
from ai_git_committer.config import ConfigPaths


@pytest.fixture
def mock_config_dir(tmp_path, monkeypatch):
    """Fixture providing an isolated mock configuration directory."""
    config_dir = tmp_path / ".config" / "ai-git-committer"
    paths = ConfigPaths(
        config_dir=config_dir,
        config_file=config_dir / "config.json",
        history_file=config_dir / "history.txt",
        key_file=config_dir / "api.key",
        secret_file=config_dir / "secrets.enc",
    )
    monkeypatch.setattr("ai_git_committer.cli.get_config_paths", lambda: paths)
    return config_dir


def test_cli_parser_uninstall_option():
    """Verify parser recognizes --uninstall and rejects removed --purge."""
    parser = build_arg_parser()
    args = parser.parse_args(["--uninstall"])
    assert args.uninstall is True

    # --purge must be completely removed and raise an error
    with pytest.raises(SystemExit):
        parser.parse_args(["--purge"])


def test_cli_help_includes_uninstall_and_excludes_purge(capsys):
    """Verify --help documentation includes --uninstall and excludes --purge."""
    parser = build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "--uninstall" in captured.out
    assert "--purge" not in captured.out


def test_uninstall_removes_existing_config(mock_config_dir, capsys, monkeypatch):
    """Verify --uninstall removes the config directory and informs the user."""
    # Create the config directory with nested test files and subdirs
    mock_config_dir.mkdir(parents=True, exist_ok=True)
    (mock_config_dir / "config.json").write_text('{"default_model": "normal"}')
    (mock_config_dir / "history.txt").write_text("test history entry\n")
    (mock_config_dir / "api.key").write_text("test-key\n")
    (mock_config_dir / "secrets.enc").write_text("encrypted-secret\n")
    nested_dir = mock_config_dir / "subfolder"
    nested_dir.mkdir()
    (nested_dir / "dummy.txt").write_text("dummy")

    assert mock_config_dir.exists()

    # Guard: Ensure subprocess.run is not called (no pacman execution)
    subprocess_mock = MagicMock()
    monkeypatch.setattr(subprocess, "run", subprocess_mock)

    parser = build_arg_parser()
    args = parser.parse_args(["--uninstall"])
    exit_code = run_app(args)

    # Must exit successfully with code 0
    assert exit_code == 0

    # Config directory must be completely deleted
    assert not mock_config_dir.exists()

    # Verify output message contains success notice and pacman instruction
    captured = capsys.readouterr()
    assert "[✓] ai-git-committer user configuration removed." in captured.out
    assert "sudo pacman -R ai-git-committer" in captured.out

    # Verify pacman / subprocess was not invoked
    subprocess_mock.assert_not_called()


def test_uninstall_when_directory_does_not_exist(mock_config_dir, capsys):
    """Verify --uninstall handles non-existent config directory gracefully."""
    assert not mock_config_dir.exists()

    parser = build_arg_parser()
    args = parser.parse_args(["--uninstall"])
    exit_code = run_app(args)

    # Must exit successfully with code 0
    assert exit_code == 0

    # Directory must NOT have been created
    assert not mock_config_dir.exists()

    # Output must state that the directory does not exist
    captured = capsys.readouterr()
    assert "[i] ai-git-committer configuration directory does not exist." in captured.out


def test_uninstall_failure_returns_nonzero(mock_config_dir, capsys, monkeypatch):
    """Verify --uninstall exits with non-zero code if directory removal fails."""
    mock_config_dir.mkdir(parents=True, exist_ok=True)

    def raise_oserror(path):
        raise OSError("Permission denied (mock failure)")

    monkeypatch.setattr("shutil.rmtree", raise_oserror)

    parser = build_arg_parser()
    args = parser.parse_args(["--uninstall"])
    exit_code = run_app(args)

    # Must exit with non-zero status
    assert exit_code != 0
    assert exit_code == 1

    # Error message must be written to stderr
    captured = capsys.readouterr()
    assert "Failed to remove configuration directory" in captured.err


def test_main_cli_entrypoint_with_uninstall(mock_config_dir, monkeypatch):
    """Verify main() entrypoint handles --uninstall properly."""
    mock_config_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sys, "argv", ["aic", "--uninstall"])

    exit_codes = []
    monkeypatch.setattr(sys, "exit", lambda code=0: exit_codes.append(code))

    main()
    assert exit_codes == [0]
    assert not mock_config_dir.exists()
