import threading
import whisper
import anthropic
import numpy as np
from . import config


class Transcriber:
    def __init__(self, settings: config.Settings, on_status=None):
        self._model = None
        self._model_name = None
        self._model_ready = threading.Event()
        self._on_status = on_status or (lambda s: None)
        self._settings = settings
        self._client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY) if config.ANTHROPIC_API_KEY else None
        self._loading_lock = threading.Lock()

    def load_model(self, model_name: str | None = None):
        with self._loading_lock:
            name = model_name or self._settings.whisper_model
            if self._model and self._model_name == name:
                return
            self._model_ready.clear()
            self._on_status("loading")
            self._model = whisper.load_model(name, device=config.WHISPER_DEVICE)
            self._model_name = name
            self._model_ready.set()
            self._on_status("ready")

    def load_model_async(self, model_name: str | None = None):
        t = threading.Thread(target=self.load_model, args=(model_name,), daemon=True)
        t.start()

    @property
    def is_ready(self) -> bool:
        return self._model_ready.is_set()

    @property
    def current_model(self) -> str:
        return self._model_name or self._settings.whisper_model

    def transcribe(self, audio: np.ndarray) -> str:
        if not self._model_ready.is_set():
            return ""
        self._on_status("transcribing")
        lang = config.WHISPER_LANGUAGES.get(self._settings.language)
        result = self._model.transcribe(
            audio,
            language=lang,
            fp16=True,
        )
        return result["text"].strip()

    def correct(self, text: str) -> str:
        if not text or not self._client:
            return text
        self._on_status("correcting")
        try:
            response = self._client.messages.create(
                model=config.ANTHROPIC_MODEL,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": f"{config.CORRECTION_PROMPT}\n\n{text}"}
                ],
                timeout=config.ANTHROPIC_TIMEOUT,
            )
            corrected = response.content[0].text.strip()
            return corrected if corrected else text
        except Exception:
            return text

    def transcribe_and_correct(self, audio: np.ndarray) -> str:
        text = self.transcribe(audio)
        if not text:
            return ""
        if self._settings.auto_correct:
            text = self.correct(text)
        self._on_status("done")
        return text
