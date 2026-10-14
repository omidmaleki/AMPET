import os

for root, dirs, files in os.walk('.'):
    if any(x in root for x in ['__pycache__']):
        continue
    for f in files:
        print(os.path.join(root, f))
    for d in dirs:
        print(os.path.join(root, d) + '/')
