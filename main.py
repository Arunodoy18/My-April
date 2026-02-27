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

"""
DAY 7 INTEGRATION — CONFIRMATION FLOW

Add a confirmation mechanism.

FLOW:
1. When an intent is detected:
   - Ask policy engine for action policy
2. If policy == SAFE:
   - Execute immediately
3. If policy == CONFIRM_REQUIRED:
   - Ask user for confirmation
   - Store pending action in memory
4. If user replies "yes":
   - Execute stored action
5. If user replies "no":
   - Discard action and respond politely

RULES:
- Only one pending action at a time
- Confirmation is session-scoped
- Do NOT persist pending actions
- Do NOT break existing commands
"""

"""Entry point for APRIL day-1 command execution backbone."""

import sys
from typing import Optional, Callable, Dict, Any

from cognition.intent import parse_intent
from core.policy import classify_action, get_confirmation_message
from core.personality import (
    detect_gratitude,
    detect_social_phrase,
    get_social_response,
    apply_tone,
    set_emotional_state,
)
from core.voice import speak, listen, is_tts_available, is_stt_available
from memory.action_history import record_action, detect_pattern

_ALLOWED_APP_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.")

# Voice mode toggle - set to True to enable voice I/O
VOICE_ENABLED = True

# Confirmation state - session scoped, not persisted
_pending_action = None  # type: Optional[Dict[str, Any]]

# Suggestion state - session scoped, not persisted
_suggested_action = None  # type: Optional[Dict[str, Any]]


def _print_april(message: str) -> None:
    """Emit a response in APRIL's required voice with emotional tone."""
    toned_message = apply_tone(message, context="")
    print(f"APRIL: {toned_message}")
    
    # Speak if voice mode is enabled
    if VOICE_ENABLED:
        speak(toned_message)


def _print_april_with_context(message: str, context: str) -> None:
    """Emit a response with specific emotional context."""
    toned_message = apply_tone(message, context=context)
    print(f"APRIL: {toned_message}")
    
    # Speak if voice mode is enabled
    if VOICE_ENABLED:
        speak(toned_message)


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


def _execute_action(intent_name: str, payload: Dict[str, Any]) -> None:
    """Execute a confirmed action based on intent type."""
    global _suggested_action
    
    if intent_name == "DANGEROUS_ACTION":
        _print_april("Confirmed. This action is not implemented yet.")
        return
    
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

    elif intent_name == "OPEN_APP":
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
                        # Record this action for pattern detection
                        action_sig = f"open {app_name}"
                        record_action(action_sig)
                        # Check for patterns
                        suggested_next = detect_pattern(action_sig)
                        if suggested_next and not _suggested_action:
                            # Parse the suggested action
                            _suggested_action = {
                                "intent_name": "OPEN_APP",
                                "payload": {"app": suggested_next.replace("open ", "")}
                            }
                            _print_april(f"You usually {suggested_next} after this. Want me to do that now?")
                    else:
                        _print_april(f"I don't have a {app_name} configured.")
                except Exception:
                    _print_april("preference lookup failed safely.")
            else:
                _handle_open_with_category(app_name, category)
                # Record this action for pattern detection
                if category:
                    action_sig = f"open {category}"
                else:
                    action_sig = f"open {app_name}"
                record_action(action_sig)
                # Check for patterns
                suggested_next = detect_pattern(action_sig)
                if suggested_next and not _suggested_action:
                    # Parse the suggested action
                    _suggested_action = {
                        "intent_name": "OPEN_APP",
                        "payload": {"app": suggested_next.replace("open ", "")}
                    }
                    _print_april(f"You usually {suggested_next} after this. Want me to do that now?")
        else:
            _handle_open("")
    else:
        _print_april("I can't do that yet.")


def _handle_confirmation_response(response: str) -> None:
    """Handle yes/no confirmation responses."""
    global _pending_action
    
    response_lower = response.strip().lower()
    
    if response_lower in {"yes", "y", "ok", "okay", "sure", "confirm"}:
        if _pending_action:
            intent_name = _pending_action.get("intent_name")
            payload = _pending_action.get("payload", {})
            _pending_action = None  # Clear pending action
            _execute_action(intent_name, payload)
        else:
            _print_april("I don't have anything to confirm.")
    elif response_lower in {"no", "n", "cancel", "never mind", "nevermind"}:
        if _pending_action:
            _pending_action = None  # Clear pending action
            _print_april("Okay. I won't do that.")
        else:
            _print_april("I don't have anything to cancel.")
    else:
        if _pending_action:
            _print_april("Please answer yes or no.")
        else:
            _print_april("I can't do that yet.")


def _handle_suggestion_response(response: str) -> None:
    """Handle yes/no suggestion responses."""
    global _suggested_action
    
    response_lower = response.strip().lower()
    
    if response_lower in {"yes", "y", "ok", "okay", "sure"}:
        if _suggested_action:
            intent_name = _suggested_action.get("intent_name")
            payload = _suggested_action.get("payload", {})
            _suggested_action = None  # Clear suggestion
            _execute_action(intent_name, payload)
        else:
            _print_april("I don't have anything to suggest.")
    elif response_lower in {"no", "n", "not now", "nope"}:
        if _suggested_action:
            _suggested_action = None  # Clear suggestion
            _print_april("Alright.")
        else:
            _print_april("Alright.")
    else:
        if _suggested_action:
            _print_april("Please answer yes or no.")
        else:
            _print_april("I can't do that yet.")


def _loop() -> None:
    """Main command loop handling user input and routing."""
    global _pending_action, _suggested_action
    
    # Check voice capabilities on startup
    if VOICE_ENABLED:
        tts_ok = is_tts_available()
        stt_ok = is_stt_available()
        
        if not tts_ok and not stt_ok:
            print("WARNING: Voice mode enabled but no TTS/STT available. Install pyttsx3 and SpeechRecognition.")
            print("Falling back to text-only mode.")
        elif not tts_ok:
            print("WARNING: TTS not available. Voice output disabled.")
        elif not stt_ok:
            print("WARNING: STT not available. Voice input disabled.")
    
    _print_april("online. ready.")

    while True:
        command = None
        
        # Try voice input first if enabled
        if VOICE_ENABLED and is_stt_available():
            print("You> 🎤 [Speak now...]", end="", flush=True)
            voice_text = listen()
            
            if voice_text:
                command = voice_text
                print(f"\rYou> {command}")  # Echo what was heard
            else:
                # Voice failed, fall back to text input
                print("\r", end="")  # Clear the listening prompt
                try:
                    command = input("You> [Not heard, type instead] ")
                except (EOFError, KeyboardInterrupt):
                    _print_april("standing down.")
                    break
                except Exception:
                    _print_april("input channel error.")
                    break
        else:
            # Standard text input
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

        # Detect social phrases (greetings, farewells, positive feedback, check-ins)
        is_social, phrase_type = detect_social_phrase(command)
        if is_social:
            if phrase_type == "greeting":
                set_emotional_state("calm")
            elif phrase_type == "checkin":
                set_emotional_state("friendly")
            elif phrase_type == "positive":
                set_emotional_state("friendly")
            
            response = get_social_response(phrase_type)
            _print_april(response)
            continue

        # Detect gratitude and respond warmly
        if detect_gratitude(command):
            set_emotional_state("friendly")
            _print_april_with_context("", "gratitude_response")
            continue

        intent_name, payload = parse_intent(command)

        # Handle suggestion responses first (higher priority)
        if _suggested_action is not None:
            _handle_suggestion_response(command)
            continue

        # Handle confirmation responses
        if _pending_action is not None:
            _handle_confirmation_response(command)
            continue

        # No intent detected
        if not intent_name:
            _print_april("I can't do that yet.")
            continue

        # Check action policy
        policy = classify_action(intent_name, payload)
        
        if policy == "SAFE":
            # Execute immediately
            _execute_action(intent_name, payload)
        elif policy == "CONFIRM_REQUIRED":
            # Store action and ask for confirmation
            _pending_action = {
                "intent_name": intent_name,
                "payload": payload
            }
            confirmation_msg = get_confirmation_message(intent_name, payload)
            _print_april(confirmation_msg)
        else:
            _print_april("I couldn't evaluate that action.")

        continue


def main() -> None:
    """Protect the main loop against unexpected faults."""
    try:
        _loop()
    except Exception as e:
        _print_april(f"critical fault: {e}. standing down.")
        sys.exit(1)


if __name__ == "__main__":
    main()
