# Voice-to-Text

Windows 11 Hintergrundprogramm für Spracheingabe per Push-to-Talk. Transkribiert lokal mit OpenAI Whisper (CUDA) und korrigiert optional über die Anthropic API (Haiku). Der transkribierte Text wird automatisch in die aktive Anwendung eingefügt — Editor, Browser, Terminal.

## Voraussetzungen

- Windows 11
- Python 3.13+ mit PyTorch (CUDA)
- NVIDIA GPU (getestet mit RTX 3070, 8 GB VRAM)
- Installierte Pakete: `openai-whisper`, `anthropic`, `pystray`, `pywin32`, `Pillow`, `numpy`, `sounddevice`

## Installation

```bash
pip install sounddevice
```

Alle anderen Abhängigkeiten sollten bereits vorhanden sein (PyTorch, Whisper, Anthropic SDK etc.).

### API-Key

Für die optionale Textkorrektur wird ein Anthropic API-Key benötigt. Erstelle eine `.env`-Datei im Projektordner:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Starten

```bash
# Mit Konsolenfenster (für Debugging)
python main.py

# Ohne Konsolenfenster (für den Alltag)
pythonw main.py
```

## Bedienung

| Aktion | Beschreibung |
|--------|-------------|
| **Ctrl+Leertaste gedrückt halten** | Aufnahme starten (Overlay wird rot) |
| **Ctrl+Leertaste loslassen** | Aufnahme stoppen → Transkription → Text wird eingefügt |
| **Tray-Icon Rechtsklick** | Einstellungen und Beenden |

### Overlay-Farben

| Farbe | Bedeutung |
|-------|-----------|
| Grau (transparent) | Bereit |
| Rot | Aufnahme läuft |
| Gelb | Transkription/Korrektur läuft |
| Grün (kurz) | Fertig, Text eingefügt |

## Einstellungen (Tray-Menü)

- **Modell** — Whisper-Modellgröße: tiny, small, medium, large-v3, turbo
- **Sprache** — auto, Deutsch, English
- **Auto-Korrektur** — Textkorrektur via Anthropic API an/aus

Einstellungen werden in `settings.json` gespeichert und bleiben nach Neustart erhalten.

## Autostart

```bash
# Aktivieren
python setup_autostart.py

# Deaktivieren
python setup_autostart.py --disable
```

## Projektstruktur

```
voice-to-text/
  main.py              Orchestrierung, Einstiegspunkt
  hotkey.py             Ctrl+Space Push-to-Talk (GetAsyncKeyState)
  audio.py              Mikrofon-Aufnahme (sounddevice, 16kHz mono)
  transcriber.py        Whisper-Transkription + Anthropic API Korrektur
  paste.py              Clipboard + Paste (Ctrl+V / Ctrl+Shift+V / Shift+Insert)
  overlay.py            Pill-Overlay am unteren Bildschirmrand (tkinter)
  tray.py               System Tray Icon mit Einstellungsmenü (pystray)
  config.py             Konfiguration + persistente Settings
  setup_autostart.py    Windows-Autostart verwalten
  .env                  Anthropic API-Key (nicht im Repo)
  settings.json         Benutzereinstellungen (nicht im Repo)
```

## Paste-Erkennung

Das Tool erkennt den Typ des Vordergrundfensters und wählt die passende Einfügemethode:

- **Standard-Apps** (Editor, Browser, IDE) → Ctrl+V
- **Windows Terminal** → Ctrl+Shift+V
- **mintty / Git Bash** → Shift+Insert
- **Legacy cmd.exe** → Shift+Insert
