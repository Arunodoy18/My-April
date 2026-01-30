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

        if intent_name == "OPEN_APP":
            if isinstance(payload, dict):
                app_name = payload.get("app", "")
                category = payload.get("category", "")
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
