# Changelog

## [1.1.0] - 2026-04-06

### Added
- macOS support (Quartz event tap for hotkeys, pbcopy/osascript for paste)
- Auto-detection of GPU device: CUDA (Windows), MPS (Apple Silicon), CPU fallback
- macOS autostart via LaunchAgent plist
- Platform abstraction layer (`platform/` module)

### Changed
- Restructured into `src/voice_to_text/` package with platform-specific modules
- GPU device is now auto-detected instead of hardcoded to CUDA

## [1.0.0] - 2026-04-06

### Added
- Push-to-Talk speech-to-text with configurable hotkey (default: Ctrl+Space)
- Local transcription via OpenAI Whisper (CUDA) with model selection (tiny, small, medium, large-v3, turbo)
- Optional text correction via Anthropic API (Haiku)
- Live VU meter overlay with pill-shaped frame at the bottom of the screen
- Language selection (auto, German, English)
- Terminal-aware paste detection (Ctrl+V, Ctrl+Shift+V, Shift+Insert)
- System tray icon with settings menu
- Persistent settings saved to `settings.json`
- Windows autostart support via registry
- Foreground window restoration after transcription
