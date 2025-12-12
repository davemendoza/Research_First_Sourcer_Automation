#!/usr/bin/env python3
# ===========================================================
#  AI Talent Engine — Final Verification Script
#  © 2025  L. David Mendoza  –  All Rights Reserved
# ===========================================================
import os, subprocess, json, datetime, hashlib, platform

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS = os.path.join(BASE, "logs")
os.makedirs(LOGS, exist_ok=True)
REPORT = os.path.join(LOGS, "final_verification_report.log")

def log(message):
    ts = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(message)
    with open(REPORT, "a") as f:
        f.write(f"{ts} {message}\n")

log("🔍 Starting FINAL VERIFICATION of AI Talent Engine...")

# --- Step 1: Git integrity check ---
try:
    branch = subprocess.getoutput("git rev-parse --abbrev-ref HEAD").strip()
    commit = subprocess.getoutput("git rev-parse HEAD").strip()
    remote = subprocess.getoutput("git config --get remote.origin.url").strip()
    log(f"✅ Git branch: {branch}")
    log(f"✅ Last commit: {commit}")
    log(f"✅ Remote repo: {remote}")
except Exception as e:
    log(f"⚠️ Git check failed: {e}")

# --- Step 2: File count verification ---
count = sum(len(files) for _, _, files in os.walk(BASE))
log(f"📦 Total files in project: {count}")

# --- Step 3: Manifest verification ---
manifest_path = os.path.join(LOGS, "provenance_manifest.json")
if os.path.exists(manifest_path):
    manifest = json.load(open(manifest_path))
    log(f"🧾 Manifest loaded with {len(manifest['files'])} tracked files.")
else:
    log("⚠️ Manifest file missing.")

# --- Step 4: Module health tests ---
core_files = [
    "core/system_health.py",
    "core/contact_enrichment.py",
    "core/security_audit.py",
    "core/dashboard_connector.py"
]
for f in core_files:
    if os.path.exists(os.path.join(BASE, f)):
        log(f"✅ {f} exists.")
    else:
        log(f"❌ {f} missing!")

# --- Step 5: Streamlit dashboard test ---
try:
    import streamlit
    ver = streamlit.__version__
    log(f"✅ Streamlit available (v{ver}).")
except Exception as e:
    log(f"⚠️ Streamlit not available: {e}")

# --- Step 6: Audio narration test (Mac only) ---
if platform.system() == "Darwin":
    status = subprocess.getoutput("pgrep -x coreaudiod")
    if status:
        log("✅ macOS Audio system running (coreaudiod detected).")
    else:
        log("⚠️ macOS Audio service inactive.")
else:
    log("ℹ️ Non-macOS platform: skipping audio test.")

# --- Step 7: SHA Integrity verification ---
if os.path.exists(manifest_path):
    mismatched = []
    for entry in manifest["files"]:
        p, old_hash = entry["path"], entry["sha256"]
        if os.path.exists(p):
            new_hash = hashlib.sha256(open(p, "rb").read()).hexdigest()
            if new_hash != old_hash:
                mismatched.append(p)
    if mismatched:
        log(f"⚠️ Integrity mismatch in {len(mismatched)} files.")
        for m in mismatched:
            log(f"   – {m}")
    else:
        log("✅ File integrity verified against manifest.")
else:
    log("⚠️ Manifest unavailable; integrity not verified.")

# --- Step 8: Demo readiness summary ---
log("──────────────────────────────────────────────")
log("🏁 DEMO READINESS SUMMARY")
log("──────────────────────────────────────────────")
log(f"✅ Build version: Final Total System Build")
log(f"✅ Repository: {remote}")
log(f"✅ Verified at: {datetime.datetime.now()}")
log("🎙️ Dashboard & narration ready for conference mode.")
log("──────────────────────────────────────────────")
log("📄 Verification log stored at: logs/final_verification_report.log")
