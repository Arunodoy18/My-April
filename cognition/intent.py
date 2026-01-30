from __future__ import annotations

from typing import Dict, Optional, Tuple

from cognition.normalize import normalize_text, remove_tokens, tokenize
from memory.preferences import get_preference

"""
DAY 4 EXTENSION — LEARN PREFERENCE INTENT

Add support for a new intent: LEARN_PREFERENCE

Trigger patterns:
- "use <app> as my <category>"
- "set my <category> to <app>"

Examples:
Input: "use firefox as my browser"
Output: ("LEARN_PREFERENCE", {"category": "browser", "app": "firefox"})

Input: "use vscode as my editor"
Output: ("LEARN_PREFERENCE", {"category": "editor", "app": "code"})

Rules:
- Reuse normalization utilities
- Do not break OPEN_APP intent
- Deterministic logic only
- Never throw exceptions
"""

"""
PROJECT: APRIL

MODULE: Intent Engine

You are implementing APRIL's intent detection system.

GOAL:
- Convert raw user text into structured intent data
- No AI models
- Deterministic, rule-based logic only

SUPPORTED INTENTS (DAY 2 ONLY):
- OPEN_APP

INPUT:
- raw_text: str (entire user command)

OUTPUT:
- intent_name: str | None
- intent_payload: dict

EXAMPLE OUTPUTS:
Input: "open chrome please"
Output: ("OPEN_APP", {"app": "chrome"})

Input: "can you launch code for me"
Output: ("LEARN_PREFERENCE", {"category": "editor", "app": "code"})

Input: "hello april"
Output: (None, {})

RULES:
- Normalize text (lowercase, trim)
- Ignore filler words (please, can you, for me, etc.)
- Detect synonyms: open, launch, start
- Extract application name safely
- Never throw exceptions

STYLE:
- Clean
- Readable
- Explicit logic
- Easy to extend later

Do not import skills.
Do not execute anything.
This module only understands intent.
"""

IntentResult = Tuple[Optional[str], Dict[str, str]]

_OPEN_VERBS: Tuple[str, ...] = ("open", "launch", "start")
_LEARN_VERBS: Tuple[str, ...] = ("use", "set")
_DANGEROUS_KEYWORDS: Tuple[str, ...] = (
	"delete",
	"remove",
	"shutdown",
	"restart",
	"kill",
	"close all",
	"terminate",
	"destroy",
	"wipe",
	"erase",
)
_FILLER_WORDS: Tuple[str, ...] = (
	"please",
	"can",
	"you",
	"could",
	"for",
	"me",
	"kindly",
	"would",
	"mind",
)

def _detect_dangerous_action(raw_text: str) -> Optional[IntentResult]:
	"""Detect commands with dangerous keywords for confirmation."""
	if not raw_text:
		return None
	
	text_lower = raw_text.lower()
	for keyword in _DANGEROUS_KEYWORDS:
		if keyword in text_lower:
			return "DANGEROUS_ACTION", {"raw": raw_text}
	
	return None


def _detect_learn_preference(tokens: Tuple[str, ...]) -> Optional[IntentResult]:
	"""Detect LEARN_PREFERENCE intent and extract category/app payload."""
	if len(tokens) < 3:
		return None

	verb = tokens[0]
	if verb not in _LEARN_VERBS:
		return None

	if verb == "use":
		# Find "as" keyword to split app name from category
		try:
			as_index = tokens.index("as")
		except ValueError:
			return None
		
		if as_index < 2:  # Need at least "use <app> as"
			return None
			
		app_tokens = tokens[1:as_index]
		app_name = " ".join(app_tokens)
		
		# Pattern: "use <app> as my <category>"
		if as_index + 2 < len(tokens) and tokens[as_index + 1] == "my":
			category = tokens[as_index + 2]
			return "LEARN_PREFERENCE", {"category": category, "app": app_name}
		# Pattern: "use <app> as <category>"
		elif as_index + 1 < len(tokens):
			category = tokens[as_index + 1]
			return "LEARN_PREFERENCE", {"category": category, "app": app_name}
			
	elif verb == "set":
		# Find "to" keyword to split category from app name
		try:
			to_index = tokens.index("to")
		except ValueError:
			return None
			
		if to_index < 2:  # Need at least "set <category> to"
			return None
			
		# Pattern: "set my <category> to <app>"
		if tokens[1] == "my" and to_index == 3:
			category = tokens[2]
			app_tokens = tokens[to_index + 1:]
			app_name = " ".join(app_tokens)
			return "LEARN_PREFERENCE", {"category": category, "app": app_name}
		# Pattern: "set <category> to <app>"
		elif to_index == 2:
			category = tokens[1]
			app_tokens = tokens[to_index + 1:]
			app_name = " ".join(app_tokens)
			return "LEARN_PREFERENCE", {"category": category, "app": app_name}

	return None


def _detect_open_app(tokens: Tuple[str, ...]) -> Optional[IntentResult]:
	"""Detect OPEN_APP intent and extract application payload."""
	if not tokens:
		return None

	verb = tokens[0]
	if verb not in _OPEN_VERBS:
		return None

	remainder = tokens[1:]
	if not remainder:
		return None

	# Handle "my category" patterns
	if remainder[0] == "my" and len(remainder) > 1:
		category = remainder[1]
		app_name = get_preference(category)
		if app_name:
			return "OPEN_APP", {"app": app_name, "category": category}

	# Handle direct category lookup
	app_token = remainder[0]
	if not app_token:
		return None

	# Try as preference category first
	preferred_app = get_preference(app_token)
	if preferred_app:
		return "OPEN_APP", {"app": preferred_app, "category": app_token}

	# Fallback to direct app name
	return "OPEN_APP", {"app": app_token}


def parse_intent(raw_text: str) -> IntentResult:
	"""Convert free-form text into intent classification and payload."""
	normalized = normalize_text(raw_text)
	if not normalized:
		return None, {}

	tokens = tokenize(normalized)
	if not tokens:
		return None, {}

	filtered_tokens = remove_tokens(tokens, _FILLER_WORDS)
	if not filtered_tokens:
		return None, {}

	# Check for dangerous actions first (before parsing)
	dangerous_intent = _detect_dangerous_action(raw_text)
	if dangerous_intent is not None:
		return dangerous_intent

	# Try LEARN_PREFERENCE intent
	learn_intent = _detect_learn_preference(filtered_tokens)
	if learn_intent is not None:
		return learn_intent

	# Try OPEN_APP intent
	open_app_intent = _detect_open_app(filtered_tokens)
	if open_app_intent is not None:
		return open_app_intent

	return None, {}