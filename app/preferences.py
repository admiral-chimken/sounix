"""
preferences.py
------------------------
Feature #7 for Sounix: customization settings.

Covers:
- Choosing which installed Ollama model to use
- Toggling which features run automatically
- Adjusting Threat Detection sensitivity
- Setting a custom background image
"""

import os
import shutil

from memory import recall, remember
from ollama_client import get_installed_models

DEFAULT_MODEL_KEY = "preferred_ollama_model"
FEATURE_TOGGLE_KEY = "enabled_features"
SENSITIVITY_KEY = "threat_sensitivity"
BACKGROUND_PATH = "app/assets/background.jpg"

TOGGLEABLE_FEATURES = [
    "predictive_analytics",
    "threat_detection",
    "security_news",
    "adblock",
]


def list_available_models():
    return get_installed_models()


def set_preferred_model(model_name):
    available = list_available_models()
    if model_name not in available:
        return (
            f"Sounix: '{model_name}' is not an installed model.\n"
            f"Available models: {', '.join(available)}"
        )

    remember(DEFAULT_MODEL_KEY, model_name)
    return f"Sounix: Preferred model set to {model_name}."


def get_preferred_model():
    return recall(DEFAULT_MODEL_KEY)


def show_model_status():
    current = get_preferred_model()
    available = list_available_models()

    lines = ["Sounix: Ollama Model Settings"]
    lines.append(f"Current preference: {current if current else '(using default)'}")
    lines.append(f"Available models: {', '.join(available) if available else '(none found)'}")
    lines.append("\nUse: set model <name>")

    return "\n".join(lines)


def _load_toggles():
    toggles = recall(FEATURE_TOGGLE_KEY)
    if toggles is None:
        toggles = {f: True for f in TOGGLEABLE_FEATURES}
        remember(FEATURE_TOGGLE_KEY, toggles)
    return toggles


def toggle_feature(feature_name):
    feature_name = feature_name.strip().lower()
    if feature_name not in TOGGLEABLE_FEATURES:
        return (
            f"Sounix: Unknown feature '{feature_name}'.\n"
            f"Available: {', '.join(TOGGLEABLE_FEATURES)}"
        )

    toggles = _load_toggles()
    toggles[feature_name] = not toggles.get(feature_name, True)
    remember(FEATURE_TOGGLE_KEY, toggles)

    state = "ON" if toggles[feature_name] else "OFF"
    return f"Sounix: {feature_name} is now {state}."


def is_feature_enabled(feature_name):
    toggles = _load_toggles()
    return toggles.get(feature_name, True)


def show_feature_status():
    toggles = _load_toggles()
    lines = ["Sounix: Feature Toggles"]
    for name, enabled in toggles.items():
        mark = "[ON]" if enabled else "[OFF]"
        lines.append(f"  {mark} {name}")
    lines.append("\nUse: toggle feature <name>")
    return "\n".join(lines)


def set_sensitivity(level):
    level = level.strip().lower()
    if level not in {"low", "normal", "high"}:
        return "Sounix: Use: set sensitivity low|normal|high"

    remember(SENSITIVITY_KEY, level)
    return f"Sounix: Threat Detection sensitivity set to {level}."


def get_sensitivity():
    level = recall(SENSITIVITY_KEY)
    return level if level else "normal"


def set_background_image(source_path):
    source_path = source_path.strip().strip('"').strip("'")
    source_path = os.path.expanduser(source_path)

    if not os.path.exists(source_path):
        return f"Sounix: Could not find file: {source_path}"

    try:
        shutil.copy(source_path, BACKGROUND_PATH)
        return (
            "Sounix: Background image updated. "
            "Restart Sounix to see the new background."
        )
    except Exception as e:
        return f"Sounix: Could not set background image: {e}"
