import asyncio
import base64
import os
import time

import flet as ft
from app_logging import get_logger
from formatter_templates import SMART_FORMATTER_TEMPLATES
from merge_split_helpers import (
    activate_split_loading,
    apply_split_success_state,
    build_split_request,
    build_split_status_callback,
    deactivate_split_loading,
    normalize_split_lines_input,
    resolve_files_to_process,
)
from tool_context import HandlerContext

PROCESS_LOGGER = get_logger("app.process", "process.log")


def register_image_optimizer_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def btn_open_img(_event):
        if await deps.guard_busy():
            return
        deps.current_fp_context[deps.fp_open] = {"ui": ui["txt_img_src"], "type": "open"}
        await deps.fp_open.pick_files_async(allowed_extensions=["jpg", "jpeg", "png", "webp"])

    async def run_optimize_img(_event):
        if await deps.guard_busy():
            return
        if not ui["txt_img_src"].value:
            return

        src_path = ui["txt_img_src"].value
        dir_name = os.path.dirname(src_path)
        base_name = os.path.splitext(os.path.basename(src_path))[0]

        fmt = ui["dd_img_format"].value
        ext = ".jpg" if fmt == "JPEG" else ".png" if fmt == "PNG" else ".webp" if fmt == "WEBP" else os.path.splitext(src_path)[1]
        target_fmt = None if fmt == "Original" else fmt
        out_path = os.path.join(dir_name, f"{base_name}_optimized{ext}")

        await deps.set_busy(True)
        ui["lbl_img_status"].value = "⏳ กำลังประมวลผล..."
        await deps.safe_update(ui["lbl_img_status"])

        success, result = await asyncio.to_thread(
            deps.optimize_image,
            src_path,
            out_path,
            int(ui["slider_img_quality"].value),
            target_fmt,
        )

        if success:
            old_size = os.path.getsize(src_path) / 1024
            new_size = result / 1024
            reduction = (1 - (new_size / old_size)) * 100 if old_size else 0
            ui["lbl_img_status"].value = f"✅ สำเร็จ! {old_size:.1f}KB -> {new_size:.1f}KB (ลดลง {reduction:.1f}%)"
            ui["lbl_img_status"].color = deps.color_secondary
            await deps.show_toast("🖼️ บันทึกรูปภาพเรียบร้อย")
        else:
            ui["lbl_img_status"].value = f"❌ Error: {result}"
            ui["lbl_img_status"].color = "red"

        await deps.set_busy(False)
        await deps.safe_update(ui["lbl_img_status"])

    actions["btn_open_img"] = btn_open_img
    actions["run_optimize_img"] = run_optimize_img


def register_password_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def sl_ch(e):
        ui["lbl_pass_len"].value = f"ความยาวรหัสผ่าน: {int(e.control.value)}"
        await deps.safe_update(ui["lbl_pass_len"])

    async def gen(_event):
        pwd = deps.build_password(
            int(ui["slider_len"].value),
            ui["chk_upper"].value,
            ui["chk_lower"].value,
            ui["chk_nums"].value,
            ui["chk_syms"].value,
        )
        ui["txt_pass_out"].value = pwd if pwd else "❌ เลือกรูปแบบด้วยครับ"
        await deps.show_toast("สำเร็จ" if pwd else "พลาด", bool(pwd))
        await deps.safe_update(ui["txt_pass_out"])

    async def cp_p(_event):
        if ui["txt_pass_out"].value:
            deps.page.set_clipboard(ui["txt_pass_out"].value)
            await deps.show_toast("คัดลอกแล้ว")

    ui["slider_len"].on_change = sl_ch
    actions["run_gen_pass"] = gen
    actions["btn_copy_pass"] = cp_p


def register_binary_tool_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def calc_from_dec(_event):
        val = ui["txt_dec"].value.replace(",", "")
        if val.isdigit():
            num = int(val)
            ui["lbl_bin"].value = f"Binary: {bin(num)[2:]}"
            ui["col_breakdown"].controls.clear()
            for i, bit in enumerate(reversed(bin(num)[2:])):
                if bit == "1":
                    ui["col_breakdown"].controls.append(
                        deps.ft.Text(f"Bit {i}   >   {2**i}", color=deps.color_text, weight="bold")
                    )
            ui["lbl_sum"].value = f"ผลรวม: {num:,}"
            ui["box_breakdown"].visible = True
        else:
            ui["lbl_bin"].value = "Binary: -"
            ui["lbl_sum"].value = "ผลรวม: 0"
            ui["box_breakdown"].visible = False
        await deps.safe_update(ui["lbl_bin"])
        await deps.safe_update(ui["lbl_sum"])
        await deps.safe_update(ui["box_breakdown"])

    ui["txt_dec"].on_change = calc_from_dec


def register_qr_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def run_gen_qr(_event):
        if await deps.guard_busy():
            return
        if not ui["txt_qr"].value:
            await deps.show_toast("กรุณากรอกข้อความก่อน", False)
            return
        try:
            b64_qr = deps.generate_qr_base64(ui["txt_qr"].value)
            if b64_qr:
                ui["img_qr"].src_base64 = b64_qr
                ui["img_qr"].visible = True
                ui["qr_container"].visible = True
                ui["lbl_qr_status"].value = "สำเร็จ"
                ui["lbl_qr_status"].color = deps.color_secondary
                await deps.safe_update(ui["qr_container"])
                await deps.show_toast("สร้าง QR สำเร็จ")
        except Exception as ex:
            ui["lbl_qr_status"].value = f"Error: {ex}"
            ui["lbl_qr_status"].color = "red"
        await deps.safe_update(ui["img_qr"])
        await deps.safe_update(ui["lbl_qr_status"])

    async def do_save_qr(path):
        if path:
            with open(path, "wb") as file_obj:
                file_obj.write(base64.b64decode(ui["img_qr"].src_base64))
            await deps.show_toast("บันทึกรูปสำเร็จ")

    async def btn_save_qr(_event):
        if await deps.guard_busy():
            return
        if not ui["img_qr"].src_base64:
            await deps.show_toast("สร้าง QR ก่อน", False)
            return
        deps.current_fp_context[deps.fp_save] = {"type": "save", "callback": do_save_qr}
        await deps.fp_save.save_file_async(file_name="qrcode.png", file_type=ft.FilePickerFileType.IMAGE, allowed_extensions=["png"])

    actions["run_gen_qr"] = run_gen_qr
    actions["btn_save_qr"] = btn_save_qr


def register_bit_finder_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def run_find_bits(_event):
        if not ui["txt_bin_in"].value:
            return
        val = ui["txt_bin_in"].value.strip().replace(" ", "").replace("\n", "").replace("\r", "")
        indices = deps.find_binary_indices(val)

        if indices:
            idx_str = ", ".join(map(str, indices))
            ui["txt_bin_out"].value = idx_str
            ui["txt_sql_out"].value = f"select AppName,VisibilityPosition from SponsorApps where VisibilityPosition in ({idx_str})"
        else:
            ui["txt_bin_out"].value = "ไม่พบเลข 1"
            ui["txt_sql_out"].value = ""

        ui["lbl_bin_count"].value = f"พบเลข 1 จำนวน: {len(indices)} จุด"
        await deps.safe_update(ui["txt_bin_out"])
        await deps.safe_update(ui["txt_sql_out"])
        await deps.safe_update(ui["lbl_bin_count"])

    async def clr_bin(_event):
        ui["txt_bin_in"].value = ""
        ui["txt_bin_out"].value = ""
        ui["txt_sql_out"].value = ""
        ui["lbl_bin_count"].value = "พบเลข 1 จำนวน: 0 จุด"
        await deps.safe_update(ui["txt_bin_in"])
        await deps.safe_update(ui["txt_bin_out"])
        await deps.safe_update(ui["txt_sql_out"])
        await deps.safe_update(ui["lbl_bin_count"])

    async def cp_bin(_event):
        if ui["txt_bin_out"].value and ui["txt_bin_out"].value != "ไม่พบเลข 1":
            deps.page.set_clipboard(ui["txt_bin_out"].value)
            await deps.show_toast("คัดลอกตำแหน่งแล้ว")

    async def cp_sql(_event):
        if ui["txt_sql_out"].value:
            deps.page.set_clipboard(ui["txt_sql_out"].value)
            await deps.show_toast("คัดลอก SQL แล้ว")

    actions["run_find_bits"] = run_find_bits
    actions["run_clear_bits"] = clr_bin
    actions["btn_copy_bits"] = cp_bin
    actions["btn_copy_sql"] = cp_sql


def register_hidden_char_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    anomalies = {
        "\u200B": "Zero-Width Space",
        "\u200C": "Zero-Width Non-Joiner",
        "\u200D": "Zero-Width Joiner",
        "\uFEFF": "BOM",
        "\u00A0": "Non-Breaking Space",
        "\u0000": "Null",
        "\u0007": "Bell",
        "\u0008": "Backspace",
        "\u000B": "Vertical Tab",
        "\u000C": "Form Feed",
        "\u001F": "Unit Separator",
    }
    file_placeholder = "โหมดไฟล์: ยังไม่ได้เลือกไฟล์"
    clean_buffer = [None]

    async def op_h(_event):
        deps.current_fp_context[deps.fp_open] = {"ui": ui["lbl_hidden_file"], "type": "open"}
        await deps.fp_open.pick_files_async(allowed_extensions=["xlsx", "xls", "csv", "txt"])
        ui["txt_hidden_in"].value = ""
        ui["txt_hidden_in"].disabled = True
        PROCESS_LOGGER.info("hidden_char_file_picker_opened")
        await deps.safe_update(ui["txt_hidden_in"])

    async def cl_h(_event):
        ui["lbl_hidden_file"].value = file_placeholder
        ui["lbl_hidden_file"].color = "white54"
        ui["txt_hidden_in"].disabled = False
        ui["txt_hidden_out"].value = ""
        PROCESS_LOGGER.info("hidden_char_file_mode_cleared")
        await deps.safe_update(ui["lbl_hidden_file"])
        await deps.safe_update(ui["txt_hidden_in"])
        await deps.safe_update(ui["txt_hidden_out"])

    async def run_chk(_event):
        if await deps.guard_busy():
            return
        selected_path = ui["lbl_hidden_file"].value
        if selected_path != file_placeholder and os.path.exists(selected_path):
            PROCESS_LOGGER.info("hidden_char_check_start mode=file path=%s", selected_path)
            cleaned_data, status_msg = deps.process_hidden_char_file(selected_path, anomalies)
            clean_buffer[0] = cleaned_data
            ui["txt_hidden_out"].value = status_msg
            PROCESS_LOGGER.info(
                "hidden_char_check_complete mode=file has_clean_buffer=%s",
                clean_buffer[0] is not None,
            )
        else:
            text = ui["txt_hidden_in"].value
            PROCESS_LOGGER.info("hidden_char_check_start mode=text length=%s", len(text))
            count = 0
            report = []
            for char, description in anomalies.items():
                if char in text:
                    found = text.count(char)
                    report.append(f"พบ {description}: {found}")
                    count += found
            if count > 0:
                ui["txt_hidden_out"].value = f"พบ {count} แห่ง:\n" + "\n".join(report)
            else:
                ui["txt_hidden_out"].value = "ไม่พบอักขระแฝง"
            PROCESS_LOGGER.info("hidden_char_check_complete mode=text anomaly_count=%s", count)
        await deps.safe_update(ui["txt_hidden_out"])

    async def run_vis(_event):
        if not ui["txt_hidden_in"].value:
            return
        PROCESS_LOGGER.info("hidden_char_visualize length=%s", len(ui["txt_hidden_in"].value))
        spans = []
        for char in ui["txt_hidden_in"].value:
            if char in anomalies:
                spans.append(ft.TextSpan("[!]", style=ft.TextStyle(color="red", weight="bold", bgcolor="yellow100")))
            else:
                spans.append(ft.TextSpan(char, style=ft.TextStyle(color=deps.color_text)))
        ui["view_highlight"].spans = spans
        ui["view_highlight"].visible = True
        ui["txt_hidden_in"].visible = False
        await deps.safe_update(ui["view_highlight"])
        await deps.safe_update(ui["txt_hidden_in"])

    async def run_save(_event):
        if clean_buffer[0] is None:
            return
        selected_path = ui["lbl_hidden_file"].value
        try:
            PROCESS_LOGGER.info("hidden_char_save_start path=%s", selected_path)
            if selected_path.endswith((".xlsx", ".xls")):
                clean_buffer[0].to_excel(selected_path, index=False)
            elif selected_path.endswith(".csv"):
                clean_buffer[0].to_csv(selected_path, index=False, encoding="utf-8-sig")
            else:
                with open(selected_path, "w", encoding="utf-8") as file_obj:
                    file_obj.write(clean_buffer[0])
            await deps.show_toast("บันทึกทับแล้ว")
            clean_buffer[0] = None
            PROCESS_LOGGER.info("hidden_char_save_complete path=%s", selected_path)
        except Exception as ex:
            PROCESS_LOGGER.exception("hidden_char_save_error path=%s error=%s", selected_path, ex)
            await deps.show_toast(f"ผิดพลาด: {ex}", False)

    async def run_clean(_event):
        if await deps.guard_busy() or not ui["txt_hidden_in"].value or ui["txt_hidden_in"].disabled:
            return
        PROCESS_LOGGER.info("hidden_char_clean_text_start length=%s", len(ui["txt_hidden_in"].value))
        ui["txt_hidden_in"].value = deps.clean_hidden_text(ui["txt_hidden_in"].value, anomalies)
        ui["txt_hidden_out"].value = "ล้างอักขระแฝงแล้ว"
        PROCESS_LOGGER.info("hidden_char_clean_text_complete")
        await deps.safe_update(ui["txt_hidden_in"])
        await deps.safe_update(ui["txt_hidden_out"])

    async def clr_all(_event):
        ui["txt_hidden_in"].value = ""
        ui["txt_hidden_out"].value = ""
        ui["view_highlight"].visible = False
        ui["txt_hidden_in"].visible = True
        ui["lbl_hidden_file"].value = file_placeholder
        PROCESS_LOGGER.info("hidden_char_clear_all")
        await deps.safe_update(ui["txt_hidden_in"])
        await deps.safe_update(ui["txt_hidden_out"])
        await deps.safe_update(ui["view_highlight"])
        await deps.safe_update(ui["lbl_hidden_file"])

    async def cp_h(_event):
        if ui["txt_hidden_in"].value:
            deps.page.set_clipboard(ui["txt_hidden_in"].value)
            await deps.show_toast("คัดลอกแล้ว")

    actions["btn_open_hidden"] = op_h
    actions["btn_clear_hidden"] = cl_h
    actions["run_check_hidden"] = run_chk
    actions["run_visual_check"] = run_vis
    actions["run_save_replace_hidden"] = run_save
    actions["run_clean_hidden"] = run_clean
    actions["run_clear_hidden_all"] = clr_all
    actions["btn_copy_clean"] = cp_h


def register_smart_formatter_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def apply_template(event):
        template_id = event.control.data
        ticket = ui["txt_fmt_ticket"].value.strip()
        subject = ui["txt_fmt_subject"].value.strip()
        date_value = ui["txt_fmt_date"].value.strip()

        try:
            if template_id == "1":
                if not ticket or not subject:
                    await deps.show_toast("⚠️ กรุณากรอก Ticket No. และ Subject", False)
                    return
                ui["txt_fmt_res"].value = SMART_FORMATTER_TEMPLATES["1"].format(ticket_no=ticket, subject=subject)
            elif template_id == "2":
                if not ticket or not date_value:
                    await deps.show_toast("⚠️ กรุณากรอก Ticket No. และ วันที่", False)
                    return
                ui["txt_fmt_res"].value = SMART_FORMATTER_TEMPLATES["2"].format(ticket_no=ticket, date=date_value)
            elif template_id == "7":
                if not ticket:
                    await deps.show_toast("⚠️ กรุณากรอก Ticket No.", False)
                    return
                ui["txt_fmt_res"].value = SMART_FORMATTER_TEMPLATES["7"].format(ticket_no=ticket)
            else:
                ui["txt_fmt_res"].value = SMART_FORMATTER_TEMPLATES[template_id]

            await deps.safe_update(ui["txt_fmt_res"])
            await deps.show_toast(f"✅ ใช้ Template #{template_id}")
        except Exception as exc:
            await deps.show_toast(f"❌ Template Error: {exc}", False)

    async def copy_output(_event):
        if not ui["txt_fmt_res"].value:
            return
        deps.page.set_clipboard(ui["txt_fmt_res"].value)
        await deps.show_toast("📋 คัดลอกแล้ว")

    async def clear_fields(_event):
        ui["txt_fmt_ticket"].value = ""
        ui["txt_fmt_subject"].value = ""
        ui["txt_fmt_date"].value = ""
        ui["txt_fmt_input"].value = ""
        ui["txt_fmt_res"].value = ""
        await deps.safe_update(ui["txt_fmt_ticket"])
        await deps.safe_update(ui["txt_fmt_subject"])
        await deps.safe_update(ui["txt_fmt_date"])
        await deps.safe_update(ui["txt_fmt_input"])
        await deps.safe_update(ui["txt_fmt_res"])

    async def format_custom(_event):
        answer = ui["txt_fmt_input"].value.strip()
        if not answer:
            return
        ui["txt_fmt_res"].value = f"เรียน ทีมที่เกี่ยวข้อง\n\n          {answer}\n\nขอบคุณค่ะ"
        await deps.safe_update(ui["txt_fmt_res"])
        await deps.show_toast("📧 จัดรูปแบบคำตอบแล้ว")

    actions["apply_fmt"] = apply_template
    actions["btn_copy_fmt"] = copy_output
    actions["run_clear_fmt"] = clear_fields
    actions["run_format_email"] = format_custom


def register_merge_split_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    cancel_requested = [False]

    async def on_lines_change(event):
        await normalize_split_lines_input(event.control, deps)

    ui["txt_lines"].on_change = on_lines_change

    async def btn_open_src(_event):
        if await deps.guard_busy():
            return
        deps.current_fp_context[deps.fp_dir] = {"ui": ui["txt_src_dir"], "type": "dir"}
        PROCESS_LOGGER.info("merge_split_directory_picker_opened")
        await deps.fp_dir.get_directory_path_async()

    async def btn_cancel_click(_event):
        cancel_requested[0] = True
        deps.lbl_modal_status.value = "⚠️ กำลังหยุดการทำงาน..."
        deps.btn_cancel_process.disabled = True
        PROCESS_LOGGER.warning("merge_split_cancel_requested")
        await deps.safe_update(deps.lbl_modal_status)
        await deps.safe_update(deps.btn_cancel_process)

    deps.btn_cancel_process.on_click = btn_cancel_click

    async def run_split(_event):
        if await deps.guard_busy():
            return
        if not ui["txt_src_dir"].value:
            ui["lbl_split_status"].value = "❌ กรุณาเลือกโฟลเดอร์ต้นทาง"
            PROCESS_LOGGER.warning("merge_split_validation_failed missing_source_directory")
            await deps.safe_update(ui["lbl_split_status"])
            return

        request = build_split_request(ui, deps)
        PROCESS_LOGGER.info(
            "merge_split_start src_dir=%s src_type=%s out_type=%s chunk_size=%s has_header=%s",
            request["src_dir"],
            request["src_ext_label"],
            request["out_ext_label"],
            request["size"],
            request["has_header"],
        )
        os.makedirs(request["out_dir"], exist_ok=True)
        files_to_process = resolve_files_to_process(request, deps)
        if not files_to_process:
            ui["lbl_split_status"].value = f"❌ ไม่พบไฟล์ประเภท {request['src_ext_label']}"
            PROCESS_LOGGER.warning(
                "merge_split_validation_failed no_files_found src_dir=%s src_type=%s",
                request["src_dir"],
                request["src_ext_label"],
            )
            await deps.safe_update(ui["lbl_split_status"])
            return
        PROCESS_LOGGER.info("merge_split_files_resolved count=%s files=%s", len(files_to_process), files_to_process)

        cancel_requested[0] = False
        await activate_split_loading(ui, deps)

        start_time = time.time()
        loop = asyncio.get_running_loop()
        status_callback = build_split_status_callback(deps)

        try:
            result = await asyncio.to_thread(
                deps.process_file_split_streaming,
                src_dir=request["src_dir"],
                files_to_process=files_to_process,
                out_dir=request["out_dir"],
                base_name=request["base_name"],
                size=request["size"],
                has_header=request["has_header"],
                src_ext_label=request["src_ext_label"],
                out_ext_label=request["out_ext_label"],
                out_ext_dot=request["out_ext_dot"],
                status_callback=lambda message, force=False: loop.call_soon_threadsafe(
                    lambda: asyncio.create_task(status_callback(message, force))
                ),
                cancel_check=lambda: cancel_requested[0],
            )

            elapsed = time.time() - start_time
            apply_split_success_state(ui, result, files_to_process, elapsed, cancel_requested[0], deps)
            PROCESS_LOGGER.info(
                "merge_split_complete cancelled=%s total_rows=%s files_created=%s errors=%s elapsed=%.2f",
                cancel_requested[0],
                result["total_rows"],
                result["files_created"],
                len(result["errors"]),
                elapsed,
            )
        except Exception as exc:
            ui["lbl_split_status"].value = f"❌ พลาด: {exc}"
            ui["lbl_split_status"].color = "red"
            PROCESS_LOGGER.exception("merge_split_error error=%s", exc)
        finally:
            await deactivate_split_loading(deps)

    actions["btn_open_src"] = btn_open_src
    actions["run_split"] = run_split
