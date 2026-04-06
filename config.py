import os
import json
from pathlib import Path

# Load .env file
_env_path = Path(__file__).parent / ".env"
if _env_path.exists():
    for line in _env_path.read_text().strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# Virtual key codes
VK_CONTROL = 0x11
VK_SPACE = 0x20

# Hotkey configuration
HOTKEY_MODIFIER = VK_CONTROL
HOTKEY_KEY = VK_SPACE

# Whisper configuration defaults
WHISPER_DEVICE = "cuda"

# Audio configuration
SAMPLE_RATE = 16000
CHANNELS = 1

# Anthropic API
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = "claude-haiku-4-5-20251001"
ANTHROPIC_TIMEOUT = 5.0
CORRECTION_PROMPT = (
    "Korrigiere den folgenden transkribierten Text. "
    "Behalte den Inhalt und die Sprache bei, korrigiere nur Grammatik, "
    "Rechtschreibung und Interpunktion. "
    "Gib nur den korrigierten Text zurück, ohne Erklärungen."
)

# Overlay configuration
OVERLAY_WIDTH = 140
OVERLAY_HEIGHT = 14
OVERLAY_IDLE_ALPHA = 0.3
OVERLAY_ACTIVE_ALPHA = 1.0
OVERLAY_DONE_DURATION_MS = 500

# Colors
COLOR_IDLE = "#808080"
COLOR_RECORDING = "#FF0000"
COLOR_TRANSCRIBING = "#FFD700"
COLOR_DONE = "#00CC00"

# Available whisper models
WHISPER_MODELS = ["tiny", "small", "medium", "large-v3", "turbo"]

# Available languages
WHISPER_LANGUAGES = {
    "auto": None,
    "Deutsch": "de",
    "English": "en",
}

# Persistent settings file
_settings_path = Path(__file__).parent / "settings.json"


def _load_settings() -> dict:
    if _settings_path.exists():
        try:
            return json.loads(_settings_path.read_text())
        except Exception:
            pass
    return {}


def _save_settings(settings: dict):
    _settings_path.write_text(json.dumps(settings, indent=2))


class Settings:
    def __init__(self):
        data = _load_settings()
        self.whisper_model: str = data.get("whisper_model", "small")
        self.auto_correct: bool = data.get("auto_correct", True)
        self.language: str = data.get("language", "Deutsch")

    def save(self):
        _save_settings({
            "whisper_model": self.whisper_model,
            "auto_correct": self.auto_correct,
            "language": self.language,
        })
