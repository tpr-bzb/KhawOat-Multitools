import asyncio
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import app_release


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload


class FakePage:
    def __init__(self):
        self.update_calls = 0

    def update(self):
        self.update_calls += 1


class UpdaterE2ETests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.page = FakePage()
        self.splash_content = SimpleNamespace(content=SimpleNamespace(controls=[]))
        self.lbl_splash_status = SimpleNamespace(value="", color=None)
        self.progress_bar = SimpleNamespace(value=0, visible=True)
        self.release_metadata = app_release.ReleaseMetadata(
            version="17.0.0",
            change_log="",
            force_setup=True,
            update_url="https://example.com/releases",
        )

    async def test_no_update_skips_patch_lookup(self):
        response = FakeResponse({"version": "17.0.0", "force_setup": False})

        with mock.patch.object(app_release.requests, "get", return_value=response), \
             mock.patch.object(app_release, "check_for_patches", new=mock.AsyncMock()) as check_for_patches:
            await app_release.run_auto_update(
                page=self.page,
                splash_content=self.splash_content,
                lbl_splash_status=self.lbl_splash_status,
                progress_bar=self.progress_bar,
                current_version="17.0.0",
                release_metadata=self.release_metadata,
                accent_color="#ffaa00",
                primary_color="#00ff99",
            )

        check_for_patches.assert_not_awaited()
        self.assertEqual(self.splash_content.content.controls, [])

    async def test_asset_only_patch_updates_and_requests_restart(self):
        response = FakeResponse({"version": "17.0.1", "force_setup": False})
        patches = [
            {
                "rel_path": "assets/morning.gif",
                "url": "https://example.com/assets/morning.gif",
                "hash": "hash-1",
            }
        ]

        async def fake_sleep(_seconds):
            return None

        with mock.patch.object(app_release.requests, "get", return_value=response), \
             mock.patch.object(app_release, "check_for_patches", new=mock.AsyncMock(return_value=(patches, "17.0.1"))), \
             mock.patch.object(app_release, "apply_patch", new=mock.AsyncMock(return_value=True)) as apply_patch, \
             mock.patch.object(app_release.asyncio, "sleep", side_effect=fake_sleep), \
             mock.patch.object(app_release.os, "execl") as execl_mock, \
             mock.patch.object(app_release.sys, "frozen", True, create=True), \
             mock.patch.object(app_release.sys, "executable", str(PROJECT_ROOT / "dist" / "KhawOat_MultiTools_Pro.exe")):
            await app_release.run_auto_update(
                page=self.page,
                splash_content=self.splash_content,
                lbl_splash_status=self.lbl_splash_status,
                progress_bar=self.progress_bar,
                current_version="17.0.0",
                release_metadata=self.release_metadata,
                accent_color="#ffaa00",
                primary_color="#00ff99",
            )

        apply_patch.assert_awaited_once()
        execl_mock.assert_called_once()
        called_args = apply_patch.await_args.args
        self.assertEqual(called_args[0], "https://example.com/assets/morning.gif")
        self.assertTrue(str(called_args[1]).replace("\\", "/").endswith("assets/morning.gif"))
        self.assertEqual(apply_patch.await_args.kwargs["expected_hash"], "hash-1")
        self.assertEqual(self.lbl_splash_status.value, "Update Complete! Restarting...")

    async def test_unsafe_patch_requires_installer_prompt(self):
        response = FakeResponse({"version": "17.0.1", "force_setup": False, "update_url": "https://example.com/setup"})
        patches = [{"rel_path": "services.py", "url": "https://example.com/services.py", "hash": "unsafe"}]

        async def noop_wait():
            return None

        with mock.patch.object(app_release.requests, "get", return_value=response), \
             mock.patch.object(app_release, "check_for_patches", new=mock.AsyncMock(return_value=(patches, "17.0.1"))), \
             mock.patch.object(app_release, "apply_patch", new=mock.AsyncMock()) as apply_patch, \
             mock.patch.object(app_release, "wait_for_installer_download", side_effect=noop_wait), \
             mock.patch.object(app_release.sys, "frozen", True, create=True):
            await app_release.run_auto_update(
                page=self.page,
                splash_content=self.splash_content,
                lbl_splash_status=self.lbl_splash_status,
                progress_bar=self.progress_bar,
                current_version="17.0.0",
                release_metadata=self.release_metadata,
                accent_color="#ffaa00",
                primary_color="#00ff99",
            )

        apply_patch.assert_not_awaited()
        self.assertEqual(self.lbl_splash_status.value, "Critical Update Required!")
        self.assertFalse(self.progress_bar.visible)
        self.assertEqual(len(self.splash_content.content.controls), 1)
        self.assertEqual(self.splash_content.content.controls[0].text, "Download Installer")

    async def test_patch_failure_falls_back_to_offline_mode(self):
        response = FakeResponse({"version": "17.0.1", "force_setup": False})
        patches = [
            {
                "rel_path": "assets/night.gif",
                "url": "https://example.com/assets/night.gif",
                "hash": "hash-2",
            }
        ]

        async def fake_sleep(_seconds):
            return None

        with mock.patch.object(app_release.requests, "get", return_value=response), \
             mock.patch.object(app_release, "check_for_patches", new=mock.AsyncMock(return_value=(patches, "17.0.1"))), \
             mock.patch.object(app_release, "apply_patch", new=mock.AsyncMock(return_value=False)) as apply_patch, \
             mock.patch.object(app_release.asyncio, "sleep", side_effect=fake_sleep), \
             mock.patch.object(app_release.os, "execl") as execl_mock, \
             mock.patch.object(app_release.sys, "frozen", True, create=True), \
             mock.patch.object(app_release.sys, "executable", str(PROJECT_ROOT / "dist" / "KhawOat_MultiTools_Pro.exe")):
            await app_release.run_auto_update(
                page=self.page,
                splash_content=self.splash_content,
                lbl_splash_status=self.lbl_splash_status,
                progress_bar=self.progress_bar,
                current_version="17.0.0",
                release_metadata=self.release_metadata,
                accent_color="#ffaa00",
                primary_color="#00ff99",
            )

        apply_patch.assert_awaited_once()
        execl_mock.assert_not_called()
        self.assertIn("Offline Mode: Patch failed verification for assets/night.gif", self.lbl_splash_status.value)


if __name__ == "__main__":
    unittest.main()
