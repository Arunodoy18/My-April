# My-April

**APRIL** — A Personal Responsive Intelligence Layer

A local-first desktop assistant with natural language understanding, learning capabilities, and optional voice interface.

## Features

### 🧠 Core Intelligence (Days 1-9)
- **Natural Language Understanding**: Parse commands in plain English
- **Application Control**: Launch apps safely (Chrome, Edge, VS Code, Calculator, Notepad)
- **Preference Learning**: Teach APRIL your preferences ("use Chrome as my browser")
- **Pattern Detection**: Proactively suggests next actions based on your habits
- **Safety Policy**: Confirms dangerous operations before execution
- **Emotional Responses**: Contextual tone (friendly/calm/focused)
- **Social Awareness**: Responds to greetings, thanks, and farewells naturally

### 🎤 Voice Interface (Day 10) — OPTIONAL
- **Voice Input**: Speak commands instead of typing
- **Voice Output**: APRIL speaks responses aloud
- **Fully Local**: No cloud dependencies (offline TTS/STT)
- **Graceful Fallback**: Falls back to text if voice fails

## Quick Start

### Basic Setup (Text Mode)

```powershell
# Clone/navigate to directory
cd C:\dev\My-April

# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Run APRIL
python main.py
```

### Enable Voice (Optional)

```powershell
# Install voice dependencies
pip install -r requirements.txt

# Edit main.py and set: VOICE_ENABLED = True

# Run with voice
python main.py
```

See [VOICE_GUIDE.md](VOICE_GUIDE.md) for detailed voice setup instructions.

## Example Usage

```
APRIL: online. ready.

You> open chrome
APRIL: Opening Chrome.

You> use microsoft edge as my browser
APRIL: Got it. I'll use microsoft edge as your browser.

You> open browser
APRIL: Opening your browser.

You> thanks
APRIL: You're welcome! Happy to help.

You> delete file important.txt
APRIL: Are you sure you want to execute: delete file important.txt? (yes/no)
You> no
APRIL: Action cancelled.
```

## Architecture

```
User Input (text/voice)
    ↓
Intent Parser (cognition/intent.py)
    ↓
Safety Policy (core/policy.py) → Confirmation if dangerous
    ↓
Action Executor (main.py)
    ↓
Skill Modules (skills/*)
    ↓
Memory Systems (memory/*)
    ↓
Response (with emotional tone) → Voice Output (optional)
```

### Key Modules

- **main.py**: Command loop and orchestration
- **cognition/intent.py**: Natural language parsing
- **core/policy.py**: Action safety classification
- **core/personality.py**: Emotional state and tone
- **core/voice.py**: Speech I/O (optional)
- **skills/system_control/open_app.py**: Safe app launcher
- **memory/preferences.py**: Persistent user preferences
- **memory/action_history.py**: Pattern detection and suggestions

## Safety & Privacy

✅ **Local-First**: No cloud, no telemetry, no data collection  
✅ **Whitelisted Actions**: Only safe, predefined operations allowed  
✅ **Confirmation Flow**: Dangerous commands require explicit approval  
✅ **No Shell Execution**: No arbitrary command execution  
✅ **Transparent**: All code is readable Python, no black boxes

## Development Timeline

- **Day 1**: Command backbone + open app skill
- **Day 2**: Natural language intent parsing
- **Day 3**: Preference system with category aliases
- **Day 4**: Live learning ("use X as my Y")
- **Day 5**: JSON persistence for preferences
- **Day 7**: Safety policy + confirmation flow
- **Day 8**: Action history + proactive suggestions
- **Day 9**: Personality layer + social responses
- **Day 10**: Voice interface (speech I/O)

## Technology Stack

- **Language**: Python 3.12+
- **Core**: Standard library only (no dependencies)
- **Voice (Optional)**:
  - pyttsx3 (TTS)
  - SpeechRecognition (STT)
  - PyAudio (microphone)

## Philosophy

APRIL is built on principles of:
- **Determinism**: Predictable, rule-based behavior (no AI/ML)
- **Locality**: Runs entirely on your machine
- **Modularity**: Easy to extend with new skills
- **Safety**: Explicit permissions and confirmations
- **Transparency**: Readable, maintainable code

## Roadmap

- [x] Voice interface
- [ ] File system skills (with safety)
- [ ] Calendar/reminder system
- [ ] Note-taking and search
- [ ] System monitoring
- [ ] Multi-language support
- [ ] Custom skill API

## Contributing

APRIL is a personal project but follows clean architecture principles. To add a new skill:

1. Create module in `skills/<category>/`
2. Implement safe, single-responsibility function
3. Add intent detection in `cognition/intent.py`
4. Add policy classification in `core/policy.py`
5. Wire into action executor in `main.py`

## License

See [LICENSE](LICENSE)

## Acknowledgments

Built with ❤️ as an exploration of local-first AI assistants.
