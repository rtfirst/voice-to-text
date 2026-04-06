# Voice-to-Text

A cross-platform background application for speech input via Push-to-Talk. Transcribes locally using OpenAI Whisper (GPU-accelerated) and optionally corrects text via the Anthropic API (Haiku). The transcribed text is automatically pasted into the active application — editor, browser, or terminal.

Supports **Windows 11** and **macOS**.

## Features

- **Push-to-Talk** — hold a configurable hotkey to record, release to transcribe and paste
- **Local transcription** — runs Whisper on your GPU, no cloud dependency for speech-to-text
- **Optional AI correction** — fixes grammar and punctuation via Anthropic API
- **Live VU meter** — pill-shaped overlay at the bottom of the screen reacts to your voice
- **Smart paste** — auto-detects window type and uses the appropriate paste method
- **Configurable via tray menu** — hotkey, model size, language, auto-correction
- **Persistent settings** — saved to `settings.json`, survives restarts
- **Cross-platform** — Windows (CUDA) and macOS (MPS / CPU)

## Requirements

- Python 3.13+
- [OpenAI Whisper](https://github.com/openai/whisper) with PyTorch

### Windows
- NVIDIA GPU with CUDA support (tested with RTX 3070, 8 GB VRAM)
- PyTorch with CUDA
- Packages: `pywin32`

### macOS
- Apple Silicon (MPS acceleration) or Intel (CPU fallback)
- PyTorch with MPS support (macOS 12.3+)
- Accessibility permissions required (System Settings → Privacy & Security → Accessibility)

### Both platforms
- `openai-whisper`, `anthropic`, `pystray`, `Pillow`, `numpy`, `sounddevice`

## Installation

```bash
pip install sounddevice
```

All other dependencies should already be present (PyTorch, Whisper, Anthropic SDK, etc.).

### macOS additional setup

Grant Accessibility permissions to your terminal or Python to allow global hotkey detection and keystroke simulation:

**System Settings → Privacy & Security → Accessibility** → add Terminal / iTerm2 / Python

### API Key

For optional text correction, an Anthropic API key is required. Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# With console output (for debugging)
python main.py

# Without console window (Windows only)
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
| Recording | Live level: green → yellow → red |
| Transcribing | All segments yellow |
| Done | All segments green (briefly) |

## Settings (Tray Menu)

- **Hotkey** — Ctrl+Space, Alt+Space, Ctrl+F9, F13, and more
- **Model** — Whisper model size: tiny, small, medium, large-v3, turbo
- **Language** — auto, Deutsch, English
- **Auto-Correction** — text correction via Anthropic API on/off

Settings are saved to `settings.json` and persist across restarts.

## GPU Acceleration

The application auto-detects the best available compute device:

| Platform | Device | Notes |
|----------|--------|-------|
| Windows + NVIDIA | CUDA | Best performance |
| macOS Apple Silicon | MPS | Good performance on M1/M2/M3 |
| Any | CPU | Fallback, slower |

## Autostart

```bash
# Enable
python setup_autostart.py

# Disable
python setup_autostart.py --disable
```

- **Windows**: adds a registry entry under `HKCU\...\Run`
- **macOS**: creates a LaunchAgent plist in `~/Library/LaunchAgents/`

## Project Structure

```
voice-to-text/
  main.py                                Entry point
  setup_autostart.py                     Autostart management (Windows + macOS)
  requirements.txt
  src/
    voice_to_text/
      __init__.py
      __main__.py                        python -m voice_to_text
      app.py                             Main orchestration
      audio.py                           Microphone recording (sounddevice)
      config.py                          Configuration + persistent settings
      hotkey.py                          Hotkey dispatcher
      overlay.py                         VU meter overlay (tkinter)
      paste.py                           Paste dispatcher
      transcriber.py                     Whisper + Anthropic API
      tray.py                            System tray menu (pystray)
      platform/
        __init__.py                      Platform detection
        hotkey_win.py                    Windows: GetAsyncKeyState polling
        hotkey_mac.py                    macOS: Quartz event tap
        paste_win.py                     Windows: win32 clipboard + SendInput
        paste_mac.py                     macOS: pbcopy + osascript
        overlay_win.py                   Windows: Win32 layered window
        overlay_mac.py                   macOS: tkinter alpha
```

## Paste Detection (Windows)

On Windows, the tool detects the foreground window type:

- **Standard apps** (editor, browser, IDE) → Ctrl+V
- **Windows Terminal** → Ctrl+Shift+V
- **mintty / Git Bash** → Shift+Insert
- **Legacy cmd.exe** → Shift+Insert

On macOS, Cmd+V is used universally.

## License

[MIT](LICENSE)
