import datetime, os
LOG_FILE="logs/demo_activity.log"
def log_run(agent,status="✅ Success",duration=None):
    os.makedirs("logs",exist_ok=True)
    t=datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    d=f" | Duration: {duration}" if duration else ""
    msg=f"{t} Agent: {agent} | Status: {status}{d}"
    print(msg)
    with open(LOG_FILE,"a") as f: f.write(msg+"\n")
# © 2025 L. David Mendoza – All Rights Reserved
