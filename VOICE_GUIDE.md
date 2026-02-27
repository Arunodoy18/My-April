# DAY 10 — VOICE INTERFACE GUIDE

## Overview

APRIL now supports optional voice input/output using local, offline speech processing.

**Architecture**: Voice is a pure I/O layer. All intelligence (intent parsing, safety, memory) remains unchanged.

## Quick Start

### 1. Install Voice Dependencies (Optional)

```powershell
# Activate virtual environment
.venv\Scripts\activate

# Install voice libraries
pip install pyttsx3 SpeechRecognition PyAudio
```

**Note**: PyAudio installation on Windows may require:
- Visual C++ Build Tools
- Or pre-built wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 2. Enable Voice Mode

In `main.py`, change:
```python
VOICE_ENABLED = False
```
to:
```python
VOICE_ENABLED = True
```

### 3. Run APRIL

```powershell
python main.py
```

## How It Works

### Voice Input (Speech-to-Text)
- APRIL listens when you see `[Listening...]`
- Speak your command clearly
- APRIL converts speech to text
- Falls back to keyboard if voice fails

### Voice Output (Text-to-Speech)
- All APRIL responses are spoken aloud
- Uses your system's default voice
- Text is also printed (no change)

## Example Session

```
APRIL: online. ready.
You> [Listening...]
You> open chrome
APRIL: Opening Chrome. [spoken + printed]

You> [Listening...]
You> thanks
APRIL: You're welcome! Happy to help. [spoken + printed]
```

## Behavior Details

### With VOICE_ENABLED = True
- APRIL listens for voice commands
- If voice recognition fails → prompts for text input
- All responses are spoken AND printed
- Exit/quit commands work in both modes

### With VOICE_ENABLED = False (Default)
- Behaves exactly as Days 1-9
- Pure keyboard input/output
- No voice dependencies required

## Technical Details

### Libraries Used

**pyttsx3** (Text-to-Speech):
- Offline, uses OS speech engine
- Windows: SAPI5
- macOS: NSSpeechSynthesizer  
- Linux: eSpeak

**SpeechRecognition** (Speech-to-Text):
- Supports multiple engines
- Default: CMU Sphinx (offline)
- Fallback: Google Web Speech API (online, better accuracy)

### Safety & Constraints

✅ Voice NEVER bypasses:
- Intent parsing
- Policy checks  
- Confirmation flow
- Preference system
- Action history

❌ Voice does NOT add:
- Wake words
- Background listening
- Async/threading
- Cloud dependencies (except Google fallback)

## Troubleshooting

### "WARNING: TTS not available"
- Install: `pip install pyttsx3`
- Windows: Ensure SAPI5 is available (built-in)

### "WARNING: STT not available"  
- Install: `pip install SpeechRecognition PyAudio`
- Test microphone permissions

### Microphone Not Working
- Check Windows privacy settings → Microphone access
- Ensure microphone is not muted
- Try: `python -m speech_recognition` (test tool)

### Poor Recognition Accuracy
- Speak clearly and at normal pace
- Reduce background noise
- Consider using Google fallback (requires internet)

### Voice Cuts Off Early
- Adjust `phrase_time_limit` in `core/voice.py`
- Currently set to 10 seconds per command

## Customization

### Change Voice Speed/Volume
Edit `core/voice.py`:
```python
_tts_engine.setProperty('rate', 150)    # Speed (default ~200)
_tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
```

### Change Voice Gender/Type
Edit `core/voice.py`:
```python
voices = _tts_engine.getProperty('voices')
_tts_engine.setProperty('voice', voices[1].id)  # Try different indices
```

### Force Offline STT
Edit `core/voice.py`, remove Google fallback in `listen()`.

### Force Google STT
Replace `recognize_sphinx` with `recognize_google` in `listen()`.

## Performance Notes

- TTS latency: ~100-500ms (depends on text length)
- STT latency: ~1-3 seconds (local Sphinx)
- STT latency: ~500ms-2s (Google, requires internet)
- No background CPU usage (listening only when prompted)

## Future Enhancements (Not Implemented)

- Wake word detection
- Continuous listening mode
- Multiple language support
- Custom voice training
- Whisper integration (better offline STT)
- Vosk integration (fast offline STT)

## Architecture Guarantee

Voice is a **pure I/O layer**. If you disable it:
- APRIL works exactly as before
- Zero behavior changes
- No dependencies required

This design ensures:
- Easy to replace STT/TTS engines
- Easy to debug (voice failures don't break logic)
- Easy to extend (add wake words, etc.)
