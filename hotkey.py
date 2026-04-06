import ctypes
import threading
import time
import config

user32 = ctypes.windll.user32


def _is_key_pressed(vk: int) -> bool:
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0


class PushToTalkHook:
    def __init__(self, on_start=None, on_stop=None):
        self._on_start = on_start or (lambda: None)
        self._on_stop = on_stop or (lambda: None)
        self._is_active = False
        self._running = False
        self._thread = None

    def _poll(self):
        while self._running:
            ctrl = _is_key_pressed(0xA2) or _is_key_pressed(0xA3)
            space = _is_key_pressed(config.HOTKEY_KEY)
            both_held = ctrl and space

            if both_held and not self._is_active:
                self._is_active = True
                try:
                    self._on_start()
                except Exception:
                    pass
            elif not both_held and self._is_active:
                self._is_active = False
                try:
                    self._on_stop()
                except Exception:
                    pass

            time.sleep(0.03)

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._poll, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)
