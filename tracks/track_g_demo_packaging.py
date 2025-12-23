#!/usr/bin/env python3
"""
Track G — Demo Packaging (Audit-Safe)
v2.0 | Dec 22, 2025
© 2025 L. David Mendoza. All Rights Reserved.
"""

import os, shutil, hashlib
from datetime import datetime, timezone

SRC="outputs/track_f"
DST="outputs/demo"

os.makedirs(DST, exist_ok=True)
manifest=[]

for f in os.listdir(SRC):
    if f.endswith(".csv"):
        src=os.path.join(SRC,f)
        dst=os.path.join(DST,f)
        shutil.copy2(src,dst)
        h=hashlib.sha256(open(dst,"rb").read()).hexdigest()
        manifest.append((f,h))

with open(os.path.join(DST,"MANIFEST.txt"),"w") as m:
    m.write(f"Demo Freeze UTC: {datetime.now(timezone.utc).isoformat()}\n\n")
    for f,h in manifest:
        m.write(f"{f}  SHA256:{h}\n")

os.chmod(DST,0o555)
print("✅ Track G v2 complete — demo locked")
