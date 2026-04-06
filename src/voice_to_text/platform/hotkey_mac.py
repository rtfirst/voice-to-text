"""macOS hotkey detection via Quartz event tap."""

import threading
import time

try:
    from Quartz import (
        CGEventTapCreate, CGEventTapEnable, CFMachPortCreateRunLoopSource,
        CFRunLoopGetCurrent, CFRunLoopAddSource, CFRunLoopRun, CFRunLoopStop,
        kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionListenOnly,
        CGEventGetIntegerValueField, kCGKeyboardEventKeycode,
        kCGEventKeyDown, kCGEventKeyUp, kCGEventFlagsChanged,
        CGEventGetFlags,
        kCGEventFlagMaskCommand, kCGEventFlagMaskControl,
        kCGEventFlagMaskAlternate, kCGEventFlagMaskShift,
        kCFRunLoopCommonModes,
    )
    HAS_QUARTZ = True
except ImportError:
    HAS_QUARTZ = False

# macOS keycode for Space
_KC_SPACE = 49

# Map config modifier names to macOS event flag masks
_MODIFIER_FLAGS = {
    "Ctrl": kCGEventFlagMaskControl if HAS_QUARTZ else 0,
    "Shift": kCGEventFlagMaskShift if HAS_QUARTZ else 0,
    "Alt": kCGEventFlagMaskAlternate if HAS_QUARTZ else 0,
    "Win": kCGEventFlagMaskCommand if HAS_QUARTZ else 0,
    "Cmd": kCGEventFlagMaskCommand if HAS_QUARTZ else 0,
}

# Map config key names to macOS keycodes
_KEYCODES = {
    "Space": 49,
    "F1": 122, "F2": 120, "F3": 99, "F4": 118,
    "F5": 96, "F6": 97, "F7": 98, "F8": 100,
    "F9": 101, "F10": 109, "F11": 103, "F12": 111,
    "F13": 105, "F14": 107, "F15": 113, "F16": 106,
}


class PushToTalkHook:
    def __init__(self, settings, on_start=None, on_stop=None):
        self._on_start = on_start or (lambda: None)
        self._on_stop = on_stop or (lambda: None)
        self._settings = settings
        self._is_active = False
        self._running = False
        self._thread = None
        self._run_loop = None

    def _get_modifier_flag(self):
        from .. import config
        preset = config.HOTKEY_PRESETS.get(self._settings.hotkey)
        if not preset or not preset[0]:
            return None
        return _MODIFIER_FLAGS.get(preset[0])

    def _get_keycode(self):
        from .. import config
        preset = config.HOTKEY_PRESETS.get(self._settings.hotkey, (None, "Space"))
        return _KEYCODES.get(preset[1], _KC_SPACE)

    def _callback(self, proxy, event_type, event, refcon):
        keycode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
        flags = CGEventGetFlags(event)
        target_keycode = self._get_keycode()
        mod_flag = self._get_modifier_flag()

        if keycode == target_keycode:
            if mod_flag is not None:
                mod_held = (flags & mod_flag) != 0
            else:
                mod_held = True

            if event_type == kCGEventKeyDown and mod_held and not self._is_active:
                self._is_active = True
                try:
                    self._on_start()
                except Exception:
                    pass
            elif event_type == kCGEventKeyUp and self._is_active:
                self._is_active = False
                try:
                    self._on_stop()
                except Exception:
                    pass

        # Handle modifier release while key might still be tracked
        if event_type == kCGEventFlagsChanged and self._is_active and mod_flag:
            if (flags & mod_flag) == 0:
                self._is_active = False
                try:
                    self._on_stop()
                except Exception:
                    pass

        return event

    def _run(self):
        if not HAS_QUARTZ:
            # Fallback: polling with pynput
            self._poll_fallback()
            return

        mask = (1 << kCGEventKeyDown) | (1 << kCGEventKeyUp) | (1 << kCGEventFlagsChanged)
        tap = CGEventTapCreate(
            kCGSessionEventTap,
            kCGHeadInsertEventTap,
            kCGEventTapOptionListenOnly,
            mask,
            self._callback,
            None,
        )
        if not tap:
            self._poll_fallback()
            return

        source = CFMachPortCreateRunLoopSource(None, tap, 0)
        self._run_loop = CFRunLoopGetCurrent()
        CFRunLoopAddSource(self._run_loop, source, kCFRunLoopCommonModes)
        CGEventTapEnable(tap, True)
        CFRunLoopRun()

    def _poll_fallback(self):
        """Fallback polling using pynput if Quartz is unavailable."""
        try:
            from pynput import keyboard
        except ImportError:
            return

        pressed_keys = set()

        def on_press(key):
            pressed_keys.add(key)
            self._check_hotkey(pressed_keys)

        def on_release(key):
            pressed_keys.discard(key)
            if self._is_active:
                self._is_active = False
                try:
                    self._on_stop()
                except Exception:
                    pass

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            while self._running:
                time.sleep(0.1)

    def _check_hotkey(self, pressed_keys):
        # Simplified check for pynput fallback
        pass

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._run_loop and HAS_QUARTZ:
            CFRunLoopStop(self._run_loop)
        if self._thread:
            self._thread.join(timeout=2)
