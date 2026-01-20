#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine – Voice Narration Module
#  © 2025 L. David Mendoza
#  Provides cross-platform TTS fallback: pyttsx3 → gTTS → macOS "say"
# ===========================================================

import os, tempfile, platform, subprocess

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

def speak(text: str, voice: str = "default", rate: int = 180, lang: str = "en"):
    """High-level speech wrapper."""
    if not text: return

    # --- Option 1: pyttsx3 (local, offline)
    if pyttsx3:
        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", rate)
            if voice != "default":
                for v in engine.getProperty("voices"):
                    if voice.lower() in v.name.lower():
                        engine.setProperty("voice", v.id)
                        break
            engine.say(text)
            engine.runAndWait()
            return
        except Exception:
            pass

    # --- Option 2: gTTS (online, high-quality)
    if gTTS:
        try:
            tts = gTTS(text=text, lang=lang)
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tts.save(tmp.name)
            subprocess.run(["afplay" if platform.system()=="Darwin" else "mpg123", tmp.name])
            os.remove(tmp.name)
            return
        except Exception:
            pass

    # --- Option 3: macOS "say"
    if platform.system() == "Darwin":
        subprocess.run(["say", text])

    # --- Fallback: silent log
    print(f"[Narration skipped] {text}")
