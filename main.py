"""Startscript — leitet an das Package weiter."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from voice_to_text.app import VoiceToText

if __name__ == "__main__":
    app = VoiceToText()
    app.run()
