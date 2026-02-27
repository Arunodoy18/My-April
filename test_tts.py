"""
Quick test to verify TTS audio output.
Run this to check if you can hear APRIL's voice.
"""

import pyttsx3

print("Testing TTS audio output...")
print("You should hear: 'Hello, this is APRIL speaking.'")
print()

try:
    engine = pyttsx3.init('sapi5')
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"Found {len(voices)} voices:")
    for i, voice in enumerate(voices):
        print(f"  {i}: {voice.name}")
    print()
    
    # Set female voice if available
    for voice in voices:
        if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            print(f"Using voice: {voice.name}")
            break
    
    # Set properties
    rate = engine.getProperty('rate')
    print(f"Current rate: {rate}")
    engine.setProperty('rate', 175)
    
    volume = engine.getProperty('volume')
    print(f"Current volume: {volume}")
    engine.setProperty('volume', 1.0)
    
    print()
    print("Speaking now...")
    engine.say("Hello, this is APRIL speaking.")
    engine.runAndWait()
    print("Done!")
    
    print()
    print("If you heard the voice, TTS is working correctly.")
    print("If not, check:")
    print("  1. Windows volume is not muted")
    print("  2. Speakers are plugged in and selected as default device")
    print("  3. Windows Settings > System > Sound > Output device")
    
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("TTS is not working. Install: pip install pyttsx3")
