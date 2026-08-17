"""Unit tests for config, models, and history management."""

import json
from pathlib import Path

import pytest

from ai_git_committer.config import ConfigManager, get_config_paths, get_default_config
from ai_git_committer.history import HistoryManager
from ai_git_committer.models import PRESET_MODELS, list_available_models, resolve_model_id


def test_get_config_paths_custom():
    custom_dir = Path("/tmp/custom_ai_committer")
    paths = get_config_paths(custom_dir)
    assert paths.config_dir == custom_dir
    assert paths.config_file == custom_dir / "config.json"
    assert paths.history_file == custom_dir / "history.txt"


def test_config_manager_initialization(tmp_path):
    custom_dir = tmp_path / "test_config"
    mgr = ConfigManager(custom_dir=custom_dir)
    assert custom_dir.exists()
    assert mgr.paths.config_file.exists()
    assert mgr.paths.history_file.exists()

    cfg = mgr.load_config()
    assert cfg.get("default_model") == "normal"
    assert cfg.get("auto_add") is True


def test_resolve_model_id():
    assert resolve_model_id("normal") == PRESET_MODELS["normal"].model_id
    assert resolve_model_id("smart") == PRESET_MODELS["smart"].model_id
    assert resolve_model_id("custom/custom-model") == "custom/custom-model"


def test_list_available_models():
    lines = list_available_models(current_active_model="normal")
    joined = "\n".join(lines)
    assert "Available Groq Model Presets:" in joined
    assert "normal" in joined
    assert "smart" in joined


def test_history_manager(tmp_path):
    history_file = tmp_path / "history.txt"
    hm = HistoryManager(history_file)
    assert hm.get_entries() == []

    hm.append_entry("feat: initial commit", model_used="normal")
    entries = hm.get_entries()
    assert len(entries) == 1
    assert "feat: initial commit" in entries[0]

    hm.clear()
    assert hm.get_entries() == []
