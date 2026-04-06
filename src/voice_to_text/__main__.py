"""Einstiegspunkt: python -m voice_to_text"""

from .app import VoiceToText

if __name__ == "__main__":
    app = VoiceToText()
    app.run()
