"""macOS-specific overlay window setup."""


def setup_window(root):
    """Apply macOS window attributes for always-on-top transparent overlay."""
    root.attributes("-alpha", 0.7)

    root.update_idletasks()
    root.deiconify()
    root.update()

    # On macOS, return None — we use tkinter's alpha attribute directly
    return None


def set_alpha(hwnd, alpha: float):
    """Set window transparency via tkinter (hwnd unused on macOS)."""
    # hwnd is actually the root reference stored by the overlay
    pass


def get_bg_color():
    return "#000000"
