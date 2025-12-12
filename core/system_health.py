#!/usr/bin/env python3
import os, subprocess, platform, datetime, json
LOG_FILE = 'logs/system_health.log'
def check(cmd):
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except Exception:
        return False
report = {'timestamp': datetime.datetime.now().isoformat(),
          'python': platform.python_version(),
          'streamlit': check(['python3','-m','streamlit','--version']),
          'ssh': check(['ssh','-T','git@github.com']),
          'audio': check(['pgrep','-x','coreaudiod'])}
with open(LOG_FILE,'w') as f: json.dump(report,f,indent=2)
print('✅ System health diagnostics complete →',LOG_FILE)
