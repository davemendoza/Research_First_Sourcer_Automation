#!/usr/bin/env python3
import subprocess, shutil, sys, platform
checks={'python':sys.version,'git':shutil.which('git'),'streamlit':shutil.which('streamlit'),'ssh':shutil.which('ssh')}
print('✅ Environment Check Results:')
for k,v in checks.items(): print(f'  {k}:',v or 'Missing')
