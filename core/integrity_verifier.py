#!/usr/bin/env python3
import os, hashlib, json, datetime
LOG='logs/provenance_manifest.json'
def hash_file(p):
    h=hashlib.sha256()
    with open(p,'rb') as f:
        for c in iter(lambda: f.read(8192),b''): h.update(c)
    return h.hexdigest()
manifest={'timestamp':datetime.datetime.now().isoformat(),'files':{}}
for root,_,files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            full=os.path.join(root,f)
            manifest['files'][full]=hash_file(full)
json.dump(manifest,open(LOG,'w'),indent=2)
print('✅ Integrity verification complete →',LOG)
