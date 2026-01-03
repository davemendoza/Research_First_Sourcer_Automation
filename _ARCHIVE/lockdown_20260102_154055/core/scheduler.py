#!/usr/bin/env python3
import time, subprocess
print('⏰ Scheduler active (simulated)... press Ctrl+C to stop.')
while True:
    subprocess.run(['python3','core/integrity_verifier.py'],check=False)
    time.sleep(3600)
