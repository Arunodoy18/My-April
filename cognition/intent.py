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
Output: ("OPEN_APP", {"app": "code"})

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

from __future__ import annotations

from typing import Dict, Optional, Tuple

from cognition.normalize import normalize_text, remove_tokens, tokenize
from memory.preferences import get_preference

IntentResult = Tuple[Optional[str], Dict[str, str]]

_OPEN_VERBS: Tuple[str, ...] = ("open", "launch", "start")
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

	open_app_intent = _detect_open_app(filtered_tokens)
	if open_app_intent is not None:
		return open_app_intent

	return None, {}