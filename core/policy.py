"""
PROJECT: APRIL

MODULE: Action Policy Engine

GOAL:
- Decide whether an action is safe to execute immediately
- Enforce confirmation for risky actions

ACTION LEVELS:
- SAFE
- CONFIRM_REQUIRED

INITIAL RULES:
SAFE actions:
- open application
- read-only actions

CONFIRM_REQUIRED actions:
- delete
- remove
- shutdown
- restart
- kill
- close all

INPUT:
- intent_name: str
- payload: dict

OUTPUT:
- policy: str ("SAFE" or "CONFIRM_REQUIRED")

RULES:
- Deterministic logic only
- Keyword-based classification
- Never throw exceptions
- Easy to extend later
"""

from typing import Dict, Any

# Safe intents that can execute immediately
_SAFE_INTENTS = {
    "OPEN_APP",
    "LEARN_PREFERENCE",
}

# Intents that always require confirmation
_CONFIRM_INTENTS = {
    "DANGEROUS_ACTION",
}

# Dangerous keywords that require confirmation
_DANGEROUS_KEYWORDS = {
    "delete",
    "remove", 
    "shutdown",
    "restart",
    "kill",
    "close",
    "exit",
    "quit",
    "stop",
    "terminate",
    "destroy",
    "wipe",
    "format",
    "erase",
}


def classify_action(intent_name: str, payload: Dict[str, Any]) -> str:
    """Determine if an action requires confirmation before execution."""
    if not isinstance(intent_name, str):
        return "CONFIRM_REQUIRED"
    
    # Known safe intents
    if intent_name in _SAFE_INTENTS:
        return "SAFE"
    
    # Known confirmation-required intents
    if intent_name in _CONFIRM_INTENTS:
        return "CONFIRM_REQUIRED"
    
    # Check for dangerous keywords in intent name
    intent_lower = intent_name.lower()
    for keyword in _DANGEROUS_KEYWORDS:
        if keyword in intent_lower:
            return "CONFIRM_REQUIRED"
    
    # Check for dangerous keywords in payload values
    if isinstance(payload, dict):
        for value in payload.values():
            if isinstance(value, str):
                value_lower = value.lower()
                for keyword in _DANGEROUS_KEYWORDS:
                    if keyword in value_lower:
                        return "CONFIRM_REQUIRED"
    
    # Unknown intents default to requiring confirmation for safety
    return "CONFIRM_REQUIRED"


def get_confirmation_message(intent_name: str, payload: Dict[str, Any]) -> str:
    """Generate a confirmation prompt for risky actions."""
    if intent_name == "DANGEROUS_ACTION":
        return "This action needs confirmation. Proceed? (yes/no)"
    
    if intent_name == "OPEN_APP":
        app = payload.get("app", "application") if isinstance(payload, dict) else "application"
        return f"Are you sure you want to open {app}?"
    
    return f"Are you sure you want to execute this action: {intent_name}?"