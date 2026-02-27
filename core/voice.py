"""
DAY 10 — VOICE I/O LAYER (HARDENED VERSION)

Provides local speech-to-text and text-to-speech capabilities.
Uses:
- pyttsx3 for TTS (offline, OS-native)
- speech_recognition for STT (local microphone)

This module is PURE I/O. It must NEVER:
- Parse intents
- Execute actions
- Modify state
- Make decisions

STRICT RULES:
- All operations are synchronous (blocking)
- Failures return None or fail silently
- No threading
- No background processes

HARDENED TTS LIFECYCLE:
- ONE global engine, initialized once, NEVER destroyed
- Explicit audio device release after microphone use
- Self-test loop on startup
- Retry logic if speak fails
- Comprehensive debug logging
"""

from typing import Optional
import sys
import time


# Optional imports - gracefully handle missing dependencies
try:
    import pyttsx3
    _TTS_AVAILABLE = True
except ImportError:
    _TTS_AVAILABLE = False
    pyttsx3 = None

try:
    import speech_recognition as sr
    _STT_AVAILABLE = True
except ImportError:
    _STT_AVAILABLE = False
    sr = None


# Global TTS engine (initialized once, NEVER destroyed)
_tts_engine = None
_engine_initialized = False


def _initialize_tts(force_reinit=False):
    """
    Initialize the TTS engine ONCE and never destroy it.
    Uses Windows SAPI5 with female voice selection.
    
    Args:
        force_reinit: If True, reinitialize even if already initialized (recovery mode)
    
    Returns:
        bool: True if engine ready, False otherwise
    """
    global _tts_engine, _engine_initialized
    
    if not _TTS_AVAILABLE:
        print("[TTS] pyttsx3 not available")
        return False
    
    if _engine_initialized and _tts_engine is not None and not force_reinit:
        return True
    
    try:
        print("[TTS] Initializing Windows SAPI5 engine...")
        
        # Clean up old engine if reinitializing
        if force_reinit and _tts_engine is not None:
            try:
                _tts_engine.stop()
                del _tts_engine
                _tts_engine = None
            except:
                pass
            print("[TTS] Forced reinitialization...")
        
        # Force Windows SAPI5 driver
        _tts_engine = pyttsx3.init('sapi5')
        
        # Select female voice
        voices = _tts_engine.getProperty('voices')
        print(f"[TTS] Found {len(voices)} voices")
        
        female_voice_set = False
        for voice in voices:
            voice_name_lower = voice.name.lower()
            # Prioritize: Zira (US) > Hazel (UK) > any female
            if 'zira' in voice_name_lower:
                _tts_engine.setProperty('voice', voice.id)
                print(f"[TTS] ✓ Selected: {voice.name}")
                female_voice_set = True
                break
            elif 'hazel' in voice_name_lower and not female_voice_set:
                _tts_engine.setProperty('voice', voice.id)
                print(f"[TTS] ✓ Selected: {voice.name}")
                female_voice_set = True
            elif 'female' in voice_name_lower and not female_voice_set:
                _tts_engine.setProperty('voice', voice.id)
                print(f"[TTS] ✓ Selected: {voice.name}")
                female_voice_set = True
        
        # Set voice properties
        _tts_engine.setProperty('rate', 175)  # Natural speaking pace
        _tts_engine.setProperty('volume', 1.0)  # Maximum volume
        
        _engine_initialized = True
        print("[TTS] ✓ Engine initialized successfully")
        
        # Self-test: speak initialization message
        print("[TTS] Running self-test...")
        try:
            _tts_engine.stop()  # Clear any pending audio
            _tts_engine.say("APRIL voice system initialized")
            _tts_engine.runAndWait()
            time.sleep(0.2)  # Ensure audio completes before next call
            print("[TTS] ✓ Self-test passed")
        except Exception as e:
            print(f"[TTS] ⚠ Self-test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"[TTS ERROR] Initialization failed: {e}")
        _tts_engine = None
        _engine_initialized = False
        return False


def speak(text: str) -> None:
    """
    Convert text to speech using the global TTS engine.
    GUARANTEED to attempt speech when VOICE_ENABLED=True.
    
    Args:
        text: The text to speak
    
    Returns:
        None
    
    Behavior:
        - Uses global engine (never destroyed)
        - Blocks until speech completes
        - Retries once if engine fails
        - Never crashes on failure
    """
    print(f"\n[TTS] >>> speak() called: '{text[:50]}...'")
    
    if not isinstance(text, str) or not text.strip():
        print("[TTS] ⚠ Text empty/invalid")
        return
    
    if not _TTS_AVAILABLE:
        print("[TTS] ⚠ pyttsx3 not available")
        return
    
    # Ensure engine is initialized
    if not _initialize_tts():
        print("[TTS] ✗ Initialization failed")
        return
    
    try:
        # Remove emojis and special characters that TTS can't handle
        clean_text = text.replace("😊", "").replace("🙂", "").replace("✨", "").strip()
        if not clean_text:
            print("[TTS] ⚠ Clean text is empty after emoji removal")
            return
        
        print(f"[TTS] Speaking: '{clean_text}'")
        
        # Use global engine
        _tts_engine.stop()  # Clear any pending audio queue
        _tts_engine.say(clean_text)
        _tts_engine.runAndWait()
        time.sleep(0.2)  # Ensure audio fully completes before returning
        
        print("[TTS] ✓ Speech completed successfully")
        
    except Exception as e:
        print(f"[TTS ERROR] Speech failed: {e}")
        print("[TTS] Attempting recovery (reinitialize engine)...")
        
        # Retry once with reinitialized engine
        try:
            if _initialize_tts(force_reinit=True):
                print("[TTS] Retry: speaking after reinitialization...")
                _tts_engine.stop()  # Clear audio queue
                _tts_engine.say(clean_text)
                _tts_engine.runAndWait()
                time.sleep(0.2)  # Ensure audio completes
                print("[TTS] ✓ Recovery successful")
            else:
                print("[TTS] ✗ Recovery failed - engine won't initialize")
        except Exception as e2:
            print(f"[TTS ERROR] Recovery attempt failed: {e2}")


def listen() -> Optional[str]:
    """
    Listen to microphone and convert speech to text.
    Listens once per call (not continuous).
    
    CRITICAL: After microphone use, explicitly releases audio device
    with delay to prevent TTS contention.
    
    Returns:
        str: Transcribed text if successful
        None: If STT unavailable, no speech detected, or error
    
    Behavior:
        - Blocks while listening (with timeout)
        - Returns None on any failure
        - Never throws exceptions outward
        - Optimized for short phrases like "hi", "hello", "thanks"
        - Releases audio device after use (150ms delay for driver)
    """
    if not _STT_AVAILABLE:
        return None
    
    recognizer = sr.Recognizer()
    
    # Optimize for short utterances
    recognizer.energy_threshold = 300  # Lower = more sensitive
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8  # Shorter pause detection for quick phrases
    
    result = None
    
    try:
        with sr.Microphone() as source:
            # Proper ambient noise calibration for better detection
            print("[STT] Calibrating for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            print("[STT] Listening...")
            # Listen for speech - optimized for short phrases
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)
            
            # CRITICAL: Microphone context closes here
            # source.__exit__ is called, releasing the device
        
        # CRITICAL: Force audio device release with delay
        # Windows audio drivers need time to fully release the device
        print("[STT] Releasing audio device...")
        time.sleep(0.15)  # 150ms delay for driver to release device
        
        # Now process the audio (microphone is released)
        print("[STT] Processing audio...")
        
        # Use Google Web Speech API (fast and accurate)
        try:
            text = recognizer.recognize_google(audio)
            
            # Confidence filtering
            if text:
                cleaned = text.strip().lower()
                # Reject very short garbage (but allow "hi", "no", etc.)
                if len(cleaned) < 2:
                    print(f"[STT] ⚠ Rejected too short: '{cleaned}'")
                    return None
                # Return original casing for proper handling
                print(f"[STT] ✓ Recognized: '{text}'")
                result = text.strip()
                return result
            return None
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            print("[STT] ⚠ Speech unintelligible")
            return None
        except sr.RequestError:
            # Google not available, try Sphinx as fallback
            print("[STT] Google API unavailable, trying Sphinx...")
            try:
                text = recognizer.recognize_sphinx(audio)
                if text:
                    cleaned = text.strip().lower()
                    if len(cleaned) < 2:
                        print(f"[STT] ⚠ Rejected too short: '{cleaned}'")
                        return None
                    print(f"[STT] ✓ Recognized (Sphinx): '{text}'")
                    result = text.strip()
                    return result
                return None
            except Exception as e:
                print(f"[STT ERROR] Sphinx failed: {e}")
                return None
    
    except sr.WaitTimeoutError:
        print("[STT] ⚠ Timeout - no speech detected")
        
        # Still release audio device on timeout
        time.sleep(0.15)
        return None
    except Exception as e:
        print(f"[STT ERROR] Unexpected error: {e}")
        
        # Still release audio device on error
        time.sleep(0.15)
        return None


def is_tts_available() -> bool:
    """Check if text-to-speech is available."""
    return _TTS_AVAILABLE and _initialize_tts()


def is_stt_available() -> bool:
    """Check if speech-to-text is available."""
    return _STT_AVAILABLE


def get_voice_status() -> dict:
    """
    Get status of voice capabilities.
    
    Returns:
        dict with keys:
            - tts_available: bool
            - stt_available: bool
            - voice_ready: bool (both available)
    """
    tts_ok = is_tts_available()
    stt_ok = is_stt_available()
    
    return {
        "tts_available": tts_ok,
        "stt_available": stt_ok,
        "voice_ready": tts_ok and stt_ok,
    }
