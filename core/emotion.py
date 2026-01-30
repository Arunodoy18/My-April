"""
DAY 9 — PERSONALITY & EMOTIONAL TONE LAYER

GOAL:
Add a lightweight personality and emotional tone system to APRIL
that affects how responses are phrased, not what actions are taken.

WHAT TO ADD:

A. EMOTIONAL STATE
------------------
- Maintain a simple emotional state variable:
  ["calm", "focused", "friendly"]
- Default state = "calm"
- Emotional state NEVER affects logic or decisions

B. TONE MODULATION
------------------
- Route all APRIL responses through a tone formatter
- Tone affects wording only (e.g., warmth, politeness)
- Examples:
  calm → "Opening Chrome."
  friendly → "Opening Chrome 🙂"
  focused → "Chrome opened."

C. EMOTION CHANGES (SAFE TRIGGERS ONLY)
--------------------------------------
- If user says "thanks" / "thank you" → shift to friendly
- If user gives multiple commands quickly → shift to focused
- If idle or neutral conversation → shift to calm

D. STRICT RULES
---------------
- Do NOT change command execution behavior
- Do NOT change policy or confirmation logic
- Do NOT store emotions persistently yet
- Do NOT add emotional reasoning to decisions
- Emotions only affect response phrasing

APRIL'S IDENTITY:
-----------------
- Supportive
- Professional
- Calm by default
- Warm when appreciated
- Focused when working

GOAL STATE:
-----------
APRIL feels human-like, consistent, and pleasant
without ever becoming unpredictable.
"""

from typing import Literal
import time

EmotionalState = Literal["calm", "focused", "friendly"]

_current_state: EmotionalState = "calm"
_last_command_time = 0.0
_command_count_window = 0


def get_current_state() -> EmotionalState:
    """Return the current emotional state."""
    return _current_state


def set_state(state: EmotionalState) -> None:
    """Manually set emotional state."""
    global _current_state
    if state in {"calm", "focused", "friendly"}:
        _current_state = state


def detect_gratitude(user_input: str) -> bool:
    """Check if user is expressing thanks."""
    if not isinstance(user_input, str):
        return False
    
    text_lower = user_input.lower().strip()
    gratitude_phrases = {
        "thanks", "thank you", "thanks!", "thank you!", 
        "ty", "thx", "appreciate it", "appreciated"
    }
    
    return any(phrase in text_lower for phrase in gratitude_phrases)


def update_state_on_input(user_input: str) -> None:
    """Update emotional state based on user behavior."""
    global _current_state, _last_command_time, _command_count_window
    
    current_time = time.time()
    
    # Check for gratitude
    if detect_gratitude(user_input):
        _current_state = "friendly"
        _command_count_window = 0
        return
    
    # Check for rapid commands (within 3 seconds)
    if current_time - _last_command_time < 3:
        _command_count_window += 1
        if _command_count_window >= 2:
            _current_state = "focused"
    else:
        # Reset to calm if idle
        if current_time - _last_command_time > 10:
            _current_state = "calm"
        _command_count_window = 0
    
    _last_command_time = current_time


def apply_tone(message: str) -> str:
    """Apply emotional tone to a response message."""
    if not isinstance(message, str):
        return message
    
    # Tone variations don't change meaning, just add slight personality
    if _current_state == "friendly":
        # Add warmth to positive responses
        if message.startswith("Okay.") or message.startswith("Opening") or message.startswith("Confirmed"):
            return f"{message} 🙂"
        elif "from now on" in message:
            return message.replace("from now on.", "from now on! 🙂")
    
    elif _current_state == "focused":
        # Keep responses terse and efficient
        # Replace longer phrases with shorter ones
        message = message.replace("Opening Chrome.", "Chrome opened.")
        message = message.replace("Opening Microsoft Edge.", "Edge opened.")
        message = message.replace("Opening Visual Studio Code.", "Code opened.")
        message = message.replace("Opening your browser.", "Browser opened.")
        message = message.replace("Opening your editor.", "Editor opened.")
    
    # calm state: default phrasing, no modifications
    return message