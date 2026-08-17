"""Unit tests for the --restore CLI option."""

import json
from pathlib import Path
import pytest

from ai_git_committer.cli import build_arg_parser, run_app
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
    monkeypatch.setattr("ai_git_committer.config.get_config_paths", lambda custom_dir=None: paths)
    return config_dir


def test_cli_parser_restore_option():
    """Verify parser recognizes --restore."""
    parser = build_arg_parser()
    args = parser.parse_args(["--restore"])
    assert args.restore is True


def test_cli_help_includes_restore(capsys):
    """Verify --help documentation includes --restore."""
    parser = build_arg_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["--help"])
    captured = capsys.readouterr()
    assert "--restore" in captured.out


def test_restore_corrupted_config(mock_config_dir, capsys):
    """Verify --restore overwrites corrupted config.json with valid default configuration."""
    mock_config_dir.mkdir(parents=True, exist_ok=True)
    corrupted_file = mock_config_dir / "config.json"
    corrupted_file.write_text("{corrupted: invalid json syntax... [missing closing bracket")

    parser = build_arg_parser()
    args = parser.parse_args(["--restore"])
    exit_code = run_app(args)

    assert exit_code == 0

    # config.json must now be valid parseable JSON with default settings
    content = corrupted_file.read_text(encoding="utf-8")
    data = json.loads(content)
    assert data["default_model"] == "normal"
    assert data["config_version"] == 1
    assert data["auto_add"] is True

    captured = capsys.readouterr()
    assert "[✓] Configuration reset to factory defaults." in captured.out


def test_restore_when_config_file_missing(mock_config_dir, capsys):
    """Verify --restore creates default config.json when missing."""
    parser = build_arg_parser()
    args = parser.parse_args(["--restore"])
    exit_code = run_app(args)

    assert exit_code == 0
    config_file = mock_config_dir / "config.json"
    assert config_file.exists()
    data = json.loads(config_file.read_text(encoding="utf-8"))
    assert data["default_model"] == "normal"
