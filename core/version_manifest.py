#!/usr/bin/env python3
import json, datetime, subprocess, os
LOG_FILE='logs/version_manifest.json'
git_hash = subprocess.getoutput('git rev-parse HEAD') or 'unknown'
manifest={'build_version':'1.0.0',
          'schema':'AI_Talent_Schema_Rules v3.2',
          'timestamp':datetime.datetime.now().isoformat(),
          'commit':git_hash}
os.makedirs('logs',exist_ok=True)
json.dump(manifest,open(LOG_FILE,'w'),indent=2)
print('✅ Version manifest written →',LOG_FILE)
