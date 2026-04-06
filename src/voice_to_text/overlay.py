"""VU meter overlay — pill-shaped widget at the bottom of the screen."""

import queue
import sys
import tkinter as tk
from . import config

if sys.platform == "darwin":
    from .platform import overlay_mac as _platform
else:
    from .platform import overlay_win as _platform

_NUM_SEGMENTS = 20
_SEGMENT_GAP = 1
_PILL_PAD = 2


class Overlay:
    def __init__(self):
        self._queue: queue.Queue[str] = queue.Queue()
        self._root: tk.Tk | None = None
        self._canvas: tk.Canvas | None = None
        self._state = "idle"
        self._level_fn = None
        self._animate_id = None
        self._smoothed_level = 0.0
        self._hwnd = None

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
        self._canvas.delete("pill")
        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT
        r = h // 2

        self._canvas.create_arc(0, 0, h, h, start=90, extent=180,
                                fill="#555555", outline="#555555", tags="pill")
        self._canvas.create_rectangle(r, 0, w - r, h,
                                      fill="#555555", outline="#555555", tags="pill")
        self._canvas.create_arc(w - h, 0, w, h, start=-90, extent=180,
                                fill="#555555", outline="#555555", tags="pill")

        self._canvas.create_arc(1, 1, h - 1, h - 1, start=90, extent=180,
                                fill="#222222", outline="#222222", tags="pill")
        self._canvas.create_rectangle(r, 1, w - r, h - 1,
                                      fill="#222222", outline="#222222", tags="pill")
        self._canvas.create_arc(w - h + 1, 1, w - 1, h - 1, start=-90, extent=180,
                                fill="#222222", outline="#222222", tags="pill")

    def _vu_area(self):
        w = config.OVERLAY_WIDTH
        h = config.OVERLAY_HEIGHT
        r = h // 2
        return r + _PILL_PAD, _PILL_PAD + 1, w - r - _PILL_PAD, h - _PILL_PAD - 1

    def _draw_vu_idle(self):
        self._canvas.delete("vu")
        x1, y1, x2, y2 = self._vu_area()
        vu_w = x2 - x1
        seg_w = (vu_w - (_NUM_SEGMENTS - 1) * _SEGMENT_GAP) / _NUM_SEGMENTS
        for i in range(_NUM_SEGMENTS):
            sx1 = x1 + i * (seg_w + _SEGMENT_GAP)
            sx2 = sx1 + seg_w
            self._canvas.create_rectangle(sx1, y1, sx2, y2,
                                          fill="#3A3A3A", outline="", tags="vu")

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
            fill = self._segment_color(i, _NUM_SEGMENTS) if i < lit else "#3A3A3A"
            self._canvas.create_rectangle(sx1, y1, sx2, y2,
                                          fill=fill, outline="", tags="vu")

    def _draw_vu_full(self, color):
        self._canvas.delete("vu")
        x1, y1, x2, y2 = self._vu_area()
        vu_w = x2 - x1
        seg_w = (vu_w - (_NUM_SEGMENTS - 1) * _SEGMENT_GAP) / _NUM_SEGMENTS
        for i in range(_NUM_SEGMENTS):
            sx1 = x1 + i * (seg_w + _SEGMENT_GAP)
            sx2 = sx1 + seg_w
            self._canvas.create_rectangle(sx1, y1, sx2, y2,
                                          fill=color, outline="", tags="vu")

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

        bg_color = _platform.get_bg_color()
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

        self._hwnd = _platform.setup_window(self._root)

        alpha = config.OVERLAY_IDLE_ALPHA
        if self._hwnd:
            _platform.set_alpha(self._hwnd, alpha)
        else:
            self._root.attributes("-alpha", alpha)

        self._poll_queue()

    def _set_alpha(self, alpha: float):
        if self._hwnd:
            _platform.set_alpha(self._hwnd, alpha)
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
