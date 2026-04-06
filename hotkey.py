import ctypes
import threading
import time
import config

user32 = ctypes.windll.user32

# VK codes for left/right variants of modifier keys
_MODIFIER_VARIANTS = {
    0x11: (0xA2, 0xA3),  # Ctrl -> L-Ctrl, R-Ctrl
    0x10: (0xA0, 0xA1),  # Shift -> L-Shift, R-Shift
    0x12: (0xA4, 0xA5),  # Alt -> L-Alt, R-Alt
}


def _is_key_pressed(vk: int) -> bool:
    return (user32.GetAsyncKeyState(vk) & 0x8000) != 0


def _is_modifier_pressed(vk: int) -> bool:
    variants = _MODIFIER_VARIANTS.get(vk)
    if variants:
        return _is_key_pressed(variants[0]) or _is_key_pressed(variants[1])
    return _is_key_pressed(vk)


class PushToTalkHook:
    def __init__(self, settings: config.Settings, on_start=None, on_stop=None):
        self._on_start = on_start or (lambda: None)
        self._on_stop = on_stop or (lambda: None)
        self._settings = settings
        self._is_active = False
        self._running = False
        self._thread = None

    def _poll(self):
        while self._running:
            mod_vk = self._settings.hotkey_modifier_vk
            key_vk = self._settings.hotkey_key_vk

            if mod_vk is not None:
                both_held = _is_modifier_pressed(mod_vk) and _is_key_pressed(key_vk)
            else:
                both_held = _is_key_pressed(key_vk)

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
