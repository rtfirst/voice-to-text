"""Push-to-Talk hotkey detection — delegates to platform-specific implementation."""

import sys

if sys.platform == "darwin":
    from .platform.hotkey_mac import PushToTalkHook
else:
    from .platform.hotkey_win import PushToTalkHook

__all__ = ["PushToTalkHook"]
