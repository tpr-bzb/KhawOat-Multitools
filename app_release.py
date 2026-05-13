import asyncio
import json
import os
import re
import sys
import time
import webbrowser
from dataclasses import dataclass

import flet as ft
import requests

from app_logging import get_logger
from services import apply_patch, check_for_patches


def get_runtime_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(__file__)


VERSION_FILE = os.path.join(get_runtime_base_dir(), "version.json")
VERSION_JSON_URL = "https://raw.githubusercontent.com/tpr-bzb/KhawOat-Multitools/main/version.json"
DEFAULT_UPDATE_URL = "https://github.com/tpr-bzb/KhawOat-Multitools/releases"
SAFE_PATCH_PATH_PREFIXES = ("assets/",)
SAFE_PATCH_EXACT_PATHS = {"version.json"}
ALWAYS_UNSAFE_PATCH_PATHS = {"requirements.txt"}


def parse_version(version_text: str) -> tuple[int, ...]:
    parts = re.findall(r"\d+", str(version_text or "0"))
    return tuple(int(part) for part in parts) or (0,)


@dataclass(frozen=True)
class ReleaseMetadata:
    version: str
    change_log: str
    force_setup: bool
    update_url: str


def is_runtime_patch_safe(rel_path: str, *, frozen: bool) -> bool:
    normalized = str(rel_path).replace("\\", "/")
    if normalized in ALWAYS_UNSAFE_PATCH_PATHS:
        return False
    if not frozen:
        return True
    return normalized in SAFE_PATCH_EXACT_PATHS or normalized.startswith(SAFE_PATCH_PATH_PREFIXES)


def must_use_installer(*, remote_force_setup: bool, patches: list[dict], frozen: bool) -> bool:
    if remote_force_setup:
        return True
    return any(not is_runtime_patch_safe(patch["rel_path"], frozen=frozen) for patch in patches)


def load_release_metadata(version_file: str = VERSION_FILE) -> ReleaseMetadata:
    try:
        with open(version_file, "r", encoding="utf-8") as version_handle:
            data = json.load(version_handle)
    except Exception:
        data = {}

    return ReleaseMetadata(
        version=str(data.get("version", "1.0")),
        change_log=str(data.get("change_log", "")),
        force_setup=bool(data.get("force_setup", False)),
        update_url=str(data.get("update_url", DEFAULT_UPDATE_URL)),
    )


RELEASE_METADATA = load_release_metadata()
UPDATE_LOGGER = get_logger("app.update", "update.log")


async def wait_for_installer_download() -> None:
    while True:
        await asyncio.sleep(1)


async def run_auto_update(
    page: ft.Page,
    splash_content: ft.Container,
    lbl_splash_status: ft.Text,
    progress_bar: ft.ProgressBar,
    current_version: str,
    release_metadata: ReleaseMetadata,
    accent_color: str,
    primary_color: str,
) -> None:
    try:
        UPDATE_LOGGER.info("auto_update_start current_version=%s", current_version)
        lbl_splash_status.value = "Checking for Professional Updates..."
        page.update()

        cache_bypass_url = f"{VERSION_JSON_URL}?t={int(time.time())}"
        response = requests.get(cache_bypass_url, timeout=10)
        if response.status_code != 200:
            UPDATE_LOGGER.warning("version_check_http_status status=%s", response.status_code)
            return

        data = response.json()
        remote_version = str(data.get("version", "0"))
        UPDATE_LOGGER.info(
            "version_check_result remote_version=%s remote_force_setup=%s",
            remote_version,
            bool(data.get("force_setup")),
        )
        if parse_version(remote_version) <= parse_version(current_version):
            UPDATE_LOGGER.info("auto_update_noop remote_version_not_newer")
            return

        manifest_url = VERSION_JSON_URL.replace("version.json", "manifest.json")
        cache_bypass_manifest = f"{manifest_url}?t={int(time.time())}"
        base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.getcwd()
        patches, _remote_ver = await check_for_patches(cache_bypass_manifest, base_dir)
        UPDATE_LOGGER.info(
            "patch_scan_complete base_dir=%s patch_count=%s frozen=%s",
            base_dir,
            len(patches),
            bool(getattr(sys, "frozen", False)),
        )

        if must_use_installer(
            remote_force_setup=bool(data.get("force_setup")),
            patches=patches,
            frozen=bool(getattr(sys, "frozen", False)),
        ):
            UPDATE_LOGGER.warning(
                "installer_required remote_force_setup=%s patch_paths=%s",
                bool(data.get("force_setup")),
                [patch["rel_path"] for patch in patches],
            )
            lbl_splash_status.value = "Critical Update Required!"
            lbl_splash_status.color = accent_color
            progress_bar.visible = False
            page.update()

            download_url = data.get("update_url", release_metadata.update_url)

            async def open_download(_event):
                webbrowser.open(download_url)

            button = ft.ElevatedButton(
                "Download Installer",
                icon=ft.icons.DOWNLOAD,
                on_click=open_download,
                bgcolor=primary_color,
                color="black",
                height=50,
            )
            splash_content.content.controls.append(button)
            page.update()
            await wait_for_installer_download()

        lbl_splash_status.value = "Pre-loading Professional Assets..."
        page.update()
        if not patches:
            UPDATE_LOGGER.info("auto_update_noop no_runtime_safe_patches")
            return

        total = len(patches)
        for index, patch in enumerate(patches, start=1):
            UPDATE_LOGGER.info(
                "patch_apply_start rel_path=%s index=%s total=%s expected_hash=%s",
                patch["rel_path"],
                index,
                total,
                patch.get("hash"),
            )
            lbl_splash_status.value = f"Patching: {patch['rel_path']} ({index}/{total})"
            progress_bar.value = index / total
            page.update()
            success = await apply_patch(
                patch["url"],
                os.path.join(base_dir, patch["rel_path"]),
                expected_hash=patch.get("hash"),
            )
            if not success:
                UPDATE_LOGGER.error("patch_apply_failed rel_path=%s", patch["rel_path"])
                raise RuntimeError(f"Patch failed verification for {patch['rel_path']}")
            UPDATE_LOGGER.info("patch_apply_success rel_path=%s", patch["rel_path"])

        lbl_splash_status.value = "Update Complete! Restarting..."
        page.update()
        UPDATE_LOGGER.info("auto_update_complete restart_requested patch_count=%s", total)
        await asyncio.sleep(1)
        if getattr(sys, "frozen", False):
            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            os.execl(sys.executable, sys.executable, __file__, *sys.argv)
    except Exception as exc:
        UPDATE_LOGGER.exception("auto_update_error error=%s", exc)
        lbl_splash_status.value = f"Offline Mode: {exc}"
        page.update()
        await asyncio.sleep(1)
