# WhisperDictate

Voice-to-text dictation for Windows. Hold a hotkey, speak, release — your words get transcribed and pasted at the cursor.

Uses [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with `distil-large-v3.5` by default and Silero VAD for local English transcription.

## Setup

Requires Windows, Python 3.12+, and an NVIDIA GPU (CPU works but is slow).

```powershell
git clone https://github.com/kevindzit/WhisperDictate.git C:\WhisperDictation
cd C:\WhisperDictation
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup.ps1
```

The script installs dependencies, verifies `faster_whisper`, saves the model choice,
and adds WhisperDictation to Windows Startup. First launch downloads the selected
model. Setup stops if an install command or dependency verification fails.

## Usage

| Action | Hotkey |
|--------|--------|
| Record | Hold **Ctrl+Alt** |
| Transcribe + paste | Release |

Right-click the system tray icon to reset hotkeys or exit.

## Models

Choose a model during setup:

```powershell
.\setup.ps1 -Model "turbo"
```

| Model option | What it loads |
|--------------|---------------|
| `distil-large-v3.5` | **Default.** `deepdml/faster-distil-whisper-large-v3.5` |
| `turbo` | The faster-whisper `turbo` model |
| `large-v3` | The faster-whisper `large-v3` model |
| `small` | The faster-whisper `small` model |

Setup saves the choice in `model.txt` beside the app. To change it without
reinstalling dependencies, run this from the project folder:

```powershell
Set-Content -Path .\model.txt -Value "large-v3" -Encoding UTF8
```

Exit the running app from the system tray and restart it after changing models.
The startup log shows the model actually selected. Both launchers read the same
file. Without `model.txt`, the app keeps its original `distil-large-v3.5` default.
The file is ignored by Git so each installation can keep its own choice.
Transcription remains set to English for every model.

## Tests

The model selection and backend verification tests use Python's standard library:

```powershell
python -m unittest discover -s tests -v
```

On Windows, also run the PowerShell setup checks:

```powershell
.\tests\test_setup.ps1
```

GitHub Actions runs both checks on Windows with Python 3.12. The tests use stubs
for audio, GPU detection, and model loading. They do not install application
dependencies, download models, record audio, or change Windows Startup.

## Troubleshooting

See [SETUP.md](SETUP.md) for manual setup steps and common fixes.

## License

MIT
