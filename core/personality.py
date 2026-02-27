"""
DAY 9 — PERSONALITY & EMOTIONAL TONE LAYER

Module for managing APRIL's emotional state and tone modulation.

GOAL:
- Add personality without affecting command execution
- Responses feel warmer and more human-like
- Emotional state affects phrasing only, never logic

EMOTIONAL STATES:
- calm: Default professional tone
- friendly: Warmer, more personal
- focused: Concise, efficient
"""

from typing import Literal

EmotionalState = Literal["calm", "friendly", "focused"]

_current_state: EmotionalState = "calm"


def get_emotional_state() -> EmotionalState:
    """Return the current emotional state."""
    return _current_state


def set_emotional_state(state: EmotionalState) -> None:
    """Update APRIL's emotional state."""
    global _current_state
    if state in {"calm", "friendly", "focused"}:
        _current_state = state


def apply_tone(message: str, context: str = "") -> str:
    """Apply emotional tone to a message based on current state and context."""
    # Context-specific responses take priority
    if context == "gratitude_response":
        return _format_gratitude_response()
    
    if not isinstance(message, str) or not message:
        return message
    
    state = _current_state
    
    # Apply tone based on emotional state
    if state == "friendly":
        # Add warmth to standard messages
        if message.startswith("Opening"):
            return message
        return message
    elif state == "focused":
        # Make more concise
        if message.startswith("Opening"):
            app = message.replace("Opening ", "").replace(".", "")
            return f"{app} opened."
        return message
    else:  # calm (default)
        return message


def _format_gratitude_response() -> str:
    """Return an appropriate response to user gratitude based on emotional state."""
    state = _current_state
    
    if state == "friendly":
        return "You're welcome! Happy to help."
    elif state == "focused":
        return "You're welcome."
    else:  # calm
        return "My pleasure."


def detect_gratitude(text: str) -> bool:
    """Detect if user is expressing gratitude."""
    if not isinstance(text, str):
        return False
    
    text_lower = text.strip().lower()
    gratitude_phrases = {
        "thanks",
        "thank you",
        "thank you so much",
        "thanks a lot",
        "appreciate it",
        "much appreciated",
        "thx",
        "ty",
    }
    
    for phrase in gratitude_phrases:
        if phrase in text_lower:
            return True
    
    return False


def detect_social_phrase(text: str) -> tuple[bool, str]:
    """
    Detect common social phrases that don't require action.
    Returns (is_social, phrase_type).
    """
    if not isinstance(text, str):
        return False, ""
    
    text_lower = text.strip().lower()
    
    # Greetings
    greetings = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
    for greeting in greetings:
        if text_lower == greeting or text_lower.startswith(greeting + " "):
            return True, "greeting"
    
    # Conversational check-ins
    checkins = [
        "how are you",
        "how are you doing",
        "how's it going",
        "what's up",
        "whats up",
        "how do you do",
        "you okay",
        "you good",
    ]
    for checkin in checkins:
        if checkin in text_lower:
            return True, "checkin"
    
    # Farewells
    farewells = {"bye", "goodbye", "see you", "later", "good night"}
    for farewell in farewells:
        if text_lower == farewell or farewell in text_lower:
            return True, "farewell"
    
    # Positive feedback
    positive = {"good job", "well done", "nice", "great", "awesome", "perfect"}
    for pos in positive:
        if pos in text_lower:
            return True, "positive"
    
    return False, ""


def get_social_response(phrase_type: str) -> str:
    """Generate appropriate response for social phrases based on emotional state."""
    state = _current_state
    
    if phrase_type == "greeting":
        if state == "friendly":
            return "Hi there! How can I help?"
        elif state == "focused":
            return "Hello."
        else:  # calm
            return "Hello."
    
    elif phrase_type == "checkin":
        if state == "friendly":
            return "I'm doing great! Ready to help you. 😊"
        elif state == "focused":
            return "I'm operational."
        else:  # calm
            return "I'm doing well, thank you."
    
    elif phrase_type == "farewell":
        if state == "friendly":
            return "See you later!"
        elif state == "focused":
            return "Goodbye."
        else:  # calm
            return "Goodbye."
    
    elif phrase_type == "positive":
        set_emotional_state("friendly")
        if state == "friendly":
            return "Thank you! 😊"
        else:
            return "Thank you."
    
    return ""