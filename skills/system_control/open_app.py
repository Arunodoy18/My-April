"""
PROJECT: APRIL


SKILL NAME: Open Application


You are implementing APRIL's first real system skill.


CONTEXT:
APRIL is a local desktop assistant.
This skill allows APRIL to open applications by name
in a safe, controlled, predictable way.


GOAL:
- Open common desktop applications by name
- Work on Windows (for now)
- Never crash APRIL
- Never execute arbitrary commands


INPUT:
- app_name: str (example: "chrome", "code", "notepad")


OUTPUT:
- A short status message for APRIL to speak


REQUIREMENTS:
- Use Python standard library only
- Use subprocess or os safely
- Maintain a controlled mapping of allowed apps
- Do NOT allow raw command execution
- Catch and handle all exceptions


SAFETY RULES (CRITICAL):
- No shell=True
- No user-provided strings passed directly to OS
- Only open apps from a predefined whitelist


STYLE:
- Clean
- Minimal
- Professional


APRIL should say things like:
"Opening Chrome."
or
"I couldn't find that application."


Return values only. Do not print.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from typing import Optional, Sequence, TypedDict


class AppEntry(TypedDict):
	"""Approved application definition."""

	label: str
	candidates: Sequence[str]


_ALLOWED_APPS: dict[str, AppEntry] = {
	"notepad": {
		"label": "Notepad",
		"candidates": ("notepad.exe",),
	},
	"calculator": {
		"label": "Calculator",
		"candidates": ("calc.exe",),
	},
	"chrome": {
		"label": "Chrome",
		"candidates": (
			r"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
			r"C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
			"chrome.exe",
		),
	},
	"edge": {
		"label": "Microsoft Edge",
		"candidates": (
			r"C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
			r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
			"msedge.exe",
		),
	},
	"code": {
		"label": "Visual Studio Code",
		"candidates": (
			r"C:\\Program Files\\Microsoft VS Code\\Code.exe",
			r"C:\\Program Files (x86)\\Microsoft VS Code\\Code.exe",
			r"C:\\Users\\%USERNAME%\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
			"code.exe",
		),
	},
}


def _expand_environment(path: str) -> str:
	"""Expand environment variables in whitelisted paths."""
	return os.path.expandvars(path)


def _resolve_executable(options: Sequence[str]) -> Optional[str]:
	"""Return first existing executable path from the approved list."""
	for option in options:
		expanded = _expand_environment(option)
		if os.path.isabs(expanded):
			if os.path.exists(expanded):
				return expanded
		else:
			resolved = shutil.which(expanded)
			if resolved:
				return resolved
	return None


def open_application(app_name: str) -> str:
	"""Open a whitelisted application by name and return APRIL's spoken status."""
	if not isinstance(app_name, str):
		return "I couldn't find that application."

	key = app_name.strip().lower()
	if not key:
		return "I couldn't find that application."

	app_entry = _ALLOWED_APPS.get(key)
	if not app_entry:
		return "I couldn't find that application."

	executable = _resolve_executable(app_entry["candidates"])
	if not executable:
		return "I couldn't find that application."

	try:
		subprocess.Popen([executable], start_new_session=True)
	except FileNotFoundError:
		return "I couldn't find that application."
	except OSError:
		return "Opening failed safely."

	return f"Opening {app_entry['label']}."