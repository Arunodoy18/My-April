"""
DAY 8 EXTENSION — PERSISTENT ACTION HISTORY

Upgrade action history to persist across APRIL restarts.

REQUIREMENTS:
- Store action history in memory/action_history.json
- Load history at module import
- Save history after each action is recorded
- Maintain rolling window (max 100 actions)

IMPLEMENT:
- _load_history()
- _save_history()
- record_action(action_signature: str) -> None
- get_history() -> list[str]
- detect_pattern(last_action: str) -> str | None

RULES:
- File path relative to this module
- Never raise exceptions outward
- Fail safely (empty history on error)
- Keep rolling window to prevent infinite growth
"""

import json
from pathlib import Path
from typing import Optional

_MODULE_DIR = Path(__file__).parent
_HISTORY_FILE = _MODULE_DIR / "action_history.json"
_MAX_HISTORY_SIZE = 100

_action_history = []


def _load_history():
    """Load action history from JSON file."""
    global _action_history
    try:
        if _HISTORY_FILE.exists():
            with open(_HISTORY_FILE, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                if isinstance(loaded, list):
                    _action_history = loaded[-_MAX_HISTORY_SIZE:]  # Keep only recent actions
                else:
                    _action_history = []
        else:
            _action_history = []
    except Exception:
        _action_history = []


def _save_history():
    """Save current action history to JSON file."""
    try:
        _MODULE_DIR.mkdir(parents=True, exist_ok=True)
        with open(_HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(_action_history, f, indent=2)
    except Exception:
        pass


def record_action(action_signature: str) -> None:
    """Record an executed action and persist to disk."""
    if not isinstance(action_signature, str) or not action_signature.strip():
        return
    
    global _action_history
    _action_history.append(action_signature.strip())
    
    # Maintain rolling window
    if len(_action_history) > _MAX_HISTORY_SIZE:
        _action_history.pop(0)
    
    _save_history()


def get_history() -> list:
    """Return current action history."""
    return _action_history.copy()


def detect_pattern(last_action: str) -> Optional[str]:
    """Detect if there's a common pattern following the last action."""
    if len(_action_history) < 4:
        return None
    
    # Look for pattern: last_action → next_action
    pattern_candidates = {}
    
    for i in range(len(_action_history) - 1):
        if _action_history[i] == last_action:
            next_action = _action_history[i + 1]
            if next_action != last_action:  # Don't suggest same action
                pattern_candidates[next_action] = pattern_candidates.get(next_action, 0) + 1
    
    # If any pattern occurs 3+ times, suggest it
    for action, count in pattern_candidates.items():
        if count >= 3:
            return action
    
    return None


# Load history when module is imported
_load_history()