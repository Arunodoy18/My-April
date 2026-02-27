"""
Test script for voice module.
Run this to verify TTS and STT work independently.
"""

import sys
from core.voice import (
    speak,
    listen,
    is_tts_available,
    is_stt_available,
    get_voice_status,
)


def test_voice_status():
    """Check if voice capabilities are available."""
    print("=" * 50)
    print("VOICE MODULE STATUS CHECK")
    print("=" * 50)
    
    status = get_voice_status()
    
    print(f"TTS Available: {status['tts_available']}")
    print(f"STT Available: {status['stt_available']}")
    print(f"Voice Ready: {status['voice_ready']}")
    print()
    
    if not status['tts_available']:
        print("⚠️  Text-to-Speech not available.")
        print("   Install: pip install pyttsx3")
        print()
    
    if not status['stt_available']:
        print("⚠️  Speech-to-Text not available.")
        print("   Install: pip install SpeechRecognition PyAudio")
        print()
    
    return status['voice_ready']


def test_tts():
    """Test text-to-speech."""
    if not is_tts_available():
        print("❌ TTS not available. Skipping TTS test.")
        return False
    
    print("=" * 50)
    print("TESTING TEXT-TO-SPEECH")
    print("=" * 50)
    
    test_messages = [
        "Hello, this is APRIL.",
        "Testing text to speech.",
        "If you can hear this, TTS is working correctly.",
    ]
    
    for i, msg in enumerate(test_messages, 1):
        print(f"{i}. Speaking: {msg}")
        speak(msg)
        print("   ✓ Spoken")
    
    print("\n✅ TTS test complete!")
    return True


def test_stt():
    """Test speech-to-text."""
    if not is_stt_available():
        print("❌ STT not available. Skipping STT test.")
        return False
    
    print("=" * 50)
    print("TESTING SPEECH-TO-TEXT")
    print("=" * 50)
    
    print("\nInstructions:")
    print("1. When you see [Listening...], speak clearly")
    print("2. Say a simple command like: 'open chrome'")
    print("3. The text you spoke will be displayed")
    print()
    
    for attempt in range(3):
        print(f"\nAttempt {attempt + 1}/3:")
        print("[Listening...]")
        
        result = listen()
        
        if result:
            print(f"✓ Heard: {result}")
            return True
        else:
            print("✗ No speech detected or recognition failed")
            
            if attempt < 2:
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    break
    
    print("\n❌ STT test failed or no speech detected")
    return False


def main():
    """Run all voice tests."""
    print("\n")
    print("╔" + "═" * 48 + "╗")
    print("║" + " " * 48 + "║")
    print("║" + "    APRIL VOICE MODULE TEST SUITE".center(48) + "║")
    print("║" + " " * 48 + "║")
    print("╚" + "═" * 48 + "╝")
    print("\n")
    
    # Check status
    voice_ready = test_voice_status()
    
    if not voice_ready:
        print("\n⚠️  Voice not fully available. Some tests will be skipped.")
        print("    See installation instructions above.")
        return
    
    print("\n✅ Voice module is ready!")
    print("\nPress Enter to start tests (or Ctrl+C to cancel)...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTests cancelled.")
        return
    
    # Test TTS
    print("\n")
    test_tts()
    
    # Test STT
    print("\n")
    response = input("\nTest speech-to-text? (y/n): ").strip().lower()
    if response == 'y':
        test_stt()
    else:
        print("STT test skipped.")
    
    print("\n")
    print("=" * 50)
    print("ALL TESTS COMPLETE")
    print("=" * 50)
    print("\nIf tests passed, you can enable voice in main.py:")
    print("  VOICE_ENABLED = True")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted.")
        sys.exit(0)
