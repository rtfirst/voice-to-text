"""Startscript — leitet an das Package weiter. Verhindert Doppelstart."""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))


def _ensure_single_instance():
    """Prevent multiple instances via a Windows mutex."""
    if sys.platform != "win32":
        return True
    import ctypes
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, "VoiceToText_SingleInstance")
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        sys.exit(0)
    # Keep reference to prevent GC
    _ensure_single_instance._mutex = mutex
    return True


if __name__ == "__main__":
    _ensure_single_instance()
    from voice_to_text.app import VoiceToText
    app = VoiceToText()
    app.run()
