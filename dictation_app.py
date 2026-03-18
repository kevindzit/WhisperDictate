import os
import time
import threading
import keyboard
import pyaudio
import wave
import numpy as np
import pyperclip
from faster_whisper import WhisperModel
import torch
import pystray
from PIL import Image, ImageDraw
import tempfile

# Use GPU if available (CUDA), otherwise fallback to CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load distil-large-v3.5 via faster-whisper (CTranslate2 backend)
# Faster than turbo, slightly more accurate on short audio, English-optimized
compute_type = "float16" if device == "cuda" else "float32"
model = WhisperModel("deepdml/faster-distil-whisper-large-v3.5", device=device, compute_type=compute_type)

recording = False
audio_frames = []
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
p = pyaudio.PyAudio()

def create_icon():
    image = Image.new('RGB', (64, 64), color = (255, 255, 255))
    dc = ImageDraw.Draw(image)
    dc.rectangle((20, 20, 44, 50), fill=(0, 0, 0))
    dc.rectangle((27, 10, 37, 20), fill=(0, 0, 0))
    dc.rectangle((20, 50, 44, 54), fill=(0, 0, 0))
    return image

def start_recording():
    global recording, audio_frames
    if not recording:
        audio_frames = []
        recording = True
        threading.Thread(target=record_audio).start()
        print("Recording started...")

def stop_recording():
    global recording
    if recording:
        recording = False
        print("Recording stopped, transcribing...")

        time.sleep(0.5)

        if audio_frames:
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_name = temp_file.name
            temp_file.close()

            with wave.open(temp_file_name, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(audio_frames))

            # Transcribe with faster-whisper: VAD trims silence, initial_prompt aids accuracy
            segments, info = model.transcribe(
                temp_file_name,
                language="en",
                beam_size=5,
                vad_filter=True,
                initial_prompt="Dictated text.",
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()

            pyperclip.copy(text)

            os.unlink(temp_file_name)

            print(f"Transcribed: {text}")

            keyboard.press_and_release('ctrl+v')

def record_audio():
    stream = p.open(format=FORMAT,
                   channels=CHANNELS,
                   rate=RATE,
                   input=True,
                   frames_per_buffer=CHUNK)

    global recording, audio_frames
    while recording:
        data = stream.read(CHUNK)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()

def reset_hooks(icon=None):
    """Reset keyboard hooks when they stop working (e.g., after playing games)"""
    global recording, audio_frames

    print("Resetting hooks...")

    # Stop any ongoing recording
    if recording:
        recording = False
        audio_frames = []
        print("  Stopped stuck recording")

    # Rehook keyboard (unhook all and re-register)
    try:
        keyboard.unhook_all()
        keyboard.hook(on_hotkey)
        print("  Keyboard hooks reset")
    except Exception as e:
        print(f"  Keyboard reset error: {e}")

    print("Reset complete! Hotkeys should work now.")

def on_exit(icon):
    icon.stop()
    keyboard.unhook_all()
    p.terminate()
    os._exit(0)

def check_ctrl_alt(e):
    return keyboard.is_pressed('ctrl') and keyboard.is_pressed('alt')

def on_hotkey(e):
    if e.event_type == keyboard.KEY_DOWN and check_ctrl_alt(e):
        start_recording()
    elif e.event_type == keyboard.KEY_UP and not check_ctrl_alt(e):
        stop_recording()

def main():
    keyboard.hook(on_hotkey)

    icon = pystray.Icon("WhisperDictation")
    icon.icon = create_icon()
    icon.menu = pystray.Menu(
        pystray.MenuItem("Reset", reset_hooks),
        pystray.MenuItem("Exit", on_exit)
    )
    icon.title = "Whisper Dictation"

    print("Whisper Dictation started!")
    print("  Model: distil-large-v3.5 (faster-whisper)")
    print(f"  Device: {device} ({compute_type})")
    print("  VAD: enabled")
    print("  Hotkey: Hold Ctrl+Alt to record")
    icon.run()

if __name__ == "__main__":
    main()
