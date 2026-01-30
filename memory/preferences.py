"""
DAY 4 STABILIZATION — PREFERENCES MODULE

You are fixing APRIL's preference memory module.

REQUIREMENTS:
- Remove or relocate any `from __future__ import annotations`
- Ensure no SyntaxError can occur
- Use a single in-memory dictionary
- Keys must be lowercase ("browser", "editor")

IMPLEMENT EXACTLY:
- get_preference(key: str) -> str | None
- set_preference(key: str, value: str) -> None

RULES:
- Normalize keys using key.strip().lower()
- Never raise exceptions
- Do not validate app existence
- Keep file minimal
"""

_preferences = {
    "editor": "code",
    "browser": "chrome",
}


def get_preference(key: str) -> str:
    """Return the configured preference for a category."""
    if not isinstance(key, str):
        return ""
    
    normalized_key = key.strip().lower()
    if not normalized_key:
        return ""
    
    return _preferences.get(normalized_key, "")


def set_preference(key: str, value: str) -> None:
    """Update a preference value in the in-memory store."""
    if not isinstance(key, str) or not isinstance(value, str):
        return
    
    normalized_key = key.strip().lower()
    normalized_value = value.strip().lower()
    if not normalized_key or not normalized_value:
        return
    
    _preferences[normalized_key] = normalized_value