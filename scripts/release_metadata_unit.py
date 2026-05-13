import json
import os
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app_release import get_runtime_base_dir, is_runtime_patch_safe, must_use_installer
import generate_manifest


VERSION_FILE = PROJECT_ROOT / "version.json"
MANIFEST_FILE = PROJECT_ROOT / "manifest.json"
README_FILE = PROJECT_ROOT / "README.md"
INSTALLER_FILE = PROJECT_ROOT / "setting.iss"


class ReleaseMetadataUnitTests(unittest.TestCase):
    def test_runtime_base_dir_uses_executable_location_when_frozen(self):
        with mock.patch.object(sys, "frozen", True, create=True), \
             mock.patch.object(sys, "executable", r"D:\Apps\Tool\KhawOat_MultiTools_Pro.exe"):
            self.assertEqual(get_runtime_base_dir(), r"D:\Apps\Tool")

    def test_runtime_patch_policy_for_frozen_builds(self):
        self.assertTrue(is_runtime_patch_safe("assets/morning.gif", frozen=True))
        self.assertTrue(is_runtime_patch_safe("version.json", frozen=True))
        self.assertFalse(is_runtime_patch_safe("services.py", frozen=True))
        self.assertFalse(is_runtime_patch_safe("requirements.txt", frozen=True))
        self.assertFalse(is_runtime_patch_safe("requirements.txt", frozen=False))
        self.assertTrue(is_runtime_patch_safe("services.py", frozen=False))

    def test_installer_is_required_for_force_setup_or_unsafe_frozen_patch(self):
        self.assertTrue(
            must_use_installer(
                remote_force_setup=True,
                patches=[{"rel_path": "assets/morning.gif"}],
                frozen=True,
            )
        )
        self.assertTrue(
            must_use_installer(
                remote_force_setup=False,
                patches=[{"rel_path": "services.py"}],
                frozen=True,
            )
        )
        self.assertFalse(
            must_use_installer(
                remote_force_setup=False,
                patches=[{"rel_path": "assets/morning.gif"}],
                frozen=True,
            )
        )

    def test_version_alignment_across_project_files(self):
        version_data = json.loads(VERSION_FILE.read_text(encoding="utf-8-sig"))
        manifest_data = json.loads(MANIFEST_FILE.read_text(encoding="utf-8-sig"))
        readme_text = README_FILE.read_text(encoding="utf-8")
        installer_text = INSTALLER_FILE.read_text(encoding="utf-8")

        version = version_data["version"]
        installer_version_match = re.search(r'#define MyAppVersion "([^"]+)"', installer_text)
        output_filename_match = re.search(r"OutputBaseFilename=KhawOat_MultiTools_v([0-9.]+)_Setup", installer_text)

        self.assertIsNotNone(installer_version_match)
        self.assertIsNotNone(output_filename_match)
        self.assertEqual(manifest_data["version"], version)
        self.assertEqual(installer_version_match.group(1), version)
        self.assertEqual(output_filename_match.group(1), version)
        self.assertIn(f"(v{version})", readme_text)
        self.assertIn(f"KhawOat_MultiTools_v{version}_Setup.exe", readme_text)

    def test_generate_manifest_uses_version_and_tracks_selected_files(self):
        original_cwd = os.getcwd()
        original_include_files = list(generate_manifest.INCLUDE_FILES)
        original_include_folders = list(generate_manifest.INCLUDE_FOLDERS)

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                root = Path(temp_dir)
                (root / "version.json").write_text(json.dumps({"version": "99.1"}), encoding="utf-8")
                (root / "alpha.txt").write_text("alpha", encoding="utf-8")
                assets_dir = root / "assets"
                assets_dir.mkdir()
                (assets_dir / "logo.txt").write_text("asset", encoding="utf-8")

                generate_manifest.INCLUDE_FILES = ["alpha.txt", "missing.txt", "version.json"]
                generate_manifest.INCLUDE_FOLDERS = ["assets"]

                os.chdir(root)
                generate_manifest.generate_manifest()

                manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["version"], "99.1")
                self.assertIn("alpha.txt", manifest["files"])
                self.assertIn("version.json", manifest["files"])
                self.assertIn("assets/logo.txt", manifest["files"])
                self.assertNotIn("missing.txt", manifest["files"])
                self.assertEqual(manifest["files"]["alpha.txt"]["size"], 5)
                os.chdir(original_cwd)
        finally:
            os.chdir(original_cwd)
            generate_manifest.INCLUDE_FILES = original_include_files
            generate_manifest.INCLUDE_FOLDERS = original_include_folders


if __name__ == "__main__":
    unittest.main()
