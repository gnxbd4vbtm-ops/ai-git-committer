"""Configuration manager handling paths, loading, saving, and schema migrations."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from .exceptions import ConfigError
from .utils import get_logger, open_in_editor

logger = get_logger()

CURRENT_CONFIG_VERSION = 1
CONFIG_DIR_NAME = "ai-git-committer"


@dataclass
class ConfigPaths:
    """Dataclass holding all path references for application state."""

    config_dir: Path
    config_file: Path
    history_file: Path
    key_file: Path
    secret_file: Path


def get_config_paths(custom_dir: Optional[Path] = None) -> ConfigPaths:
    """Get standardized configuration file paths.

    Args:
        custom_dir: Optional custom base directory for testing or overriding.

    Returns:
        ConfigPaths object containing all relevant Path instances.
    """
    base_dir = custom_dir or (Path.home() / ".config" / CONFIG_DIR_NAME)
    return ConfigPaths(
        config_dir=base_dir,
        config_file=base_dir / "config.json",
        history_file=base_dir / "history.txt",
        key_file=base_dir / "api.key",
        secret_file=base_dir / "secrets.enc",
    )


def get_default_config() -> Dict[str, Any]:
    """Get default configuration dictionary including schema comment fields.

    Returns:
        Dictionary of default settings.
    """
    return {
        "config_version": CURRENT_CONFIG_VERSION,
        "_comment_version": "Configuration schema version for automatic migrations",
        "default_model": "normal",
        "_comment_default_model": "Default model preset or custom model ID to use (normal, smart, or explicit model name)",
        "temperature": 0.2,
        "_comment_temperature": "Sampling temperature for AI generation (0.0 to 1.0)",
        "max_tokens": 100,
        "_comment_max_tokens": "Maximum tokens allowed in AI response",
        "auto_add": True,
        "_comment_auto_add": "Automatically run git add . before inspecting status",
        "confirm_commit": True,
        "_comment_confirm_commit": "Prompt for interactive confirmation before executing git commit",
        "enforce_conventional_commits": True,
        "_comment_enforce_conventional_commits": "Validate commit messages against Conventional Commits standard",
    }


class ConfigManager:
    """Manager for loading, updating, migrating, and resetting config files."""

    def __init__(self, custom_dir: Optional[Path] = None) -> None:
        """Initialize ConfigManager with path configuration.

        Args:
            custom_dir: Optional custom directory override.
        """
        self.paths = get_config_paths(custom_dir)
        self.ensure_config_directory()

    def ensure_config_directory(self) -> None:
        """Ensure config directory and essential subfiles exist on disk."""
        try:
            self.paths.config_dir.mkdir(parents=True, exist_ok=True)

            if not self.paths.config_file.exists():
                logger.debug("Config file missing. Creating default config at %s", self.paths.config_file)
                self.save_config(get_default_config())

            if not self.paths.history_file.exists():
                logger.debug("Creating empty history file at %s", self.paths.history_file)
                self.paths.history_file.touch(mode=0o600)

        except Exception as err:
            raise ConfigError(f"Failed to initialize configuration directory: {err}") from err

    def load_config(self) -> Dict[str, Any]:
        """Load and validate configuration from config.json. Automatically migrates if needed.

        Returns:
            Dictionary containing current active configuration settings.

        Raises:
            ConfigError: If JSON parsing fails or file is unreadable.
        """
        if not self.paths.config_file.exists():
            default_cfg = get_default_config()
            self.save_config(default_cfg)
            return default_cfg

        try:
            data = json.loads(self.paths.config_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            raise ConfigError(
                f"Invalid JSON format in config file {self.paths.config_file}: {err}"
            ) from err
        except Exception as err:
            raise ConfigError(f"Failed to read config file {self.paths.config_file}: {err}") from err

        # Perform migration check
        migrated_data = self.migrate_config(data)
        return migrated_data

    def save_config(self, config_data: Dict[str, Any]) -> None:
        """Save configuration dictionary to config.json formatted nicely.

        Args:
            config_data: Configuration dict to write.

        Raises:
            ConfigError: If file writing fails.
        """
        try:
            self.paths.config_dir.mkdir(parents=True, exist_ok=True)
            formatted_json = json.dumps(config_data, indent=2) + "\n"
            self.paths.config_file.write_text(formatted_json, encoding="utf-8")
            logger.debug("Saved configuration to %s", self.paths.config_file)
        except Exception as err:
            raise ConfigError(f"Failed to save configuration to {self.paths.config_file}: {err}") from err

    def migrate_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check config_version and migrate data if schema version is outdated.

        Args:
            data: Existing loaded configuration dictionary.

        Returns:
            Updated configuration dictionary.
        """
        version = data.get("config_version", 0)

        if version >= CURRENT_CONFIG_VERSION:
            return data

        logger.info("Migrating configuration schema from version %s to %s", version, CURRENT_CONFIG_VERSION)
        updated = get_default_config()
        # Merge existing user settings over defaults
        for key, value in data.items():
            if not key.startswith("_comment"):
                updated[key] = value

        updated["config_version"] = CURRENT_CONFIG_VERSION
        self.save_config(updated)
        return updated

    def reset_config(self) -> Dict[str, Any]:
        """Reset config.json to fresh default values.

        Returns:
            Default configuration dictionary.
        """
        defaults = get_default_config()
        self.save_config(defaults)
        logger.info("Reset configuration to defaults at %s", self.paths.config_file)
        return defaults

    def set_model(self, model_name: str) -> Dict[str, Any]:
        """Permanently update the default_model setting in config.json.

        Args:
            model_name: New model preset or model ID.

        Returns:
            Updated configuration dictionary.
        """
        config = self.load_config()
        config["default_model"] = model_name
        self.save_config(config)
        return config

    def edit_interactive(self) -> None:
        """Open config.json in user's default text editor."""
        open_in_editor(self.paths.config_file)
