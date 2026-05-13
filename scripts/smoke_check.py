import importlib
import json
from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE = PROJECT_ROOT / "version.json"
MANIFEST_FILE = PROJECT_ROOT / "manifest.json"
sys.path.insert(0, str(PROJECT_ROOT))

REQUIRED_MODULES = [
    "main",
    "app_release",
    "app_logging",
    "app_runtime",
    "handlers_basic",
    "handlers_tools",
    "merge_split_helpers",
    "json_tool_helpers",
    "json_view_helpers",
    "services",
    "ui_views",
    "ui_config",
]

REQUIRED_VERSION_KEYS = {
    "version",
    "force_setup",
    "update_url",
    "change_log",
}

REQUIRED_MANIFEST_FILES = {
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
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as file_obj:
        return json.load(file_obj)


def validate_version_json() -> None:
    data = load_json(VERSION_FILE)
    missing = REQUIRED_VERSION_KEYS.difference(data.keys())
    if missing:
        raise RuntimeError(f"version.json is missing keys: {sorted(missing)}")


def validate_manifest_json() -> None:
    data = load_json(MANIFEST_FILE)
    files = data.get("files")
    if not isinstance(files, dict):
        raise RuntimeError("manifest.json must contain a 'files' object")

    missing_files = REQUIRED_MANIFEST_FILES.difference(files.keys())
    if missing_files:
        raise RuntimeError(f"manifest.json is missing tracked files: {sorted(missing_files)}")


def validate_imports() -> None:
    for module_name in REQUIRED_MODULES:
        importlib.import_module(module_name)


def main() -> None:
    validate_version_json()
    validate_manifest_json()
    validate_imports()
    print("smoke_check_ok")


if __name__ == "__main__":
    main()
