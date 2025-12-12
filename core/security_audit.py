#!/usr/bin/env python3
import os
print('🔐 Running security audit...')
for root,_,files in os.walk('.'):
    for f in files:
        if f.endswith('.py') and 'token' in open(os.path.join(root,f)).read():
            print('⚠️  Possible secret in',f)
print('✅ Security audit complete.')
