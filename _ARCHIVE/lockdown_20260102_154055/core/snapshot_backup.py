#!/usr/bin/env python3
import shutil, datetime
d=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
shutil.make_archive(f'archive/system_snapshot_{d}','zip','.')
print('📦 Snapshot archived.')
