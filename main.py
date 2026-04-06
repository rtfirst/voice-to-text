import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from audio import AudioRecorder
from transcriber import Transcriber
from overlay import Overlay
from tray import TrayIcon
from hotkey import PushToTalkHook
from paste import paste_text, get_foreground_window


class VoiceToText:
    def __init__(self):
        self._shutdown_event = threading.Event()
        self._settings = config.Settings()
        self._overlay = Overlay()
        self._recorder = AudioRecorder()
        self._transcriber = Transcriber(
            settings=self._settings,
            on_status=self._on_transcriber_status,
        )
        self._tray = TrayIcon(
            settings=self._settings,
            on_quit=self._shutdown,
            on_model_change=self._on_model_change,
        )
        self._hotkey = PushToTalkHook(
            settings=self._settings,
            on_start=self._on_recording_start,
            on_stop=self._on_recording_stop,
        )
        self._target_hwnd = None

    def _on_transcriber_status(self, status: str):
        self._overlay.set_state(status)
        status_map = {
            "loading": "Lade Modell...",
            "ready": "Bereit",
            "transcribing": "Transkribiere...",
            "correcting": "Korrigiere...",
            "done": "Bereit",
        }
        if status in status_map:
            self._tray.set_status(status_map[status])

    def _on_model_change(self, model_name: str):
        self._transcriber.load_model_async(model_name)

    def _on_recording_start(self):
        if not self._transcriber.is_ready:
            return
        # Remember which window was active BEFORE recording
        self._target_hwnd = get_foreground_window()
        self._overlay.set_state("recording")
        self._tray.set_status("Aufnahme...")
        self._recorder.start()

    def _on_recording_stop(self):
        if not self._transcriber.is_ready:
            return
        audio = self._recorder.stop()
        target = self._target_hwnd
        if audio is None or len(audio) < config.SAMPLE_RATE * 0.3:
            self._overlay.set_state("idle")
            self._tray.set_status("Bereit")
            return

        def process():
            try:
                result = self._transcriber.transcribe_and_correct(audio)
                if result:
                    paste_text(result, target_hwnd=target)
            except Exception:
                pass
            self._overlay.set_state("done")
            self._tray.set_status("Bereit")

        t = threading.Thread(target=process, daemon=True)
        t.start()

    def _shutdown(self):
        self._shutdown_event.set()
        self._hotkey.stop()
        self._tray.stop()
        self._overlay.stop()

    def run(self):
        self._transcriber.load_model_async()
        self._hotkey.start()
        self._tray.start()
        self._overlay.run()


if __name__ == "__main__":
    app = VoiceToText()
    app.run()
