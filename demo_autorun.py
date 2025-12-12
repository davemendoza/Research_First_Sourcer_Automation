#!/usr/bin/env python3
from demos.narration.voice_narrator import speak
# ===========================================================
#  AI Talent Engine – Signal Intelligence
#  Demo Autorun + Narration Framework
#  © 2025 L. David Mendoza
# ===========================================================

import os, subprocess, time, yaml, importlib.util
from datetime import datetime

CONFIG_PATH = "demos/config/demo_map.yaml"
AGENT_DIR   = "demos/agents"
LOG_DIR     = "logs"
NARRATION   = True

def log(msg):
    print(msg)
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(f"{LOG_DIR}/demo_run_{datetime.now():%Y%m%d}.log","a") as f:
        f.write(f"[{datetime.now():%H:%M:%S}] {msg}\n")

def narrate(text):
    if not NARRATION: return
    try: subprocess.run(["say", text])
    except Exception: log("Narration unavailable; skipped.")

def load_yaml(path):
    with open(path,"r") as f: return yaml.safe_load(f)

def run_demo(agent_name, description):
    narrate(f"Launching demo {agent_name}")
    log(f"🎬 Starting demo: {agent_name} — {description}")
    agent_path = os.path.join(AGENT_DIR, f"{agent_name}.py")
    if not os.path.exists(agent_path):
        log(f"⚠️ Missing agent file: {agent_path}")
        return
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    mod  = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        if hasattr(mod,"run_demo"):
            mod.run_demo()
            log(f"✅ Demo {agent_name} finished successfully.
        if os.getenv("DEMO_MODE") == "true":
            phase_transition("next demo phase")")
        else:
            log(f"⚠️ No run_demo() found in {agent_name}.")
    except Exception as e:
        log(f"❌ Error running {agent_name}: {e}")

def audio_precheck():
    if os.getenv("DEMO_MODE"):
        subprocess.run(["python3", "core/voice_monitor.py"], check=False)

def narrate_intro():
    if os.getenv("DEMO_MODE") == "true":
        play_intro()

def main():
    log("──────────────────────────────────────")
    log(f"🚀 Demo Autorun Started {datetime.now()}")
    if not os.path.exists(CONFIG_PATH):
        log("❌ No demo_map.yaml found; aborting."); return
    demos = load_yaml(CONFIG_PATH)
    for demo in demos.get("demos", []):
        run_demo(demo["agent"], demo.get("description",""))
        time.sleep(demo.get("delay",2))
    narrate("All demos completed successfully.")
    log("🏁 All demos completed.
    if os.getenv("DEMO_MODE") == "true":
        closing_message()")
    log("──────────────────────────────────────")

if __name__ == "__main__":
    main()
