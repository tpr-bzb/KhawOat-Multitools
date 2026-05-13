import base64
import json
import time
from datetime import datetime, timezone

import flet as ft
from json_tool_helpers import (
    build_csv_tree_notice,
    build_json_diff_controls,
    focus_json_error_line,
    open_json_diff_dialog,
    reset_json_tool_state,
    sync_json_line_numbers,
)
from json_view_helpers import build_json_tree, build_json_tree_from_text
from tool_context import HandlerContext


def register_jwt_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def run_decode_jwt(_event):
        if await deps.guard_busy():
            return
        token = ui["txt_jwt_input"].value.strip()
        if not token:
            return

        result = deps.decode_jwt(token)
        if "error" in result:
            ui["lbl_jwt_status"].value = f"❌ {result['error']}"
            ui["lbl_jwt_status"].color = "red"
        else:
            ui["txt_jwt_header"].value = json.dumps(result["header"], indent=4)
            ui["txt_jwt_payload"].value = json.dumps(result["payload"], indent=4)

            status_text = "✅ Decoded Successfully"
            status_color = deps.color_secondary

            if "exp" in result["payload"]:
                exp_time = result["payload"]["exp"]
                now = time.time()
                if now > exp_time:
                    status_text += " ⚠️ (TOKEN EXPIRED!)"
                    status_color = deps.color_red_400
                else:
                    remaining = exp_time - now
                    status_text += f" 🕒 (Expires in: {int(remaining // 3600)}h {int((remaining % 3600) // 60)}m)"

            ui["lbl_jwt_status"].value = status_text
            ui["lbl_jwt_status"].color = status_color
            await deps.show_toast("🔓 JWT Decoded")

        await deps.safe_update(ui["txt_jwt_header"])
        await deps.safe_update(ui["txt_jwt_payload"])
        await deps.safe_update(ui["lbl_jwt_status"])

    async def run_clear_jwt(_event):
        ui["txt_jwt_input"].value = ""
        ui["txt_jwt_header"].value = ""
        ui["txt_jwt_payload"].value = ""
        ui["lbl_jwt_status"].value = ""
        await deps.safe_update(ui["txt_jwt_input"])
        await deps.safe_update(ui["txt_jwt_header"])
        await deps.safe_update(ui["txt_jwt_payload"])
        await deps.safe_update(ui["lbl_jwt_status"])

    actions["run_decode_jwt"] = run_decode_jwt
    actions["run_clear_jwt"] = run_clear_jwt


def register_time_converter_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def conv_ep(_event):
        val = ui["txt_epoch"].value.replace(",", "").strip()
        ui["lbl_epoch"].value = (
            f"Local Time: {deps.epoch_to_local_datetime_text(int(val))}"
            if val.isdigit()
            else "❌ กรุณากรอกตัวเลข"
        )
        await deps.safe_update(ui["lbl_epoch"])

    async def conv_tk(_event):
        val = ui["txt_ticks"].value.replace(",", "").strip()
        ui["lbl_ticks"].value = (
            f"Local Time: {deps.ticks_to_local_datetime_text(int(val))}"
            if val.isdigit()
            else "❌ กรุณากรอกตัวเลข"
        )
        await deps.safe_update(ui["lbl_ticks"])

    async def ld_ex(_event):
        ui["txt_epoch"].value = "1714272000"
        ui["txt_ticks"].value = "638498592000000000"
        await deps.show_toast("📋 โหลดตัวอย่างแล้ว")
        await deps.safe_update(ui["txt_epoch"])
        await deps.safe_update(ui["txt_ticks"])

    async def ld_cur(_event):
        now = datetime.now()
        now_utc = datetime.now(timezone.utc)
        ui["txt_epoch"].value = str(int(now.timestamp()))
        ticks = (int(now_utc.timestamp()) * 10_000_000) + 621355968000000000
        ui["txt_ticks"].value = str(int(ticks))
        await deps.show_toast("🕒 ดึงเวลาปัจจุบันแล้ว")
        await deps.safe_update(ui["txt_epoch"])
        await deps.safe_update(ui["txt_ticks"])

    async def clr_t(_event):
        ui["txt_epoch"].value = ""
        ui["lbl_epoch"].value = "Local Time: -"
        ui["txt_ticks"].value = ""
        ui["lbl_ticks"].value = "Local Time: -"
        await deps.show_toast("🗑️ ล้างแล้ว")
        await deps.safe_update(ui["txt_epoch"])
        await deps.safe_update(ui["lbl_epoch"])
        await deps.safe_update(ui["txt_ticks"])
        await deps.safe_update(ui["lbl_ticks"])

    actions["conv_epoch"] = conv_ep
    actions["conv_ticks"] = conv_tk
    actions["run_load_time_ex"] = ld_ex
    actions["run_load_current_time"] = ld_cur
    actions["run_clear_time"] = clr_t


def register_base64_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def enc(_event):
        try:
            ui["txt_b64"].value = base64.b64encode(ui["txt_b64"].value.encode("utf-8")).decode("utf-8")
            await deps.show_toast("สำเร็จ")
            await deps.safe_update(ui["txt_b64"])
        except Exception as exc:
            await deps.show_toast(f"Error: {exc}", False)

    async def dec(_event):
        try:
            ui["txt_b64"].value = base64.b64decode(ui["txt_b64"].value.encode("utf-8")).decode("utf-8")
            await deps.show_toast("สำเร็จ")
            await deps.safe_update(ui["txt_b64"])
        except Exception:
            await deps.show_toast("❌ ผิดพลาด", False)

    async def ld_b(_event):
        ui["txt_b64"].value = '{"user": "admin", "status": "active"}'
        await deps.show_toast("📋 โหลดตัวอย่างแล้ว")
        await deps.safe_update(ui["txt_b64"])

    async def clr_b(_event):
        ui["txt_b64"].value = ""
        await deps.show_toast("🗑️ ล้างแล้ว")
        await deps.safe_update(ui["txt_b64"])

    actions["run_b64_enc"] = enc
    actions["run_b64_dec"] = dec
    actions["run_load_b64_ex"] = ld_b
    actions["run_clear_b64"] = clr_b


def register_compare_text_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def run_compare_text(_event):
        if await deps.guard_busy():
            return

        original_text = ui["txt_compare_1"].value
        changed_text = ui["txt_compare_2"].value
        if not original_text and not changed_text:
            await deps.show_toast("⚠️ กรุณากรอกข้อความก่อน", False)
            return

        try:
            diff = deps.get_text_diff(original_text, changed_text)
            ui["col_diff_main"].controls.clear()

            if not diff:
                ui["col_diff_main"].controls.append(
                    ft.Text(
                        "✅ ข้อมูลเหมือนกันทุกประการ",
                        color=deps.color_secondary,
                        weight="bold",
                        text_align=ft.TextAlign.CENTER,
                    )
                )
            else:
                left_line = 1
                right_line = 1

                for line in diff:
                    tag = line[:2]
                    content = line[2:]

                    left_number = " "
                    right_number = " "
                    left_text = " "
                    right_text = " "
                    left_bg = deps.color_transparent
                    right_bg = deps.color_transparent
                    left_color = "white54"
                    right_color = "white54"
                    left_number_color = "white24"
                    right_number_color = "white24"

                    if tag == "  ":
                        left_number = str(left_line)
                        right_number = str(right_line)
                        left_text = content
                        right_text = content
                        left_line += 1
                        right_line += 1
                    elif tag == "- ":
                        left_number = str(left_line)
                        left_text = content
                        left_bg = "#2E1A1A"
                        left_color = deps.color_red_400
                        left_number_color = "red400"
                        left_line += 1
                    elif tag == "+ ":
                        right_number = str(right_line)
                        right_text = content
                        right_bg = "#1A2E1A"
                        right_color = deps.color_green_400
                        right_number_color = "green400"
                        right_line += 1
                    elif tag == "? ":
                        continue

                    ui["col_diff_main"].controls.append(
                        ft.Row(
                            [
                                ft.Text(
                                    left_number,
                                    color=left_number_color,
                                    font_family="Consolas",
                                    size=12,
                                    text_align=ft.TextAlign.RIGHT,
                                    width=35,
                                ),
                                ft.Container(
                                    content=ft.Text(left_text, color=left_color, font_family="Consolas", size=13),
                                    bgcolor=left_bg,
                                    expand=True,
                                    padding=ft.padding.only(left=5),
                                ),
                                ft.VerticalDivider(width=1, color="white10"),
                                ft.Text(
                                    right_number,
                                    color=right_number_color,
                                    font_family="Consolas",
                                    size=12,
                                    text_align=ft.TextAlign.RIGHT,
                                    width=35,
                                ),
                                ft.Container(
                                    content=ft.Text(right_text, color=right_color, font_family="Consolas", size=13),
                                    bgcolor=right_bg,
                                    expand=True,
                                    padding=ft.padding.only(left=5),
                                ),
                            ],
                            spacing=5,
                            vertical_alignment=ft.CrossAxisAlignment.START,
                        )
                    )

            await deps.show_toast("🔍 เปรียบเทียบเสร็จสิ้น")
            await deps.safe_update(ui["col_diff_main"])
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)

    async def run_clear_compare(_event):
        ui["txt_compare_1"].value = ""
        ui["txt_compare_2"].value = ""
        ui["col_diff_main"].controls.clear()
        await deps.safe_update(ui["txt_compare_1"])
        await deps.safe_update(ui["txt_compare_2"])
        await deps.safe_update(ui["col_diff_main"])

    actions["run_compare_text"] = run_compare_text
    actions["run_clear_compare"] = run_clear_compare


def register_json_tool_handlers(
    ui: dict,
    actions: dict,
    *,
    deps: HandlerContext,
):
    async def update_tree():
        ui["tree_container"].controls.clear()
        ui["tree_container"].controls.append(
            build_json_tree_from_text(ui["txt_json_input"].value, deps)
        )
        await deps.safe_update(ui["tree_container"])

    async def sync_and_detect(_event):
        await sync_json_line_numbers(ui, deps)
        value = ui["txt_json_input"].value.strip()
        if deps.is_base64_json(value):
            await deps.show_toast("💡 ตรวจพบ Base64 ที่อาจเป็น JSON! กดปุ่ม B64 Decode ได้ครับ", True)

    ui["txt_json_input"].on_change = sync_and_detect

    async def run_fmt_json(_event):
        if await deps.guard_busy():
            return
        try:
            parsed = json.loads(ui["txt_json_input"].value)
            ui["txt_json_input"].value = json.dumps(parsed, indent=4, ensure_ascii=False)
            await sync_and_detect(None)
            await update_tree()
            await deps.show_toast("✅ Format & Updated View")
        except json.JSONDecodeError as exc:
            error_line = exc.lineno
            await deps.show_toast(f"❌ Error บรรทัด {error_line}", False)
            await focus_json_error_line(ui, error_line, deps)
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)
        await deps.safe_update(ui["txt_json_input"])

    async def run_minify_json(_event):
        if await deps.guard_busy():
            return
        try:
            ui["txt_json_input"].value = json.dumps(
                json.loads(ui["txt_json_input"].value),
                separators=(",", ":"),
                ensure_ascii=False,
            )
            await deps.show_toast("✅ Minify สำเร็จ")
            await update_tree()
            await deps.safe_update(ui["txt_json_input"])
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)

    async def run_b64_decode_json(_event):
        if await deps.guard_busy():
            return
        try:
            value = ui["txt_json_input"].value.strip()
            decoded = base64.b64decode(value).decode("utf-8")
            try:
                parsed = json.loads(decoded)
                ui["txt_json_input"].value = json.dumps(parsed, indent=4, ensure_ascii=False)
            except Exception:
                ui["txt_json_input"].value = decoded
            await sync_and_detect(None)
            await update_tree()
            await deps.show_toast("🔓 Decode สำเร็จ")
            await deps.safe_update(ui["txt_json_input"])
        except Exception:
            await deps.show_toast("❌ ไม่ใช่ Base64 ที่ถูกต้อง", False)

    async def run_search_json(_event):
        keyword = ui["txt_json_search"].value.strip()
        if not keyword:
            return
        try:
            data = json.loads(ui["txt_json_input"].value)
            results = deps.search_json(data, keyword)
            if results:
                ui["tree_container"].controls.clear()
                ui["tree_container"].controls.append(build_json_tree(data, deps, highlighted_paths=results))
                await deps.show_toast(f"🔎 พบ {len(results)} จุด")
            else:
                await deps.show_toast("🔍 ไม่พบข้อมูล", False)
            await deps.safe_update(ui["tree_container"])
        except Exception:
            await deps.show_toast("❌ กรุณา Format JSON ก่อนค้นหา", False)

    async def run_clear_json(_event):
        await reset_json_tool_state(ui, deps)

    async def run_load_json_data(_event):
        ui["txt_json_input"].value = (
            '{"requestId": "REQ-20260427-0001", "customer": {"id": "CUST-10001", '
            '"name": "John Doe"}, "items": [{"sku": "SKU-001", "qty": 2}]}'
        )
        await run_fmt_json(None)

    async def run_json_to_csv(_event):
        if await deps.guard_busy():
            return
        try:
            data = json.loads(ui["txt_json_input"].value)
            csv_text = deps.json_to_csv_text(data)
            if csv_text:
                ui["txt_json_input"].value = csv_text
                await sync_and_detect(None)
                ui["tree_container"].controls.clear()
                ui["tree_container"].controls.append(build_csv_tree_notice())
                await deps.show_toast("📊 แปลงเป็น CSV สำเร็จ")
            else:
                await deps.show_toast("❌ JSON ต้องเป็นรูปแบบ List หรือ Dict เท่านั้น", False)
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)
        await deps.safe_update(ui["txt_json_input"])
        await deps.safe_update(ui["tree_container"])

    async def run_csv_to_json(_event):
        if await deps.guard_busy():
            return
        try:
            csv_text = ui["txt_json_input"].value.strip()
            data = deps.csv_to_json_data(csv_text)
            ui["txt_json_input"].value = json.dumps(data, indent=4, ensure_ascii=False)
            await sync_and_detect(None)
            await update_tree()
            await deps.show_toast("🧾 แปลงเป็น JSON สำเร็จ")
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)
        await deps.safe_update(ui["txt_json_input"])

    async def run_diff_json(_event):
        txt_diff_2 = ft.TextField(
            label="วาง JSON ตัวที่สองเพื่อเปรียบเทียบ (JSON 2)",
            multiline=True,
            min_lines=10,
            border_color=deps.color_primary,
            bgcolor="#1E231E",
        )

        async def do_compare(_compare_event, dialog):
            try:
                obj1 = json.loads(ui["txt_json_input"].value)
                obj2 = json.loads(txt_diff_2.value)
                diffs = deps.compare_json(obj1, obj2)

                ui["tree_container"].controls.clear()
                ui["tree_container"].controls.extend(build_json_diff_controls(diffs, deps))

                await deps.safe_update(ui["tree_container"])
                dialog.open = False
                await deps.page.update_async()
            except Exception as exc:
                await deps.show_toast(f"❌ Error: {exc}", False)

        await open_json_diff_dialog(deps, txt_diff_2, do_compare)

    async def run_validate_json(_event):
        value = ui["txt_json_input"].value.strip()
        if not value:
            return
        try:
            data = json.loads(value)
            message = "✅ JSON Valid!"
            if isinstance(data, dict):
                message += f" (Object with {len(data)} keys)"
            elif isinstance(data, list):
                message += f" (Array with {len(data)} items)"
            await deps.show_toast(message)
            await update_tree()
        except json.JSONDecodeError as exc:
            await deps.show_toast(f"❌ Invalid JSON: บรรทัด {exc.lineno}", False)
        except Exception as exc:
            await deps.show_toast(f"❌ Error: {exc}", False)

    async def btn_copy_json(_event):
        if await deps.guard_busy():
            return
        if not ui["txt_json_input"].value:
            await deps.show_toast("ไม่มีข้อมูล", False)
            return
        deps.page.set_clipboard(ui["txt_json_input"].value)
        await deps.show_toast("📋 คัดลอกแล้ว")

    actions["run_fmt_json"] = run_fmt_json
    actions["run_minify_json"] = run_minify_json
    actions["run_clear_json"] = run_clear_json
    actions["run_load_json_data"] = run_load_json_data
    actions["btn_copy_json"] = btn_copy_json
    actions["run_search_json"] = run_search_json
    actions["run_b64_decode_json"] = run_b64_decode_json
    actions["run_json_to_csv"] = run_json_to_csv
    actions["run_csv_to_json"] = run_csv_to_json
    actions["run_diff_json"] = run_diff_json
    actions["run_validate_json"] = run_validate_json
