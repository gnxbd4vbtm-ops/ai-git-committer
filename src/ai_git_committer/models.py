"""Model preset definitions and resolution helpers for Groq AI models."""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

from .exceptions import AIError


class ModelPreset(str, Enum):
    """Supported preset model aliases."""

    NORMAL = "normal"
    SMART = "smart"
    GPT_OSS_20B = "gpt-oss-20b"
    GPT_OSS_120B = "gpt-oss-120b"
    QWEN3_32B = "qwen3-32b"
    KIMI_K2_INSTRUCT = "kimi-k2-instruct"
    QWEN3_72B = "qwen3-72b"


@dataclass(frozen=True)
class ModelInfo:
    """Dataclass holding details for a model preset."""

    alias: str
    model_id: str
    description: str


PRESET_MODELS: Dict[str, ModelInfo] = {
    # Convenience presets
    ModelPreset.NORMAL.value: ModelInfo(
        alias="normal",
        model_id="openai/gpt-oss-20b",
        description="Fast and lightweight model suited for routine commit messages.",
    ),
    ModelPreset.SMART.value: ModelInfo(
        alias="smart",
        model_id="openai/gpt-oss-120b",
        description="High-capability reasoning model for complex changes.",
    ),

    # OpenAI GPT-OSS
    ModelPreset.GPT_OSS_20B.value: ModelInfo(
        alias="gpt-oss-20b",
        model_id="openai/gpt-oss-20b",
        description="Fast open-weight reasoning model with strong general-purpose performance.",
    ),
    ModelPreset.GPT_OSS_120B.value: ModelInfo(
        alias="gpt-oss-120b",
        model_id="openai/gpt-oss-120b",
        description="Large open-weight reasoning model for complex tasks and code.",
    ),

    # Qwen
    ModelPreset.QWEN3_32B.value: ModelInfo(
        alias="qwen3-32b",
        model_id="qwen/qwen3-32b",
        description="General-purpose Qwen model with strong reasoning and coding capabilities.",
    ),
    ModelPreset.QWEN3_72B.value: ModelInfo(
        alias="qwen3-72b",
        model_id="qwen/qwen3-72b",
        description="Large Qwen model suited for demanding reasoning and coding tasks.",
    ),

    # Moonshot AI
    ModelPreset.KIMI_K2_INSTRUCT.value: ModelInfo(
        alias="kimi-k2-instruct",
        model_id="moonshotai/kimi-k2-instruct",
        description="Large instruction-following model with strong coding capabilities.",
    ),

}


def resolve_model_id(model_input: str) -> str:
    """Resolve a model preset alias or return the raw model ID string.

    Args:
        model_input: Preset name or explicit Groq model identifier.

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

    # Allow arbitrary valid Groq model IDs.
    return model_input.strip()


def list_available_models(
    current_active_model: Optional[str] = None,
) -> List[str]:
    """Format available Groq models for CLI output.

    Args:
        current_active_model: Currently configured model setting.

    Returns:
        List of formatted model descriptions.
    """
    lines = ["Available Groq Model Presets:"]

    active = (current_active_model or "normal").strip().lower()

    for alias, info in PRESET_MODELS.items():
        is_active = (
            active == alias
            or active == info.model_id.lower()
        )

        status_marker = " (active)" if is_active else ""

        lines.append(
            f"  - {alias:<20} -> {info.model_id:<50}{status_marker}\n"
            f"    Description: {info.description}"
        )

    lines.append(
        "\nYou can also pass any valid explicit Groq model identifier."
    )

    return lines
