#!/usr/bin/env python3
import subprocess, json, datetime, platform, shutil
LOG='logs/system_health.log'
def check(cmd):
    try: subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True); return True
    except Exception: return False
report={'timestamp':datetime.datetime.now().isoformat(),
        'python': platform.python_version(),
        'git': shutil.which('git') is not None,
        'streamlit': check(['python3','-m','streamlit','--version']),
        'ssh': check(['ssh','-T','git@github.com']),
        'audio': check(['pgrep','-x','coreaudiod'])}
json.dump(report, open(LOG,'w'), indent=2)
print('✅ System health report written →', LOG)
