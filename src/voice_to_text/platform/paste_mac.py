"""macOS paste implementation using pbcopy and osascript."""

import subprocess
import time


def get_foreground_window():
    """Return a placeholder — macOS doesn't need window handles for paste."""
    return None


def _get_clipboard_text() -> str | None:
    try:
        result = subprocess.run(
            ["pbpaste"], capture_output=True, text=True, timeout=2,
        )
        return result.stdout if result.returncode == 0 else None
    except Exception:
        return None


def _set_clipboard_text(text: str):
    subprocess.run(
        ["pbcopy"], input=text, text=True, timeout=2, check=True,
    )


def _send_cmd_v():
    """Simulate Cmd+V via osascript."""
    subprocess.run(
        ["osascript", "-e",
         'tell application "System Events" to keystroke "v" using command down'],
        timeout=5,
    )


def paste_text(text: str, target_hwnd=None):
    time.sleep(0.3)

    old_clipboard = _get_clipboard_text()
    _set_clipboard_text(text)
    time.sleep(0.05)

    _send_cmd_v()

    time.sleep(0.1)

    if old_clipboard is not None:
        try:
            _set_clipboard_text(old_clipboard)
        except Exception:
            pass
