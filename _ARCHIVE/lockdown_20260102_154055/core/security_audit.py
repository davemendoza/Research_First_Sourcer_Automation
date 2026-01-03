#!/usr/bin/env python3
import os
print('🔐 Running security audit...')
issues=[]
for root,_,files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            text=open(os.path.join(root,f)).read()
            if 'token' in text.lower() or 'password' in text.lower():
                issues.append(f)
if issues: print('⚠️  Potential secrets found:',issues)
else: print('✅ No exposed secrets detected.')
