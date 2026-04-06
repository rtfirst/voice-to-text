import threading
from PIL import Image, ImageDraw
import pystray
import config


class TrayIcon:
    def __init__(self, settings: config.Settings, on_quit=None, on_model_change=None):
        self._on_quit = on_quit or (lambda: None)
        self._on_model_change = on_model_change or (lambda m: None)
        self._settings = settings
        self._icon: pystray.Icon | None = None
        self._status = "Lade Modell..."

    def _create_icon_image(self) -> Image.Image:
        img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle([20, 8, 44, 36], radius=8, fill="#4488CC")
        draw.arc([16, 24, 48, 48], start=0, end=180, fill="#4488CC", width=3)
        draw.line([32, 48, 32, 56], fill="#4488CC", width=3)
        draw.line([22, 56, 42, 56], fill="#4488CC", width=3)
        return img

    def _toggle_auto_correct(self, icon, item):
        self._settings.auto_correct = not self._settings.auto_correct
        self._settings.save()
        icon.update_menu()

    def _select_model(self, model_name):
        def handler(icon, item):
            if model_name != self._settings.whisper_model:
                self._settings.whisper_model = model_name
                self._settings.save()
                icon.update_menu()
                self._on_model_change(model_name)
        return handler

    def _is_current_model(self, model_name):
        def check(item):
            return self._settings.whisper_model == model_name
        return check

    def _is_auto_correct_on(self, item):
        return self._settings.auto_correct

    def _select_hotkey(self, hotkey_name):
        def handler(icon, item):
            if hotkey_name != self._settings.hotkey:
                self._settings.hotkey = hotkey_name
                self._settings.save()
                icon.update_menu()
        return handler

    def _is_current_hotkey(self, hotkey_name):
        def check(item):
            return self._settings.hotkey == hotkey_name
        return check

    def _select_language(self, lang_name):
        def handler(icon, item):
            if lang_name != self._settings.language:
                self._settings.language = lang_name
                self._settings.save()
                icon.update_menu()
        return handler

    def _is_current_language(self, lang_name):
        def check(item):
            return self._settings.language == lang_name
        return check

    def _build_menu(self):
        model_items = []
        for m in config.WHISPER_MODELS:
            model_items.append(
                pystray.MenuItem(
                    m,
                    self._select_model(m),
                    checked=self._is_current_model(m),
                    radio=True,
                )
            )

        lang_items = []
        for lang_name in config.WHISPER_LANGUAGES:
            lang_items.append(
                pystray.MenuItem(
                    lang_name,
                    self._select_language(lang_name),
                    checked=self._is_current_language(lang_name),
                    radio=True,
                )
            )

        hotkey_items = []
        for hk_name in config.HOTKEY_PRESETS:
            hotkey_items.append(
                pystray.MenuItem(
                    hk_name,
                    self._select_hotkey(hk_name),
                    checked=self._is_current_hotkey(hk_name),
                    radio=True,
                )
            )

        return pystray.Menu(
            pystray.MenuItem(
                lambda _: f"Status: {self._status}",
                None,
                enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Hotkey", pystray.Menu(*hotkey_items)),
            pystray.MenuItem("Modell", pystray.Menu(*model_items)),
            pystray.MenuItem("Sprache", pystray.Menu(*lang_items)),
            pystray.MenuItem(
                "Auto-Korrektur",
                self._toggle_auto_correct,
                checked=self._is_auto_correct_on,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Beenden", self._quit),
        )

    def _quit(self, icon, item):
        self._on_quit()
        icon.stop()

    def set_status(self, status: str):
        self._status = status
        if self._icon:
            self._icon.update_menu()

    def start(self):
        self._icon = pystray.Icon(
            name="VoiceToText",
            icon=self._create_icon_image(),
            title="Voice-to-Text",
            menu=self._build_menu(),
        )
        t = threading.Thread(target=self._icon.run, daemon=True)
        t.start()

    def stop(self):
        if self._icon:
            self._icon.stop()
