# Voice-to-Text

A Windows 11 background application for speech input via Push-to-Talk. Transcribes locally using OpenAI Whisper (CUDA) and optionally corrects text via the Anthropic API (Haiku). The transcribed text is automatically pasted into the active application — editor, browser, or terminal.

## Features

- **Push-to-Talk** — hold a configurable hotkey to record, release to transcribe and paste
- **Local transcription** — runs Whisper on your GPU, no cloud dependency for speech-to-text
- **Optional AI correction** — fixes grammar and punctuation via Anthropic API
- **Live VU meter** — pill-shaped overlay at the bottom of the screen reacts to your voice
- **Terminal-aware paste** — auto-detects window type (Ctrl+V, Ctrl+Shift+V, or Shift+Insert)
- **Configurable via tray menu** — hotkey, model size, language, auto-correction
- **Persistent settings** — saved to `settings.json`, survives restarts

## Requirements

- Windows 11
- Python 3.13+ with PyTorch (CUDA)
- NVIDIA GPU (tested with RTX 3070, 8 GB VRAM)
- Installed packages: `openai-whisper`, `anthropic`, `pystray`, `pywin32`, `Pillow`, `numpy`, `sounddevice`

## Installation

```bash
pip install sounddevice
```

All other dependencies should already be present (PyTorch, Whisper, Anthropic SDK, etc.).

### API Key

For optional text correction, an Anthropic API key is required. Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# With console window (for debugging)
python main.py

# Without console window (for daily use)
pythonw main.py
```

| Action | Description |
|--------|-------------|
| **Hold hotkey** | Start recording (VU meter reacts live) |
| **Release hotkey** | Stop recording, transcribe, paste into active app |
| **Right-click tray icon** | Settings and quit |

### VU Meter Overlay

| State | Display |
|-------|---------|
| Idle | Dark segments, semi-transparent |
| Recording | Live level: green, yellow, red |
| Transcribing | All segments yellow |
| Done | All segments green (briefly) |

## Settings (Tray Menu)

- **Hotkey** — Ctrl+Space, Alt+Space, Ctrl+F9, F13, and more
- **Model** — Whisper model size: tiny, small, medium, large-v3, turbo
- **Language** — auto, Deutsch, English
- **Auto-Correction** — text correction via Anthropic API on/off

Settings are saved to `settings.json` and persist across restarts.

## Autostart

```bash
# Enable
python setup_autostart.py

# Disable
python setup_autostart.py --disable
```

## Project Structure

```
voice-to-text/
  main.py                        Entry point (thin wrapper)
  setup_autostart.py             Windows autostart management
  requirements.txt
  src/
    voice_to_text/
      __init__.py                Package marker
      __main__.py                python -m voice_to_text support
      app.py                     Main orchestration (VoiceToText class)
      audio.py                   Microphone recording (sounddevice, 16kHz mono)
      config.py                  Configuration and persistent settings
      hotkey.py                  Push-to-Talk hotkey (GetAsyncKeyState polling)
      overlay.py                 VU meter overlay with pill frame (tkinter)
      paste.py                   Window-type detection and clipboard paste
      transcriber.py             Whisper transcription + Anthropic API correction
      tray.py                    System tray icon with settings menu (pystray)
```

## Paste Detection

The tool detects the foreground window type and uses the appropriate paste method:

- **Standard apps** (editor, browser, IDE) — Ctrl+V
- **Windows Terminal** — Ctrl+Shift+V
- **mintty / Git Bash** — Shift+Insert
- **Legacy cmd.exe** — Shift+Insert

## License

[MIT](LICENSE)
