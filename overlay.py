import queue
import ctypes
import ctypes.wintypes
import tkinter as tk
import config


# Win32 constants
GWL_EXSTYLE = -20
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_TOPMOST = 0x00000008
LWA_ALPHA = 0x02
HWND_TOPMOST = -1
SWP_NOMOVE = 0x0002
SWP_NOSIZE = 0x0001
SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

user32 = ctypes.windll.user32

_NUM_SEGMENTS = 20
_SEGMENT_GAP = 1
_PILL_PAD = 2  # padding inside pill for VU segments


class Overlay:
    def __init__(self):
        self._queue: queue.Queue[str] = queue.Queue()
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._state = "idle"
        self._level_fn = None
        self._animate_id = None
        self._smoothed_level = 0.0

    def set_level_fn(self, fn):
        self._level_fn = fn

    def _segment_color(self, index, total):
        ratio = index / total
        if ratio < 0.6:
            return "#00CC00"
        elif ratio < 0.8:
            return "#FFCC00"
        else:
            return "#FF3300"

    def _draw_pill_bg(self):
        """Draw rounded pill background."""
        self._canvas.delete("pill")
        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT
        r = h // 2
        border_color = "#555555"
        fill_color = "#222222"

        # Outer border pill
        self._canvas.create_arc(0, 0, h, h, start=90, extent=180,
                                fill=border_color, outline=border_color, tags="pill")
        self._canvas.create_rectangle(r, 0, w - r, h,
                                      fill=border_color, outline=border_color, tags="pill")
        self._canvas.create_arc(w - h, 0, w, h, start=-90, extent=180,
                                fill=border_color, outline=border_color, tags="pill")

        # Inner fill pill (inset 1px)
        self._canvas.create_arc(1, 1, h - 1, h - 1, start=90, extent=180,
                                fill=fill_color, outline=fill_color, tags="pill")
        self._canvas.create_rectangle(r, 1, w - r, h - 1,
                                      fill=fill_color, outline=fill_color, tags="pill")
        self._canvas.create_arc(w - h + 1, 1, w - 1, h - 1, start=-90, extent=180,
                                fill=fill_color, outline=fill_color, tags="pill")

    def _vu_area(self):
        """Return (x1, y1, x2, y2) for the VU meter area inside the pill."""
        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT
        r = h // 2
        pad = _PILL_PAD
        return r + pad, pad + 1, w - r - pad, h - pad - 1

    def _draw_vu_idle(self):
        self._canvas.delete("vu")
        x1, y1, x2, y2 = self._vu_area()
        vu_w = x2 - x1
        seg_w = (vu_w - (_NUM_SEGMENTS - 1) * _SEGMENT_GAP) / _NUM_SEGMENTS

        for i in range(_NUM_SEGMENTS):
            sx1 = x1 + i * (seg_w + _SEGMENT_GAP)
            sx2 = sx1 + seg_w
            self._canvas.create_rectangle(
                sx1, y1, sx2, y2,
                fill="#3A3A3A", outline="", tags="vu",
            )

    def _draw_vu_level(self, level):
        self._canvas.delete("vu")
        x1, y1, x2, y2 = self._vu_area()
        vu_w = x2 - x1
        seg_w = (vu_w - (_NUM_SEGMENTS - 1) * _SEGMENT_GAP) / _NUM_SEGMENTS

        amp = min(level * 12, 1.0)
        lit = int(amp * _NUM_SEGMENTS)

        for i in range(_NUM_SEGMENTS):
            sx1 = x1 + i * (seg_w + _SEGMENT_GAP)
            sx2 = sx1 + seg_w
            if i < lit:
                fill = self._segment_color(i, _NUM_SEGMENTS)
            else:
                fill = "#2A2A2A"
            self._canvas.create_rectangle(
                sx1, y1, sx2, y2,
                fill=fill, outline="", tags="vu",
            )

    def _draw_vu_full(self, color):
        self._canvas.delete("vu")
        x1, y1, x2, y2 = self._vu_area()
        vu_w = x2 - x1
        seg_w = (vu_w - (_NUM_SEGMENTS - 1) * _SEGMENT_GAP) / _NUM_SEGMENTS

        for i in range(_NUM_SEGMENTS):
            sx1 = x1 + i * (seg_w + _SEGMENT_GAP)
            sx2 = sx1 + seg_w
            self._canvas.create_rectangle(
                sx1, y1, sx2, y2,
                fill=color, outline="", tags="vu",
            )

    def _animate_vu(self):
        if self._state == "recording" and self._level_fn:
            raw = self._level_fn()
            if raw > self._smoothed_level:
                self._smoothed_level = raw
            else:
                self._smoothed_level = self._smoothed_level * 0.7 + raw * 0.3
            self._draw_vu_level(self._smoothed_level)
            self._animate_id = self._root.after(50, self._animate_vu)
        else:
            self._animate_id = None

    def _stop_animation(self):
        if self._animate_id:
            self._root.after_cancel(self._animate_id)
            self._animate_id = None

    def _create_window(self):
        self._root = tk.Tk()
        self._root.withdraw()

        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT

        self._root.overrideredirect(True)
        self._root.attributes("-topmost", True)

        bg_color = "#010101"
        self._root.attributes("-transparentcolor", bg_color)
        self._root.configure(bg=bg_color)

        self._canvas = tk.Canvas(
            self._root, width=w, height=h,
            highlightthickness=0, bd=0, bg=bg_color,
        )
        self._canvas.pack()

        self._draw_pill_bg()
        self._draw_vu_idle()

        screen_w = self._root.winfo_screenwidth()
        screen_h = self._root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = screen_h - h - 60
        self._root.geometry(f"{w}x{h}+{x}+{y}")

        self._root.update_idletasks()
        self._root.deiconify()
        self._root.update()

        try:
            hwnd = user32.GetParent(self._root.winfo_id())
            if not hwnd:
                hwnd = self._root.winfo_id()
            ex_style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ex_style |= WS_EX_TOOLWINDOW | WS_EX_TOPMOST
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
            user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0,
                SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE | SWP_SHOWWINDOW,
            )
            idle_alpha = int(config.OVERLAY_IDLE_ALPHA * 255)
            user32.SetLayeredWindowAttributes(hwnd, 0, idle_alpha, LWA_ALPHA)
            self._hwnd = hwnd
        except Exception:
            self._hwnd = None

        self._poll_queue()

    def _set_alpha(self, alpha: float):
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
        self._set_alpha(alpha)

        if state == "recording":
            self._smoothed_level = 0.0
            self._draw_pill_bg()
            self._animate_vu()
        else:
            self._stop_animation()
            self._draw_pill_bg()
            if state in ("transcribing", "correcting"):
                self._draw_vu_full(config.COLOR_TRANSCRIBING)
            elif state == "done":
                self._draw_vu_full(config.COLOR_DONE)
            else:
                self._draw_vu_idle()

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
