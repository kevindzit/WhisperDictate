# WhisperDictate

Voice-to-text dictation for Windows. Hold a hotkey, speak, release — your words get transcribed and pasted at the cursor.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with the `distil-large-v3.5` model and Silero VAD for fast, accurate English transcription on any NVIDIA GPU.

## Setup

Requires Windows, Python 3.12+, and an NVIDIA GPU (CPU works but is slow).

```powershell
git clone https://github.com/kevin36776/WhisperDictate.git C:\WhisperDictation
cd C:\WhisperDictation
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup.ps1
```

The script installs everything and adds WhisperDictation to Windows Startup. First launch downloads the model (~1.5 GB).

## Usage

| Action | Hotkey |
|--------|--------|
| Record | Hold **Ctrl+Alt** |
| Transcribe + paste | Release |

Right-click the system tray icon to reset hotkeys or exit.

## Models

The default is `distil-large-v3.5` — the fastest accurate option for English. To change models, edit the model name in `dictation_app.py` line 22.

| VRAM | Model | Notes |
|------|-------|-------|
| ~4 GB | `deepdml/faster-distil-whisper-large-v3.5` | **Default.** Fastest + accurate, English only |
| ~4 GB | `deepdml/faster-whisper-large-v3-turbo-ct2` | Fast, multilingual |
| ~10 GB | `Systran/faster-whisper-large-v3` | Slower, highest accuracy, multilingual |
| ~2 GB | `small` | Limited VRAM or CPU |

## Troubleshooting

See [SETUP.md](SETUP.md) for manual setup steps and common fixes.

## License

MIT
