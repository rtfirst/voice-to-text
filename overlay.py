import queue
import ctypes
import ctypes.wintypes
import tkinter as tk
import config


# Win32 constants for layered window
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
WS_EX_TRANSPARENT = 0x00000020
LWA_ALPHA = 0x02
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

user32 = ctypes.windll.user32


class Overlay:
    def __init__(self):
        self._queue: queue.Queue[str] = queue.Queue()
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._pill = None
        self._state = "idle"

    def _create_pill(self, color):
        """Draw a pill/capsule shape with border on the canvas."""
        self._canvas.delete("pill")
        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT
        r = h // 2
        border = "#333333"
        # Border layer (slightly larger)
        self._canvas.create_arc(1, 1, h-1, h-1, start=90, extent=180, fill=border, outline=border, tags="pill")
        self._canvas.create_rectangle(r, 1, w - r, h-1, fill=border, outline=border, tags="pill")
        self._canvas.create_arc(w - h+1, 1, w-1, h-1, start=-90, extent=180, fill=border, outline=border, tags="pill")
        # Inner fill (inset by 2px)
        self._canvas.create_arc(3, 3, h-3, h-3, start=90, extent=180, fill=color, outline=color, tags="pill")
        self._canvas.create_rectangle(r, 3, w - r, h-3, fill=color, outline=color, tags="pill")
        self._canvas.create_arc(w - h+3, 3, w-3, h-3, start=-90, extent=180, fill=color, outline=color, tags="pill")

    def _create_window(self):
        self._root = tk.Tk()
        self._root.withdraw()

        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT

        # Make window frameless and always-on-top
        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)

        # Use a transparent background color
        bg_color = "#010101"
        self._root.attributes("-transparentcolor", bg_color)
        self._root.configure(bg=bg_color)

        self._canvas = tk.Canvas(
            self._root,
            width=w,
            height=h,
            highlightthickness=0,
            bd=0,
            bg=bg_color,
        )
        self._canvas.pack()

        # Draw initial pill shape
        self._create_pill(config.COLOR_IDLE)

        # Position at bottom center of screen
        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = screen_h - h - 60
        self._root.geometry(f"{w}x{h}+{x}+{y}")

        self._root.update_idletasks()
        self._root.deiconify()
        self._root.update()

        # Set extended window styles via Win32 API
        try:
            hwnd = user32.GetParent(self._root.winfo_id())
            if not hwnd:
                hwnd = self._root.winfo_id()
            # Make it a tool window (no taskbar entry) and topmost
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex_style |= WS_EX_TOOLWINDOW | WS_EX_TOPMOST
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
            # Force topmost
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
            # Set initial transparency
            idle_alpha = int(config.OVERLAY_IDLE_ALPHA * 255)
            user32.SetLayeredWindowAttributes(hwnd, 0, idle_alpha, LWA_ALPHA)
            self._hwnd = hwnd
        except Exception as e:
            print(f"Win32 setup error: {e}")
            self._hwnd = None

        self._poll_queue()

    def _set_alpha(self, alpha: float):
        """Set window alpha via Win32 for reliable transparency."""
        if self._hwnd:
            user32.SetLayeredWindowAttributes(self._hwnd, 0, int(alpha * 255), LWA_ALPHA)
        else:
            self._root.attributes("-alpha", alpha)

    def _poll_queue(self):
        try:
            while True:
                state = self._queue.get_nowait()
                self._apply_state(state)
        except queue.Empty:
            pass
        if self._root:
            self._root.after(50, self._poll_queue)

    def _apply_state(self, state: str):
        self._state = state
        states = {
            "idle": (config.COLOR_IDLE, config.OVERLAY_IDLE_ALPHA),
            "recording": (config.COLOR_RECORDING, config.OVERLAY_ACTIVE_ALPHA),
            "transcribing": (config.COLOR_TRANSCRIBING, config.OVERLAY_ACTIVE_ALPHA),
            "correcting": (config.COLOR_TRANSCRIBING, config.OVERLAY_ACTIVE_ALPHA),
            "done": (config.COLOR_DONE, config.OVERLAY_ACTIVE_ALPHA),
            "loading": (config.COLOR_IDLE, config.OVERLAY_IDLE_ALPHA),
            "ready": (config.COLOR_IDLE, config.OVERLAY_IDLE_ALPHA),
        }
        color, alpha = states.get(state, (config.COLOR_IDLE, config.OVERLAY_IDLE_ALPHA))
        self._create_pill(color)
        self._set_alpha(alpha)

        if state == "done":
            self._root.after(config.OVERLAY_DONE_DURATION_MS, lambda: self._apply_state("idle"))

    def set_state(self, state: str):
        self._queue.put(state)

    def run(self):
        self._create_window()
        self._root.mainloop()

    def stop(self):
        if self._root:
            self._root.after(0, self._root.destroy)
