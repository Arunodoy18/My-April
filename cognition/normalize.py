"""
PROJECT: APRIL

MODULE: Text Normalization Utilities

PURPOSE:
- Provide shared normalization helpers for intent parsing and routing.
- Keep logic deterministic, transparent, and extendable.
"""

from __future__ import annotations

import re
from typing import Iterable, Tuple

_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(raw: str) -> str:
	"""Lowercase and trim text safely."""
	if not isinstance(raw, str):
		return ""
	return raw.strip().lower()


def tokenize(raw: str) -> Tuple[str, ...]:
	"""Split text into tokens using whitespace rules."""
	normalized = normalize_text(raw)
	if not normalized:
		return ()
	return tuple(token for token in _WHITESPACE_RE.split(normalized) if token)


def remove_tokens(tokens: Iterable[str], removals: Iterable[str]) -> Tuple[str, ...]:
	"""Return tokens excluding any in the removal set."""
	removal_set = {token for token in removals if isinstance(token, str)}
	return tuple(token for token in tokens if token not in removal_set)
