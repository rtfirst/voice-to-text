"""Platform-specific implementations for hotkey, paste, and overlay."""

import sys

PLATFORM = "darwin" if sys.platform == "darwin" else "win32"
