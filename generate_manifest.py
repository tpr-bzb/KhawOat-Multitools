import os
import hashlib
import json

def calculate_hash(filepath):
    """คำนวณ SHA256 ของไฟล์"""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def generate_manifest(dist_dir, version):
    """สร้าง manifest.json จากไฟล์ในโฟลเดอร์ dist"""
    manifest = {
        "version": version,
        "files": {}
    }
    
    for root, dirs, files in os.walk(dist_dir):
        for file in files:
            # ไม่เก็บไฟล์ .exe ตัวหลัก เพราะเราจะ patch ไฟล์ย่อยรอบๆ
            if file.endswith('.exe'): continue 
            
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, dist_dir)
            file_hash = calculate_hash(full_path)
            
            manifest["files"][rel_path.replace("\\", "/")] = {
                "hash": file_hash,
                "size": os.path.getsize(full_path)
            }
            
    with open('manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Manifest generated for version {version}")

if __name__ == "__main__":
    # ตัวอย่างการใช้งาน (ปรับ path ตามจริงเวลา build)
    generate_manifest("dist/KhawOat_MultiTools", "16.6")

