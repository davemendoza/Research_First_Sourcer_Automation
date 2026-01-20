#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine – Demo Narration Module
#  © 2025 L. David Mendoza
#  Narrated live introduction and transitions for conference demos
# ===========================================================

import os, datetime, platform, tempfile

LOG_FILE = "logs/narration.log"

def log(message):
    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def say(text):
    """Speak text only if DEMO_MODE=true"""
    if os.getenv("DEMO_MODE") != "true":
        return
    if platform.system() == "Darwin":
        os.system(f"say '{text}'")
    else:
        print(f"[Narration simulated] {text}")

def play_intro():
    """Main demo introduction narration"""
    log("🎙️ Starting AI Talent Engine demo narration...")
    say("Welcome to the AI Talent Engine — Signal Intelligence demonstration by Dave Mendoza.")
    say("This session will showcase research-first AI sourcing automation powered by thirty-two integrated agents.")
    say("Beginning demonstration sequence... Phase One: Citation Velocity Analysis.")
    log("✅ Intro narration completed.")

def phase_transition(phase_name):
    """Narrates transitions between demo phases"""
    if os.getenv("DEMO_MODE") != "true":
        return
    line = f"Transitioning to {phase_name}."
    log(f"🎬 {line}")
    say(line)

def closing_message():
    """Closing narration"""
    if os.getenv("DEMO_MODE") != "true":
        return
    say("This concludes the AI Talent Engine — Signal Intelligence demonstration. Thank you.")
    log("🏁 Closing narration completed.")

if __name__ == "__main__":
    play_intro()
