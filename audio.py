import threading
import numpy as np
import sounddevice as sd
import config


class AudioRecorder:
    def __init__(self):
        self._chunks: list[np.ndarray] = []
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._recording = False

    def _callback(self, indata, frames, time_info, status):
        with self._lock:
            if self._recording:
                self._chunks.append(indata.copy())

    def start(self):
        with self._lock:
            self._chunks.clear()
            self._recording = True
        self._stream = sd.InputStream(
            samplerate=config.SAMPLE_RATE,
            channels=config.CHANNELS,
            dtype="float32",
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> np.ndarray | None:
        with self._lock:
            self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        with self._lock:
            if not self._chunks:
                return None
            audio = np.concatenate(self._chunks, axis=0).flatten()
            self._chunks.clear()
        return audio
