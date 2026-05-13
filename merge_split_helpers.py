import asyncio
import os
import time

from tool_context import HandlerContext


async def normalize_split_lines_input(control, deps: HandlerContext) -> None:
    value = control.value.replace(",", "")
    if value.isdigit():
        control.value = f"{int(value):,}"
        await deps.safe_update(control)


def build_split_request(ui: dict, deps: HandlerContext) -> dict:
    src_dir = ui["txt_src_dir"].value
    src_ext_label = ui["dd_src_ext"].value
    out_ext_label = ui["dd_out_ext"].value
    src_ext_dot = deps.get_extension(src_ext_label)
    out_ext_dot = deps.get_extension(out_ext_label)
    base_name = ui["txt_base_name"].value.strip() or "output"
    size_str = ui["txt_lines"].value.replace(",", "")
    size = int(size_str) if size_str.isdigit() and int(size_str) > 0 else 1000

    return {
        "src_dir": src_dir,
        "out_dir": os.path.join(src_dir, "Split_Output"),
        "src_ext_label": src_ext_label,
        "out_ext_label": out_ext_label,
        "src_ext_dot": src_ext_dot,
        "out_ext_dot": out_ext_dot,
        "base_name": base_name,
        "size": size,
        "has_header": ui["chk_header"].value,
    }


def resolve_files_to_process(request: dict, deps: HandlerContext) -> list:
    return deps.list_files_to_process(
        request["src_dir"],
        request["src_ext_label"],
        request["src_ext_dot"],
    )


async def activate_split_loading(ui: dict, deps: HandlerContext) -> None:
    deps.btn_cancel_process.disabled = False
    ui["lbl_split_summary"].value = ""
    deps.page.dialog = deps.dlg_loading
    deps.dlg_loading.open = True
    await deps.set_busy(True)
    await deps.page.update_async()


async def deactivate_split_loading(deps: HandlerContext) -> None:
    deps.dlg_loading.open = False
    await deps.set_busy(False)
    await deps.page.update_async()


def build_split_status_callback(deps: HandlerContext):
    last_ui_update = time.time()

    async def status_callback(message, force=False):
        nonlocal last_ui_update
        deps.lbl_modal_status.value = message
        now = time.time()
        if force or (now - last_ui_update > 0.15):
            await deps.safe_update(deps.lbl_modal_status)
            last_ui_update = now
            await asyncio.sleep(0.001)

    return status_callback


def apply_split_success_state(ui: dict, result: dict, files_to_process: list, elapsed: float, was_cancelled: bool, deps: HandlerContext) -> None:
    if was_cancelled:
        ui["lbl_split_status"].value = "⚠️ ผู้ใช้ยกเลิก"
        ui["lbl_split_status"].color = "orange"
        ui["lbl_split_summary"].value = f"🛑 หยุดที่: {result['files_created']} ไฟล์ | เวลา: {elapsed:.2f}s"
        return

    ui["lbl_split_status"].value = "✅ สำเร็จ!" if not result["errors"] else "✅ สำเร็จ (พบปัญหาบางจุด)"
    ui["lbl_split_status"].color = deps.color_secondary
    ui["lbl_split_summary"].value = (
        f"📊 นำเข้า {len(files_to_process)} ไฟล์ | {result['total_rows']:,} แถว | "
        f"แบ่งได้ {result['files_created']} ไฟล์ | {elapsed:.2f}s"
    )
