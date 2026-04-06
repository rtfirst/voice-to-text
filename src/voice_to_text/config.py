import os
import json
from pathlib import Path

# Project root is three levels up from this file (src/voice_to_text/config.py)
_project_root = Path(__file__).parent.parent.parent

# Load .env file from project root
_env_path = _project_root / ".env"
if _env_path.exists():
    for line in _env_path.read_text().strip().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())

# Virtual key code mappings (name -> vk_code)
VK_CODES = {
    "Ctrl": 0x11,
    "L-Ctrl": 0xA2,
    "R-Ctrl": 0xA3,
    "Shift": 0x10,
    "L-Shift": 0xA0,
    "R-Shift": 0xA1,
    "Alt": 0x12,
    "L-Alt": 0xA4,
    "R-Alt": 0xA5,
    "Win": 0x5B,
    "Space": 0x20,
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "F13": 0x7C, "F14": 0x7D, "F15": 0x7E, "F16": 0x7F,
    "CapsLock": 0x14,
    "Tab": 0x09,
    "Insert": 0x2D,
    "Pause": 0x13,
    "ScrollLock": 0x91,
}

# Available hotkey combinations for the menu
HOTKEY_PRESETS = {
    "Ctrl+Space": ("Ctrl", "Space"),
    "Ctrl+Shift+Space": ("Ctrl", "Space"),  # uses Shift as extra modifier
    "Alt+Space": ("Alt", "Space"),
    "F13": (None, "F13"),
    "F14": (None, "F14"),
    "Ctrl+F9": ("Ctrl", "F9"),
    "Ctrl+F10": ("Ctrl", "F10"),
}

# Default hotkey
DEFAULT_HOTKEY = "Ctrl+Space"

# Whisper device — auto-detect: CUDA > MPS (Apple Silicon) > CPU
def _detect_device() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps"
    except ImportError:
        pass
    return "cpu"

WHISPER_DEVICE = _detect_device()

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
OVERLAY_WIDTH = 68
OVERLAY_HEIGHT = 10
OVERLAY_IDLE_ALPHA = 0.7
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

# Persistent settings file in project root
_settings_path = _project_root / "settings.json"


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
        self.hotkey: str = data.get("hotkey", DEFAULT_HOTKEY)

    @property
    def hotkey_modifier_vk(self) -> int | None:
        preset = HOTKEY_PRESETS.get(self.hotkey)
        if not preset or not preset[0]:
            return None
        return VK_CODES.get(preset[0])

    @property
    def hotkey_key_vk(self) -> int:
        preset = HOTKEY_PRESETS.get(self.hotkey, (None, "Space"))
        return VK_CODES.get(preset[1], 0x20)

    def save(self):
        _save_settings({
            "whisper_model": self.whisper_model,
            "auto_correct": self.auto_correct,
            "language": self.language,
            "hotkey": self.hotkey,
        })
