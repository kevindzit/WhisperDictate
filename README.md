# WhisperDictate

A fast, GPU-accelerated voice-to-text dictation tool using OpenAI's Whisper. Hold a hotkey to record, release to transcribe and paste.

## Quick Start (Windows 11)

```powershell
git clone https://github.com/kevin36776/WhisperDictate.git C:\WhisperDictation
cd C:\WhisperDictation
Set-ExecutionPolicy Bypass -Scope Process -Force
.\setup.ps1
```

The setup script auto-detects your GPU and installs everything. WhisperDictation will start automatically on boot.

## Hotkey

| Hotkey | Action |
|--------|--------|
| **Hold Ctrl+Alt** | Start recording |
| **Release** | Transcribe and paste at cursor |

---

## Hardware Configurations

### Desktop: RTX 5080 / RTX 50-series

```powershell
# The setup.ps1 script auto-detects and runs:
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu128
```

| Setting | Value |
|---------|-------|
| PyTorch | **Nightly** (required for sm_120) |
| CUDA | 12.8 |
| Model | `turbo` |
| VRAM | ~6GB |

### Laptop: RTX 4060 / RTX 40-series

```powershell
# The setup.ps1 script auto-detects and runs:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

| Setting | Value |
|---------|-------|
| PyTorch | **Stable** |
| CUDA | 12.4 |
| Model | `turbo` |
| VRAM | ~6GB |

### RTX 30-series / RTX 20-series

Same as RTX 40-series (stable PyTorch + CUDA 12.4).

---

**To set up WhisperDictation on any Windows 11 system:**

1. Clone to `C:\WhisperDictation`
2. Run `.\setup.ps1` as Administrator

The script handles everything:
- Installs Python 3.12 + FFmpeg via winget
- Detects GPU generation from `RTX 50xx` / `RTX 40xx` / `RTX 30xx` patterns
- Installs correct PyTorch (nightly for 50-series, stable for others)
- Creates `dictate-env` virtual environment
- Adds to Windows Startup

**Key detection logic in setup.ps1:**
- `RTX 50xx` → PyTorch Nightly + CUDA 12.8 (Blackwell needs nightly)
- `RTX 40xx` → PyTorch Stable + CUDA 12.4
- `RTX 30xx` → PyTorch Stable + CUDA 12.4
- `RTX 20xx` → PyTorch Stable + CUDA 12.4
- No NVIDIA → CPU fallback

See [SETUP.md](SETUP.md) for detailed manual instructions.

---

## Files

| File | Description |
|------|-------------|
| `setup.ps1` | Automated setup (run this) |
| `dictation_app.py` | Main application |
| `run_whisper_dictation.vbs` | Silent launcher for Windows Startup |
| `SETUP.md` | Detailed setup documentation |

## License

MIT License
