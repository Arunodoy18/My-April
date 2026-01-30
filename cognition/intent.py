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

import re
from typing import Dict, Iterable, Optional, Tuple

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

_TOKEN_SPLIT_RE = re.compile(r"\s+")


def _normalize(text: str) -> str:
	"""Sanitize raw text for downstream matching."""
	if not isinstance(text, str):
		return ""
	return text.strip().lower()


def _tokenize(text: str) -> Iterable[str]:
	"""Split text into lowercase tokens without empty entries."""
	if not text:
		return ()
	return tuple(token for token in _TOKEN_SPLIT_RE.split(text) if token)


def _remove_fillers(tokens: Iterable[str]) -> Tuple[str, ...]:
	"""Strip filler words while preserving order."""
	filler_set = set(_FILLER_WORDS)
	return tuple(token for token in tokens if token not in filler_set)


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

	app_token = remainder[0]
	if not app_token:
		return None

	return "OPEN_APP", {"app": app_token}


def parse_intent(raw_text: str) -> IntentResult:
	"""Convert free-form text into intent classification and payload."""
	normalized = _normalize(raw_text)
	if not normalized:
		return None, {}

	tokens = _tokenize(normalized)
	if not tokens:
		return None, {}

	filtered_tokens = _remove_fillers(tokens)
	if not filtered_tokens:
		return None, {}

	open_app_intent = _detect_open_app(filtered_tokens)
	if open_app_intent is not None:
		return open_app_intent

	return None, {}