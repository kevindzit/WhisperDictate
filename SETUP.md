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
5. Adds WhisperDictation to Windows Startup

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

### 5. Startup (optional)

```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\WhisperDictation.lnk")
$Shortcut.TargetPath = "C:\WhisperDictation\run_whisper_dictation.vbs"
$Shortcut.WorkingDirectory = "C:\WhisperDictation"
$Shortcut.Save()
```

### 6. Test

```powershell
.\dictate-env\Scripts\python.exe dictation_app.py
```

## Troubleshooting

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
├── requirements.txt               # Dependencies
├── setup.ps1                      # Automated setup
├── run_whisper_dictation.bat      # Console launcher
├── run_whisper_dictation.vbs      # Silent launcher (Startup)
├── README.md
└── SETUP.md
```
