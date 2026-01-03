#!/usr/bin/env python3
import time, os
print('♻️  Auto-refresh active (10s interval)')
while True:
    time.sleep(10)
    os.system('touch core/dashboard_connector.py')
