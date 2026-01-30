"""
PROJECT: APRIL

MODULE: User Preferences Memory

GOAL:
- Store and retrieve user-specific defaults
- Keep it simple and local
- No databases, no cloud

RESPONSIBILITIES:
- Get preferred application for a category (editor, browser)
- Set preferred application explicitly
- Provide safe defaults if not set

EXAMPLE:
get_preference("editor") -> "code"
get_preference("browser") -> "chrome"

REQUIREMENTS:
- Use an in-memory dict for now
- Easy to upgrade to disk later
- Never raise exceptions

STYLE:
- Clean
- Explicit
- Minimal
"""

from __future__ import annotations

from typing import Dict

_DEFAULTS: Dict[str, str] = {
	"editor": "code",
	"browser": "chrome",
}

_preferences: Dict[str, str] = {}


def get_preference(category: str) -> str:
	"""Return the configured preference or a safe default."""
	if not isinstance(category, str):
		return ""

	key = category.strip().lower()
	if not key:
		return ""

	return _preferences.get(key, _DEFAULTS.get(key, ""))


def set_preference(category: str, value: str) -> None:
	"""Persist a preference value safely in memory."""
	if not isinstance(category, str) or not isinstance(value, str):
		return

	key = category.strip().lower()
	val = value.strip().lower()
	if not key or not val:
		return

	_preferences[key] = val