import os

def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        # ไม่แสดงโฟลเดอร์ venv หรือ __pycache__ ให้รกตา
        if '.venv' in root or '__pycache__' in root or '.git' in root:
            continue
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

list_files('.')