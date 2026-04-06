"""Windows-specific overlay window setup."""

import ctypes

user32 = ctypes.windll.user32

GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
LWA_ALPHA = 0x02
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040


def setup_window(root):
    """Apply Win32 extended styles for always-on-top tool window."""
    bg_color = "#010101"
    root.attributes("-transparentcolor", bg_color)
    root.configure(bg=bg_color)

    root.update_idletasks()
    root.deiconify()
    root.update()

    try:
        hwnd = user32.GetParent(root.winfo_id())
        if not hwnd:
            hwnd = root.winfo_id()
        ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        ex_style |= WS_EX_TOOLWINDOW | WS_EX_TOPMOST
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
        user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
        )
        return hwnd
    except Exception:
        return None


def set_alpha(hwnd, alpha: float):
    """Set window transparency via Win32 layered window attributes."""
    if hwnd:
        user32.SetLayeredWindowAttributes(hwnd, 0, int(alpha * 255), LWA_ALPHA)


def get_bg_color():
    return "#010101"
