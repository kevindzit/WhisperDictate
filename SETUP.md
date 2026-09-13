# Setup Guide

## Automated Setup

Run PowerShell as Administrator:

```powershell
cd C:\WhisperDictation
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup.ps1
```

The script:
1. Installs Python 3.12 and FFmpeg via winget
2. Creates a virtual environment (`dictate-env/`)
3. Detects your GPU and installs the correct PyTorch + CUDA
4. Installs all dependencies
5. Verifies `faster_whisper` and saves the selected model in `model.txt`
6. Adds WhisperDictation to Windows Startup

The default model is `distil-large-v3.5`. Other supported choices are `turbo`,
`large-v3`, and `small`:

```powershell
.\setup.ps1 -Model "turbo"
```

Setup stops if an installation command or dependency verification fails.
Verification checks Python imports. First launch still downloads and loads the
selected model. Exit any running copy of the app before restarting it with a new
model choice.

## Manual Setup

If the script fails, do it by hand:

### 1. Prerequisites

```powershell
winget install Python.Python.3.12
winget install Gyan.FFmpeg
```

Restart your terminal after installing.

### 2. Virtual Environment

```powershell
cd C:\WhisperDictation
python -m venv dictate-env
.\dictate-env\Scripts\Activate.ps1
pip install --upgrade pip
```

### 3. PyTorch

```powershell
# RTX 50-series (needs nightly for Blackwell support):
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128

# RTX 20/30/40-series:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# CPU only:
pip install torch torchvision torchaudio
```

### 4. Dependencies

```powershell
pip install -r requirements.txt
```

### 5. Model Selection

From the project folder, save one of the supported model names:

```powershell
Set-Content -Path .\model.txt -Value "distil-large-v3.5" -Encoding UTF8
```

Use `turbo`, `large-v3`, or `small` to choose a different model. Without this file,
the app uses `distil-large-v3.5`. The app reads the file beside `dictation_app.py`,
even when launched from another working directory.

### 6. Startup (optional)

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WhisperDictation.lnk")
$Shortcut.TargetPath = "C:\WhisperDictation\run_whisper_dictation.vbs"
$Shortcut.WorkingDirectory = "C:\WhisperDictation"
$Shortcut.Save()
```

### 7. Test

```powershell
.\dictate-env\Scripts\python.exe dictation_app.py
```

Check the `Using model:` line in the console or `logs/whisper_dictation.log`.
After changing `model.txt`, exit from the system tray and restart the app.

## Troubleshooting

**Wrong model starts**: Check `model.txt` beside the app, then exit and restart
the running copy. Valid choices are `distil-large-v3.5`, `turbo`, `large-v3`, and
`small`. An empty or unsupported value stops startup with a clear error.

**Dependency verification failed**: Read the Python error above the setup failure.
The required backend is `faster_whisper`, installed by `requirements.txt`.
Installing the separate `whisper` package does not satisfy this check.

**"CUDA not available"** — Check that NVIDIA drivers are installed (`nvidia-smi`). Reinstall PyTorch with the correct CUDA version for your GPU.

**"PyTorch not compatible with GPU"** — RTX 50-series requires PyTorch nightly. Uninstall and reinstall with the nightly command above.

**Slow transcription** — Make sure the console shows `Using device: cuda`. If it says `cpu`, PyTorch isn't seeing your GPU.

**Hotkeys stop working** — Right-click the system tray icon and click Reset. This can happen after fullscreen games.

## File Structure

```
C:\WhisperDictation\
├── dictate-env/                   # Virtual environment
├── logs/                          # Application logs
├── dictation_app.py               # Main application
├── model.txt                      # Local model choice, created by setup
├── requirements.txt               # Dependencies
├── setup.ps1                      # Automated setup
├── run_whisper_dictation.bat      # Console launcher
├── run_whisper_dictation.vbs      # Silent launcher (Startup)
├── README.md
└── SETUP.md
```
