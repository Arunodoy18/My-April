"""
DAY 2 INTEGRATION INSTRUCTION:

Integrate cognition.intent.detect_intent into the command flow.

Flow:
1. Receive raw user input
2. Send it to detect_intent
3. If intent == OPEN_APP → route to open_app skill
4. If intent is None → respond politely

Do NOT change skill implementations.
Do NOT break Day-1 behavior.
"""
"""
DAY 4 STABILIZATION — FIX ALL CURRENT ISSUES

You are stabilizing APRIL's learning and preference system.

PROBLEMS TO FIX:
1. Preferences sometimes fail to resolve (e.g., "open browser" after setting browser)
2. Category keys ("browser", "editor") are inconsistently normalized
3. Preference resolution must be deterministic and reliable
4. Do NOT break any Day 1–4 functionality

MANDATORY FIXES:

A. CATEGORY NORMALIZATION
- Whenever reading or writing a preference category:
  - category = category.strip().lower()
- This must be applied consistently in ALL paths

B. PREFERENCE RESOLUTION FLOW (OPEN_APP)
When handling OPEN_APP intent:
1. Read payload["app"]
2. Normalize it
3. If app is "browser" or "editor":
   - Resolve via memory.preferences.get_preference(app)
4. If resolution returns None:
   - Respond: "I don't have a <category> configured."
   - Do NOT call open_app
5. If resolved:
   - Call open_app(resolved_app)

C. LEARN_PREFERENCE FLOW
When handling LEARN_PREFERENCE intent:
1. Normalize category
2. Call set_preference(category, app)
3. Confirm learning using APRIL voice
4. Do NOT validate app existence here

STRICT RULES:
- Do NOT modify open_app.py
- Do NOT add new intents
- Do NOT add persistence yet
- Do NOT add multi-word parsing
- Keep logic small and explicit
- Preserve all existing tests and behaviors

APRIL'S VOICE:
- Calm
- Acknowledging
- Deterministic
"""

"""Entry point for APRIL day-1 command execution backbone."""

import sys
from typing import Optional, Callable

from cognition.intent import parse_intent

_ALLOWED_APP_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.")


def _print_april(message: str) -> None:
    """Emit a response in APRIL's required voice."""
    print(f"APRIL: {message}")


def _sanitize_app_name(raw: str) -> Optional[str]:
    """Return a safe app name or None when validation fails."""
    candidate = raw.strip()
    if not candidate:
        return None
    if any(ch not in _ALLOWED_APP_CHARS for ch in candidate):
        return None
    return candidate


def _handle_open(command_body: str) -> None:
    """Route the open command to the system control skill with safety checks."""
    app_name = _sanitize_app_name(command_body)
    if app_name is None:
        _print_april("need a plain app name.")
        return
    _handle_open_with_category(app_name, "")


def _handle_open_with_category(app_name: str, category: str) -> None:
    """Route the open command with optional category context."""
    if not app_name:
        _print_april("need an application name.")
        return

    try:
        from skills.system_control import open_app  # type: ignore
    except Exception:
        _print_april("open skill offline.")
        return

    open_application: Optional[Callable[[str, str], Optional[str]]]
    open_application = getattr(open_app, "open_application", None)
    if not callable(open_application):
        _print_april("open skill incomplete.")
        return

    try:
        message = open_application(app_name, category)
    except Exception:
        _print_april("open failed safely.")
        return

    if message:
        _print_april(message)
    else:
        _print_april(f"opening {app_name}.")


def _loop() -> None:
    """Main command loop handling user input and routing."""
    _print_april("online. ready.")

    while True:
        try:
            command = input("You> ")
        except (EOFError, KeyboardInterrupt):
            _print_april("standing down.")
            break
        except Exception:
            _print_april("input channel error.")
            break

        command = command.strip()
        if not command:
            _print_april("awaiting command.")
            continue

        lowered = command.lower()
        if lowered in {"exit", "quit"}:
            _print_april("shutting down.")
            break

        intent_name, payload = parse_intent(command)

        """
        DAY 4 INTEGRATION — LIVE LEARNING

        Handle new intent: LEARN_PREFERENCE

        Flow:
        1. Extract category and app from payload
        2. Call memory.preferences.set_preference(category, app)
        3. Respond as APRIL acknowledging learning
        4. Do NOT call open_app here

        Example response:
        "Okay. I'll use Firefox as your browser from now on."

        Rules:
        - Do not restart APRIL
        - Preference must apply immediately
        - Preserve Day 1–3 behavior
        """

        if intent_name == "LEARN_PREFERENCE":
            if isinstance(payload, dict):
                category = payload.get("category", "").strip().lower()
                app = payload.get("app", "").strip().lower()
                if category and app:
                    try:
                        from memory.preferences import set_preference
                        set_preference(category, app)
                        _print_april(f"Okay. I'll use {app} as your {category} from now on.")
                    except Exception:
                        _print_april("I couldn't learn that preference.")
                else:
                    _print_april("I need both an app and category to learn.")
            else:
                _print_april("I couldn't understand that preference.")
            continue

        if intent_name == "OPEN_APP":
            if isinstance(payload, dict):
                app_name = payload.get("app", "").strip().lower()
                category = payload.get("category", "").strip().lower()
                
                # If this is a direct category lookup, resolve it
                if not category and app_name in {"browser", "editor"}:
                    try:
                        from memory.preferences import get_preference
                        resolved_app = get_preference(app_name)
                        if resolved_app:
                            _handle_open_with_category(resolved_app, app_name)
                        else:
                            _print_april(f"I don't have a {app_name} configured.")
                    except Exception:
                        _print_april("preference lookup failed safely.")
                else:
                    _handle_open_with_category(app_name, category)
            else:
                _handle_open("")
            continue

        _print_april("I can't do that yet.")


def main() -> None:
    """Protect the main loop against unexpected faults."""
    try:
        _loop()
    except Exception:
        _print_april("critical fault. standing down.")
        sys.exit(1)


if __name__ == "__main__":
    main()
