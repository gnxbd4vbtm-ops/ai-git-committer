"""Model preset definitions and resolution helpers for Groq AI models."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .exceptions import AIError


class ModelPreset(str, Enum):
    """Supported preset model aliases."""

    NORMAL = "normal"
    SMART = "smart"


@dataclass(frozen=True)
class ModelInfo:
    """Dataclass holding details for a model preset."""

    alias: str
    model_id: str
    description: str


PRESET_MODELS: Dict[str, ModelInfo] = {
    ModelPreset.NORMAL.value: ModelInfo(
        alias="normal",
        model_id="llama-3.1-8b-instant",
        description="Fast and lightweight model suited for quick routine commit messages.",
    ),
    ModelPreset.SMART.value: ModelInfo(
        alias="smart",
        model_id="llama-3.3-70b-versatile",
        description="High-capability model for complex changes requiring deep understanding.",
    ),
}


def resolve_model_id(model_input: str) -> str:
    """Resolve a model preset alias or return the raw model ID string.

    Args:
        model_input: Preset name ('normal', 'smart') or explicit Groq model string.

    Returns:
        The actual Groq API model ID string.

    Raises:
        AIError: If model_input is empty.
    """
    if not model_input or not model_input.strip():
        raise AIError("Model identifier cannot be empty.")

    cleaned = model_input.strip().lower()
    if cleaned in PRESET_MODELS:
        return PRESET_MODELS[cleaned].model_id

    # Return raw model name if user provided a custom model ID
    return model_input.strip()


def list_available_models(current_active_model: Optional[str] = None) -> List[str]:
    """Format available model presets for CLI output.

    Args:
        current_active_model: Currently configured model setting for highlighting.

    Returns:
        List of formatted string lines displaying available models.
    """
    lines = ["Available Groq Model Presets:"]
    active = (current_active_model or "normal").strip()

    for alias, info in PRESET_MODELS.items():
        is_active = (active == alias) or (active.lower() == info.model_id.lower())
        status_marker = " (active)" if is_active else ""
        lines.append(
            f"  - {alias:<8} -> {info.model_id:<25}{status_marker}\n"
            f"    Description: {info.description}"
        )

    lines.append("\nYou can also pass any valid explicit Groq model identifier.")
    return lines
