#!/bin/zsh
# ======================================================
#  AI Talent Engine — Demo Runner v4.1 (Schema-Locked Final Edition)
#  © 2025 L. David Mendoza · All Rights Reserved
#  Legal Notice: Confidential & Proprietary — See Legal_Proprietary_Notice.txt
# ======================================================
#  STATUS: Governance-Locked | Schema Reference: AI_Talent_Schema_Rules v3.2
#  Purpose: One-command orchestrator for autogeneration, validation, and push.
# ======================================================

set -e
set -u
set +o nomatch

cd ~/Desktop/Research_First_Sourcer_Automation/demo || {
  echo "❌ Demo directory not found."; exit 1;
}

timestamp=$(date "+%Y-%m-%d %H:%M:%S")
run_id=$(date "+%Y%m%d_%H%M")
log_prefix="logs/run_audit_${run_id}"

echo "🚀 Starting AI Talent Engine Demo (v4.1 — Schema-Locked)"
os_version=$(sw_vers -productVersion 2>/dev/null || uname -r)
user_name=$(whoami)
host_name=$(hostname)
git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "main")
git_hash=$(git rev-parse --short HEAD 2>/dev/null || echo "local")

mkdir -p data charts logs demo_assets

# ------------------------------------------------------
# 1️⃣  Phase 6 & 7 Verification
# ------------------------------------------------------
if [[ ! -f data/phase6_output.csv || ! -f data/phase7_output.csv ]]; then
  echo "⚙️  Missing CSVs — running autogeneration…"
  /usr/local/bin/python3 autogenerate_phase_data.py | tee "logs/autogen_${run_id}.log"
else
  echo "✅  Phase 6 & 7 CSVs found — skipping autogeneration."
fi

# ------------------------------------------------------
# 2️⃣  Master Generation
# ------------------------------------------------------
echo "🧠 Running master generator…"
/usr/local/bin/python3 generate_ai_talent_master_v34.py | tee "logs/master_${run_id}.log"

# ------------------------------------------------------
# 3️⃣  SHA256 + Size Audit
# ------------------------------------------------------
echo "🔒 Auditing CSV integrity…"
for f in data/*.csv; do
  [[ -f "$f" ]] || continue
  sha=$(shasum -a 256 "$f" | awk '{print $1}')
  size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f")
  echo "$(date '+%Y-%m-%d %H:%M:%S') | $(basename "$f") | ${size} bytes | SHA256:${sha}" >> "logs/hash_${run_id}.log"
done

# ------------------------------------------------------
# 4️⃣  Schema + Numeric Validation (Python block)
# ------------------------------------------------------
echo "🧩 Validating schema & numeric fields…"
/usr/local/bin/python3 - <<'PYCODE'
import pandas as pd, glob, sys, datetime
print(f"Validation — {datetime.datetime.now()}")
expected_cols = 40
errors=[]
for path in glob.glob("data/*_demo.csv"):
    df=pd.read_csv(path)
    if df.shape[1]!=expected_cols:
        errors.append(f"{path} columns={df.shape[1]} expected={expected_cols}")
    if "Citation_Trajectory" in df.columns:
        bad=df["Citation_Trajectory"].apply(lambda x: not str(x).replace('.','',1).isdigit()).sum()
        oor=df[df["Citation_Trajectory"].between(0,10)==False].shape[0]
        if bad or oor:
            errors.append(f"{path} invalid Citation_Trajectory: bad={bad}, oor={oor}")
if errors:
    print("❌ Validation errors:"); [print(" -",e) for e in errors]; sys.exit(1)
print("✅ All CSVs schema-locked & numerically valid.")
PYCODE

# ------------------------------------------------------
# 5️⃣  Governance Summary
# ------------------------------------------------------
summary="demo_assets/summary_report_${run_id}.txt"
{
  echo "AI Talent Engine Demo Summary — $timestamp"
  echo "Run ID: $run_id"
  echo "User: $user_name@$host_name"
  echo "OS: $os_version"
  echo "Git: $git_branch@$git_hash"
  echo "Schema Compliance: PASSED"
  echo "Numeric Range: [0–10]"
  echo "Audit Logs: logs/*${run_id}*"
  echo "Charts: charts/"
  echo "Data: data/"
} > "$summary"
echo "🧾 Summary saved → $summary"

# ------------------------------------------------------
# 6️⃣  Git Commit + Push
# ------------------------------------------------------
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "📤 Committing & pushing results to GitHub…"
  git add data charts logs demo_assets
  git commit -m "AI Talent Engine Demo ${run_id}" || true
  git push origin "$git_branch"
fi

# ------------------------------------------------------
# 7️⃣  Optional Remote Sync (commented)
# ------------------------------------------------------
# REMOTE_DIR="user@server:/path/to/archive/"
# echo "☁️  Syncing to \$REMOTE_DIR…"
# rsync -avz demo_assets/ "\$REMOTE_DIR"

# ------------------------------------------------------
# 8️⃣  Optional Slack/Webhook Notify (commented)
# ------------------------------------------------------
# if command -v curl >/dev/null; then
#   curl -X POST -H 'Content-type: application/json' \
#     --data "{\"text\":\"AI Talent Engine Demo ${run_id} completed successfully on ${host_name}.\"}" \
#     https://hooks.slack.com/services/XXX/YYY/ZZZ >/dev/null 2>&1 || true
# fi

# ------------------------------------------------------
# 9️⃣  Final Output
# ------------------------------------------------------
echo "\n✅ DEMO OUTPUT SUMMARY"
ls -lh data/*_demo.csv | tee -a "${log_prefix}.log" || true
ls -lh charts | tee -a "${log_prefix}.log" || true
ls -lh demo_assets | tee -a "${log_prefix}.log" || true
echo "✅  AI Talent Engine Demo completed successfully."
