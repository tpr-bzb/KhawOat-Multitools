import os
import hashlib
import json

# รายชื่อไฟล์และโฟลเดอร์ที่ต้องการให้ระบบ Auto-Update นำไป Patch
INCLUDE_FILES = [
    "main.py",
    "ui_views.py",
    "services.py",
    "ui_config.py",
    "version.json"
]

INCLUDE_FOLDERS = [
    "assets"
]

def calculate_hash(filepath):
    """คำนวณ SHA256 ของไฟล์"""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error hashing {filepath}: {e}")
        return None

def generate_manifest():
    # 1. อ่านเวอร์ชันจาก version.json
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            v_data = json.load(f)
            version = v_data.get("version", "1.0")
    except:
        version = "1.0"

    manifest = {
        "version": version,
        "files": {}
    }
    
    # 2. เพิ่มไฟล์รายตัว
    for file in INCLUDE_FILES:
        if os.path.exists(file):
            file_hash = calculate_hash(file)
            if file_hash:
                manifest["files"][file] = {
                    "hash": file_hash,
                    "size": os.path.getsize(file)
                }
    
    # 3. เพิ่มไฟล์ในโฟลเดอร์ที่กำหนด
    for folder in INCLUDE_FOLDERS:
        if os.path.exists(folder):
            for root, dirs, files in os.walk(folder):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, ".").replace("\\", "/")
                    file_hash = calculate_hash(full_path)
                    if file_hash:
                        manifest["files"][rel_path] = {
                            "hash": file_hash,
                            "size": os.path.getsize(full_path)
                        }
            
    with open('manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Manifest generated successfully for version {version}")
    print(f"📦 Total files tracked: {len(manifest['files'])}")

if __name__ == "__main__":
    generate_manifest()

