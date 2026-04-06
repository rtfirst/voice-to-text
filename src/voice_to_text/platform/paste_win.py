"""Windows paste implementation using win32 APIs."""

import ctypes
import ctypes.wintypes
import time
import win32clipboard
import win32api
import win32con

user32 = ctypes.windll.user32

_CTRL_SHIFT_V_CLASSES = {
    "CASCADIA_HOSTING_WINDOW_CLASS",
}
_SHIFT_INSERT_CLASSES = {
    "ConsoleWindowClass",
    "mintty",
    "VirtualConsoleClass",
    "TMAIN",
}

VK_SHIFT = 0x10
VK_INSERT = 0x2D


def _get_window_class(hwnd) -> str:
    if not hwnd:
        return ""
    buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, buf, 256)
    return buf.value


def get_foreground_window():
    return user32.GetForegroundWindow()


def _get_clipboard_text() -> str | None:
    try:
        win32clipboard.OpenClipboard()
        try:
            return win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        except TypeError:
            return None
        finally:
            win32clipboard.CloseClipboard()
    except Exception:
        return None


def _set_clipboard_text(text: str):
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    finally:
        win32clipboard.CloseClipboard()


def _send_ctrl_v():
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


def _send_shift_insert():
    win32api.keybd_event(VK_SHIFT, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(VK_INSERT, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(VK_INSERT, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    win32api.keybd_event(VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)


def _send_ctrl_shift_v():
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(VK_SHIFT, 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    time.sleep(0.02)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    win32api.keybd_event(VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.02)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)


def paste_text(text: str, target_hwnd=None):
    time.sleep(0.3)

    if target_hwnd:
        user32.SetForegroundWindow(target_hwnd)
        time.sleep(0.1)

    old_clipboard = _get_clipboard_text()
    _set_clipboard_text(text)
    time.sleep(0.05)

    fg_hwnd = user32.GetForegroundWindow()
    fg_class = _get_window_class(fg_hwnd)

    if fg_class in _CTRL_SHIFT_V_CLASSES:
        _send_ctrl_shift_v()
    elif fg_class in _SHIFT_INSERT_CLASSES:
        _send_shift_insert()
    else:
        _send_ctrl_v()

    time.sleep(0.1)

    if old_clipboard is not None:
        try:
            _set_clipboard_text(old_clipboard)
        except Exception:
            pass
