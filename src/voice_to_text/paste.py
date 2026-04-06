"""Clipboard paste — delegates to platform-specific implementation."""

import sys

if sys.platform == "darwin":
    from .platform.paste_mac import paste_text, get_foreground_window
else:
    from .platform.paste_win import paste_text, get_foreground_window

__all__ = ["paste_text", "get_foreground_window"]
