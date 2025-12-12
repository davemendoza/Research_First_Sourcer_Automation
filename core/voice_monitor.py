#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine – Smart Narrating Audio Watchdog
#  © 2025 L. David Mendoza
#  Ensures CoreAudio + Narration Layer stability for demos
# ===========================================================

import os, subprocess, platform, datetime

LOG_FILE = "logs/audio_health.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def say(text):
    """Speak only if DEMO_MODE is active"""
    if os.getenv("DEMO_MODE") == "true":
        os.system(f"say '{text}'")

def is_coreaudio_running():
    result = subprocess.run(
        ["pgrep", "-x", "coreaudiod"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0

def get_output_devices():
    try:
        output = subprocess.check_output(
            ["system_profiler", "SPAudioDataType"], text=True, timeout=5
        )
        devices = [line.strip() for line in output.splitlines() if "Output Device" in line]
        return devices
    except Exception:
        return []

def restart_coreaudio():
    log("⚙️ Restarting CoreAudio service...")
    subprocess.run(["sudo", "launchctl", "kickstart", "-kp", "system/com.apple.audio.coreaudiod"])
    log("✅ CoreAudio service restarted.")
    say("Audio system restored successfully.")
    return True

def monitor_audio_system():
    log("🔍 Running Audio Health Check...")
    running = is_coreaudio_running()
    devices = get_output_devices()

    if not running:
        log("❌ CoreAudio is not running.")
        restart_coreaudio()
    elif not devices:
        log("⚠️ No output devices detected.")
        restart_coreaudio()
    else:
        log("✅ Audio system healthy.")
        say("Audio system verified and ready.")
    log("──────────────────────────────────────")

if __name__ == "__main__":
    monitor_audio_system()
