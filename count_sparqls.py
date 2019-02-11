import json
from pathlib import Path
import os
data_dir = Path('./sparqls')  
template_files = [x for x in os.listdir(data_dir) if x.startswith('template')]

count = 0
for fname in template_files:
    with open(data_dir / fname) as fobj:
        count += len([json.loads(x) for x in fobj.readlines()])
print(count)


