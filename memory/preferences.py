"""
DAY 5 — PERSISTENT PREFERENCES

Upgrade the preference system to persist data across restarts.

REQUIREMENTS:
- Store preferences in a local JSON file (preferences.json)
- Load preferences at module import
- Save preferences every time set_preference is called
- If file does not exist, start with defaults

DEFAULTS:
- browser -> chrome
- editor -> code

IMPLEMENT:
- _load_preferences()
- _save_preferences()
- get_preference(key)
- set_preference(key, value)

RULES:
- File path must be relative to this module
- Keys must be normalized (strip + lowercase)
- Never raise exceptions outward
- Fail safely (fallback to defaults)

Do NOT add encryption yet.
Do NOT change public function signatures.
"""

import json
import os
from pathlib import Path

# Get the directory where this module lives
_MODULE_DIR = Path(__file__).parent
_PREFERENCES_FILE = _MODULE_DIR / "preferences.json"

# Default preferences
_DEFAULTS = {
    "browser": "chrome",
    "editor": "code",
}

# Active preferences storage
_preferences = {}


def _load_preferences():
    """Load preferences from JSON file, fall back to defaults if file missing or corrupt."""
    global _preferences
    try:
        if _PREFERENCES_FILE.exists():
            with open(_PREFERENCES_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                if isinstance(loaded, dict):
                    _preferences = loaded
                else:
                    _preferences = _DEFAULTS.copy()
        else:
            _preferences = _DEFAULTS.copy()
    except Exception:
        # Any error loading file -> use defaults
        _preferences = _DEFAULTS.copy()


def _save_preferences():
    """Save current preferences to JSON file, fail silently on errors."""
    try:
        # Ensure directory exists
        _MODULE_DIR.mkdir(parents=True, exist_ok=True)
        with open(_PREFERENCES_FILE, 'w', encoding='utf-8') as f:
            json.dump(_preferences, f, indent=2)
    except Exception:
        # Fail silently - preference changes will be lost on restart but won't crash
        pass


def get_preference(key: str) -> str:
    """Return the configured preference for a category."""
    if not isinstance(key, str):
        return ""
    
    normalized_key = key.strip().lower()
    if not normalized_key:
        return ""
    
    return _preferences.get(normalized_key, "")


def set_preference(key: str, value: str) -> None:
    """Update a preference value and persist to disk immediately."""
    if not isinstance(key, str) or not isinstance(value, str):
        return
    
    normalized_key = key.strip().lower()
    normalized_value = value.strip().lower()
    if not normalized_key or not normalized_value:
        return
    
    _preferences[normalized_key] = normalized_value
    _save_preferences()


# Load preferences when module is imported
_load_preferences()