import hashlib
import json
import os


INCLUDE_FILES = [
    "main.py",
    "app_release.py",
    "app_logging.py",
    "app_runtime.py",
    "handlers_basic.py",
    "handlers_tools.py",
    "merge_split_helpers.py",
    "json_tool_helpers.py",
    "json_view_helpers.py",
    "ui_views.py",
    "services.py",
    "ui_config.py",
    "requirements.txt",
    "version.json",
]

INCLUDE_FOLDERS = [
    "assets",
]


def calculate_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as exc:
        print(f"Error hashing {filepath}: {exc}")
        return None


def generate_manifest():
    try:
        with open("version.json", "r", encoding="utf-8") as version_file:
            version_data = json.load(version_file)
            version = version_data.get("version", "1.0")
    except Exception:
        version = "1.0"

    manifest = {
        "version": version,
        "files": {},
    }

    for file_path in INCLUDE_FILES:
        if not os.path.exists(file_path):
            continue
        file_hash = calculate_hash(file_path)
        if not file_hash:
            continue
        manifest["files"][file_path] = {
            "hash": file_hash,
            "size": os.path.getsize(file_path),
        }

    for folder in INCLUDE_FOLDERS:
        if not os.path.exists(folder):
            continue
        for root, _dirs, files in os.walk(folder):
            for file_name in files:
                full_path = os.path.join(root, file_name)
                rel_path = os.path.relpath(full_path, ".").replace("\\", "/")
                file_hash = calculate_hash(full_path)
                if not file_hash:
                    continue
                manifest["files"][rel_path] = {
                    "hash": file_hash,
                    "size": os.path.getsize(full_path),
                }

    with open("manifest.json", "w", encoding="utf-8") as manifest_file:
        json.dump(manifest, manifest_file, indent=4, ensure_ascii=False)

    print(f"Manifest generated successfully for version {version}")
    print(f"Total files tracked: {len(manifest['files'])}")


if __name__ == "__main__":
    generate_manifest()
