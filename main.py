import flet as ft
import json
import base64
import qrcode
import io
import os
import asyncio
import time
import requests
import csv
from ui_config import (
    COLOR_BG,
    COLOR_SIDEBAR,
    COLOR_CARD,
    COLOR_SURFACE,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_ACCENT,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_ERROR,
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    BORDER_SUBTLE,
    RESPONSIVE_THRESHOLD,
    configure_page,
)
from ui_views import build_tool_view, nav_btn
from services import (
    analyze_hidden_chars,
    build_password,
    clean_hidden_text,
    epoch_to_local_datetime_text,
    generate_qr_base64,
    get_extension,
    list_files_to_process,
    process_file_split_streaming,
    process_hidden_char_file,
    ticks_to_local_datetime_text,
    find_binary_indices,
    check_for_patches,
    apply_patch,
    search_json,
    is_base64_json,
    json_to_csv_text,
    csv_to_json_data,
    compare_json,
    get_text_diff,
    decode_jwt,
    optimize_image,
)
from datetime import datetime, timezone

COLORS = getattr(ft, "colors", getattr(ft, "Colors", None))
COLOR_TRANSPARENT = getattr(COLORS, "TRANSPARENT", "transparent")
COLOR_RED_400 = getattr(COLORS, "RED_400", "#ef5350")
COLOR_AMBER_300 = getattr(COLORS, "AMBER_300", "#ffd54f")
COLOR_BLUE_300 = getattr(COLORS, "BLUE_300", "#64b5f6")
COLOR_GREEN_400 = getattr(COLORS, "GREEN_400", "#66bb6a")

CURRENT_VERSION = "16.7"
VERSION_JSON_URL = "https://raw.githubusercontent.com/tpr-bzb/KhawOat-Multitools/main/version.json"

async def main(page: ft.Page):
    # Benchmark start
    init_start_time = time.time()
    
    # --- 🌊 0. Splash Screen Configuration ---
    lbl_splash_status = ft.Text("Initializing Pro Systems...", size=14, italic=True, color=COLOR_TEXT_DIM)
    pb_splash = ft.ProgressBar(width=300, color=COLOR_PRIMARY, bgcolor="white10", value=0)

    splash_content = ft.Container(
        content=ft.Column([
            ft.Text("🛠️", size=100), 
            ft.Text("KHAWOAT MULTI-TOOLS PRO", size=32, weight="bold", color=COLOR_PRIMARY), 
            lbl_splash_status,
            ft.Container(height=30),
            pb_splash, 
        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        expand=True,
        bgcolor=COLOR_BG, 
        alignment=getattr(ft.alignment, "center", ft.alignment.center_left),
    )

    splash_overlay = ft.Container(
        content=splash_content,
        expand=True,
        visible=True,
    )

    page.overlay.append(splash_overlay)
    page.update()

    # --- 🛠️ Auto-Update System (Splash Phase) ---
    import sys
    async def run_auto_update():
        try:
            lbl_splash_status.value = "🔍 Checking for Professional Updates..."
            page.update()
            
            # 1. Check version.json with Cache Bypass
            cache_bypass_url = f"{VERSION_JSON_URL}?t={int(time.time())}"
            res = requests.get(cache_bypass_url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data["version"] > CURRENT_VERSION:
                    # ✅ Check for Force Setup (v16.5 NEW)
                    if data.get("force_setup"):
                        # ... (existing force setup logic)
                        lbl_splash_status.value = "⚠️ Critical Update Required!"
                        lbl_splash_status.color = COLOR_ACCENT
                        pb_splash.visible = False
                        page.update()
                        
                        import webbrowser
                        download_url = data.get("update_url", "https://github.com/tpr-bzb/KhawOat-Multitools")
                        
                        async def open_download(e):
                            webbrowser.open(download_url)
                        
                        btn_download = ft.ElevatedButton(
                            "🌐 Download Installer", 
                            icon=ft.icons.DOWNLOAD, 
                            on_click=open_download,
                            bgcolor=COLOR_PRIMARY,
                            color="black",
                            height=50
                        )
                        splash_content.content.controls.append(btn_download)
                        page.update()
                        while True: await asyncio.sleep(1)

                    lbl_splash_status.value = "🚀 Pre-loading Professional Assets..."
                    page.update()
                    
                    # 2. Check for patches with Cache Bypass for Manifest
                    MANIFEST_URL = VERSION_JSON_URL.replace("version.json", "manifest.json")
                    cache_bypass_manifest = f"{MANIFEST_URL}?t={int(time.time())}"
                    base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
                    
                    patches, remote_ver = await check_for_patches(cache_bypass_manifest, base_dir)
                    if patches:
                        total = len(patches)
                        for i, patch in enumerate(patches):
                            lbl_splash_status.value = f"📦 Patching: {patch['rel_path']} ({i+1}/{total})"
                            pb_splash.value = (i + 1) / total
                            page.update()
                            await apply_patch(patch['url'], os.path.join(base_dir, patch['rel_path']))
                        
                        lbl_splash_status.value = "✨ Update Complete! Restarting..."
                        page.update()
                        await asyncio.sleep(1)
                        # Restart
                        if getattr(sys, 'frozen', False):
                            os.execl(sys.executable, sys.executable, *sys.argv)
                        else:
                            os.execl(sys.executable, sys.executable, __file__, *sys.argv)
        except Exception as e:
            lbl_splash_status.value = f"⚠️ Offline Mode: {e}"
            page.update()
            await asyncio.sleep(1)

    await run_auto_update()
    lbl_splash_status.value = "🎯 Ready to Deploy..."
    pb_splash.value = 1
    page.update()
    await asyncio.sleep(0.5)
    splash_overlay.visible = False
    page.update()

    # --- ⚙️ Configuration ---
    configure_page(page)

    if not hasattr(page, "update_async"):
        async def _page_update_async():
            page.update()
        page.update_async = _page_update_async

    # --- 🕒 Shared State & Helpers ---
    busy = False
    nav_controls = []
    ui_cache = {}
    actions_cache = {}
    cancel_requested = False

    async def safe_update(control):
        if not control: return
        try:
            if hasattr(control, "page") and control.page:
                if hasattr(control, "update_async"): await control.update_async()
                else: control.update()
            else:
                await page.update_async()
        except:
            pass

    async def set_busy(value: bool):
        nonlocal busy
        busy = value
        for control in nav_controls:
            control.disabled = value
            await safe_update(control)

    async def show_toast(message: str, ok: bool = True):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=COLOR_SECONDARY if ok else "red",
            open=True,
        )
        await page.update_async()

    async def guard_busy() -> bool:
        if busy:
            await show_toast("กำลังประมวลผลอยู่ กรุณารอสักครู่...", ok=False)
            return True
        return False

    async def close_banner(e):
        page.banner.open = False
        await page.update_async()

    # Shared UI Elements
    lbl_clock = ft.Text("", size=20, weight="bold", color=COLOR_PRIMARY, font_family="Consolas")
    btn_cancel_process = ft.ElevatedButton("❌ ยกเลิก", color="white", bgcolor="#8B0000")
    lbl_modal_status = ft.Text("กำลังเตรียมการ...", color="white", text_align=ft.TextAlign.CENTER)
    
    dlg_loading = ft.AlertDialog(
        modal=True,
        title=ft.Text("⏳ System Processing", weight="bold", color=COLOR_PRIMARY),
        content=ft.Container(
            content=ft.Column([
                ft.ProgressRing(color=COLOR_ACCENT, stroke_width=5),
                ft.Container(height=10),
                lbl_modal_status
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            height=120, width=300
        ),
        actions=[ft.Row([btn_cancel_process], alignment=ft.MainAxisAlignment.CENTER)],
        actions_alignment=ft.MainAxisAlignment.CENTER
    )

    # --- 📂 FilePickers (Flet-Native) ---
    current_fp_context = {}

    async def on_fp_result(e: ft.FilePickerResultEvent):
        if not e.path and not e.files: return
        ctx = current_fp_context.get(e.control)
        if not ctx: return
        
        target_ui = ctx.get("ui")
        if ctx["type"] == "dir" and e.path:
            if target_ui is not None:
                target_ui.value = e.path
        elif ctx["type"] == "open" and e.files:
            if target_ui is not None:
                target_ui.value = e.files[0].path
        elif ctx["type"] == "save":
            save_path = e.path or (e.files[0].path if e.files else None)
            if save_path and "callback" in ctx:
                await ctx["callback"](save_path)
            return
            
        if target_ui is not None:
            await safe_update(target_ui)

    fp_dir = ft.FilePicker(on_result=on_fp_result)
    fp_open = ft.FilePicker(on_result=on_fp_result)
    fp_save = ft.FilePicker(on_result=on_fp_result)
    page.overlay.extend([fp_dir, fp_open, fp_save])

    # --- 🧩 Lazy Loading Engine ---
    async def get_tool_assets(index):
        if index in ui_cache:
            return ui_cache[index], actions_cache[index]

        ui = {"lbl_clock": lbl_clock, "dlg_loading": dlg_loading}
        actions = {}

        if index == 0: # Home
            def get_greeting_data():
                hour = datetime.now().hour
                if 5 <= hour < 12: return ("อรุณสวัสดิ์ครับ! พร้อมลุยงานเช้านี้แล้วจ้า", "morning.gif")
                elif 12 <= hour < 18: return ("สวัสดียามบ่ายครับ! อย่าลืมดื่มน้ำพักสายตานะ", "afternoon.gif")
                else: return ("คืนนี้อีกยาวไกล... รักษาสุขภาพด้วยนะครับ", "night.gif")
            
            gt, gg = get_greeting_data()
            ui["greeting_text"] = gt
            ui["greeting_gif"] = gg

            # Actions for Quick Tools
            async def nav_to_tool(e):
                idx = int(e.control.data)
                await update_view(idx)
            actions["nav_tool"] = nav_to_tool

        elif index == 12: # JWT Decoder
            ui["txt_jwt_input"] = ft.TextField(label="JWT Token", multiline=True, min_lines=5, border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["txt_jwt_header"] = ft.TextField(label="Header (JSON)", multiline=True, read_only=True, min_lines=5, border_color=COLOR_PRIMARY, bgcolor="#181C18", text_style=ft.TextStyle(font_family="Consolas"))
            ui["txt_jwt_payload"] = ft.TextField(label="Payload (JSON)", multiline=True, read_only=True, min_lines=10, border_color=COLOR_SECONDARY, bgcolor="#181C18", text_style=ft.TextStyle(font_family="Consolas"))
            ui["lbl_jwt_status"] = ft.Text("", weight="bold")

            async def run_decode_jwt(e):
                if await guard_busy(): return
                token = ui["txt_jwt_input"].value.strip()
                if not token: return
                
                result = decode_jwt(token)
                if "error" in result:
                    ui["lbl_jwt_status"].value = f"❌ {result['error']}"
                    ui["lbl_jwt_status"].color = "red"
                else:
                    ui["txt_jwt_header"].value = json.dumps(result["header"], indent=4)
                    ui["txt_jwt_payload"].value = json.dumps(result["payload"], indent=4)
                    
                    # Check expiration
                    status_text = "✅ Decoded Successfully"
                    status_color = COLOR_SECONDARY
                    
                    if "exp" in result["payload"]:
                        exp_time = result["payload"]["exp"]
                        now = time.time()
                        if now > exp_time:
                            status_text += " ⚠️ (TOKEN EXPIRED!)"
                            status_color = COLOR_RED_400
                        else:
                            rem = exp_time - now
                            status_text += f" 🕒 (Expires in: {int(rem//3600)}h {int((rem%3600)//60)}m)"
                    
                    ui["lbl_jwt_status"].value = status_text
                    ui["lbl_jwt_status"].color = status_color
                    await show_toast("🔓 JWT Decoded")
                
                await safe_update(ui["txt_jwt_header"])
                await safe_update(ui["txt_jwt_payload"])
                await safe_update(ui["lbl_jwt_status"])

            async def run_clear_jwt(e):
                ui["txt_jwt_input"].value = ""; ui["txt_jwt_header"].value = ""; ui["txt_jwt_payload"].value = ""; ui["lbl_jwt_status"].value = ""
                await safe_update(ui["txt_jwt_input"]); await safe_update(ui["txt_jwt_header"]); await safe_update(ui["txt_jwt_payload"]); await safe_update(ui["lbl_jwt_status"])

            actions["run_decode_jwt"] = run_decode_jwt; actions["run_clear_jwt"] = run_clear_jwt

        elif index == 13: # Image Optimizer
            ui["txt_img_src"] = ft.TextField(label="ที่อยู่ไฟล์รูปภาพ", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, expand=True)
            ui["slider_img_quality"] = ft.Slider(min=10, max=100, divisions=18, value=80, label="{value}%", active_color=COLOR_PRIMARY)
            ui["dd_img_format"] = ft.Dropdown(label="นามสกุลเป้าหมาย", options=[ft.dropdown.Option("Original"), ft.dropdown.Option("JPEG"), ft.dropdown.Option("PNG"), ft.dropdown.Option("WEBP")], value="Original", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["lbl_img_status"] = ft.Text("สถานะ: พร้อม", color="white54")
            ui["img_preview"] = ft.Image(src="", width=300, height=300, fit=ft.ImageFit.CONTAIN)

            async def btn_open_img(e):
                if await guard_busy(): return
                current_fp_context[fp_open] = {"ui": ui["txt_img_src"], "type": "open"}
                await fp_open.pick_files_async(allowed_extensions=["jpg", "jpeg", "png", "webp"])
                # Wait for result to show preview? For now simple
            
            async def run_optimize_img(e):
                if await guard_busy(): return
                if not ui["txt_img_src"].value: return
                
                src_path = ui["txt_img_src"].value
                dir_name = os.path.dirname(src_path)
                base_name = os.path.splitext(os.path.basename(src_path))[0]
                
                fmt = ui["dd_img_format"].value
                ext = ".jpg" if fmt == "JPEG" else ".png" if fmt == "PNG" else ".webp" if fmt == "WEBP" else os.path.splitext(src_path)[1]
                target_fmt = None if fmt == "Original" else fmt
                
                out_path = os.path.join(dir_name, f"{base_name}_optimized{ext}")
                
                await set_busy(True)
                ui["lbl_img_status"].value = "⏳ กำลังประมวลผล..."
                await safe_update(ui["lbl_img_status"])
                
                success, result = await asyncio.to_thread(optimize_image, src_path, out_path, int(ui["slider_img_quality"].value), target_fmt)
                
                if success:
                    old_size = os.path.getsize(src_path) / 1024
                    new_size = result / 1024
                    reduction = (1 - (new_size / old_size)) * 100
                    ui["lbl_img_status"].value = f"✅ สำเร็จ! {old_size:.1f}KB -> {new_size:.1f}KB (ลดลง {reduction:.1f}%)"
                    ui["lbl_img_status"].color = COLOR_SECONDARY
                    await show_toast("🖼️ บันทึกรูปภาพเรียบร้อย")
                else:
                    ui["lbl_img_status"].value = f"❌ Error: {result}"
                    ui["lbl_img_status"].color = "red"
                
                await set_busy(False)
                await safe_update(ui["lbl_img_status"])

            actions["btn_open_img"] = btn_open_img; actions["run_optimize_img"] = run_optimize_img

        elif index == 1: # Merge & Split
            ui["txt_src_dir"] = ft.TextField(label="โฟลเดอร์ต้นทาง", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, expand=True)
            ui["dd_src_ext"] = ft.Dropdown(label="นามสกุลต้นทาง", options=[ft.dropdown.Option("CSV"), ft.dropdown.Option("EXCEL"), ft.dropdown.Option("TXT"), ft.dropdown.Option("NO EXT")], value="CSV", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, width=150)
            ui["dd_out_ext"] = ft.Dropdown(label="นามสกุลปลายทาง", options=[ft.dropdown.Option("CSV"), ft.dropdown.Option("EXCEL"), ft.dropdown.Option("TXT"), ft.dropdown.Option("NO EXT")], value="CSV", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, width=150)
            ui["txt_base_name"] = ft.TextField(label="ชื่อไฟล์ผลลัพธ์", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, expand=True)
            ui["txt_lines"] = ft.TextField(label="จำนวนแถวต่อไฟล์", value="1,000", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, width=200)
            ui["chk_header"] = ft.Checkbox(label="ข้อมูลมี Header (แถวแรก)", value=True, fill_color=COLOR_PRIMARY)
            ui["lbl_split_status"] = ft.Text("สถานะ: พร้อมทำงาน", color="white54")
            ui["lbl_split_summary"] = ft.Text("", color=COLOR_PRIMARY, weight="bold")

            async def on_lines_change(e):
                val = e.control.value.replace(",", "")
                if val.isdigit(): 
                    e.control.value = f"{int(val):,}"
                    await safe_update(e.control)
            ui["txt_lines"].on_change = on_lines_change

            async def btn_open_src(e):
                if await guard_busy(): return
                current_fp_context[fp_dir] = {"ui": ui["txt_src_dir"], "type": "dir"}
                await fp_dir.get_directory_path_async()
            
            async def btn_cancel_click(e):
                nonlocal cancel_requested; cancel_requested = True
                lbl_modal_status.value = "⚠️ กำลังหยุดการทำงาน..."
                btn_cancel_process.disabled = True
                await safe_update(lbl_modal_status)
                await safe_update(btn_cancel_process)
            btn_cancel_process.on_click = btn_cancel_click

            async def run_split(e):
                if busy: return
                if not ui["txt_src_dir"].value:
                    ui["lbl_split_status"].value = "❌ กรุณาเลือกโฟลเดอร์ต้นทาง"
                    await safe_update(ui["lbl_split_status"]); return
                
                src_dir = ui["txt_src_dir"].value
                out_dir = os.path.join(src_dir, "Split_Output")
                os.makedirs(out_dir, exist_ok=True)
                
                src_ext_label, out_ext_label = ui["dd_src_ext"].value, ui["dd_out_ext"].value
                src_ext_dot, out_ext_dot = get_extension(src_ext_label), get_extension(out_ext_label)
                base_name = ui["txt_base_name"].value.strip() or "output"
                size_str = ui["txt_lines"].value.replace(",", "")
                size = int(size_str) if size_str.isdigit() and int(size_str) > 0 else 1000
                has_header = ui["chk_header"].value

                files_to_process = list_files_to_process(src_dir, src_ext_label, src_ext_dot)
                if not files_to_process:
                    ui["lbl_split_status"].value = f"❌ ไม่พบไฟล์ประเภท {src_ext_label}"
                    await safe_update(ui["lbl_split_status"]); return

                nonlocal cancel_requested; cancel_requested = False; btn_cancel_process.disabled = False
                ui["lbl_split_summary"].value = ""
                page.dialog = dlg_loading; dlg_loading.open = True
                await set_busy(True); await page.update_async()

                start_time = time.time(); last_ui_update = time.time()
                loop = asyncio.get_running_loop()

                async def status_cb(msg, force=False):
                    nonlocal last_ui_update
                    lbl_modal_status.value = msg
                    now = time.time()
                    if force or (now - last_ui_update > 0.15):
                        await safe_update(lbl_modal_status)
                        last_ui_update = now; await asyncio.sleep(0.001)

                try:
                    # Execute heavy lifting via service with thread-safe callback
                    result = await asyncio.to_thread(
                        process_file_split_streaming,
                        src_dir=src_dir, files_to_process=files_to_process, out_dir=out_dir,
                        base_name=base_name, size=size, has_header=has_header,
                        src_ext_label=src_ext_label, out_ext_label=out_ext_label, out_ext_dot=out_ext_dot,
                        status_callback=lambda m, force=False: loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(status_cb(m, force))
                        ),
                        cancel_check=lambda: cancel_requested
                    )

                    elapsed = time.time() - start_time
                    if cancel_requested:
                        ui["lbl_split_status"].value = "⚠️ ผู้ใช้ยกเลิก"; ui["lbl_split_status"].color = "orange"
                        ui["lbl_split_summary"].value = f"🛑 หยุดที่: {result['files_created']} ไฟล์ | เวลา: {elapsed:.2f}s"
                    else:
                        ui["lbl_split_status"].value = "✅ สำเร็จ!" if not result["errors"] else "✅ สำเร็จ (พบปัญหาบางจุด)"
                        ui["lbl_split_status"].color = COLOR_SECONDARY
                        ui["lbl_split_summary"].value = f"📊 นำเข้า {len(files_to_process)} ไฟล์ | {result['total_rows']:,} แถว | แบ่งได้ {result['files_created']} ไฟล์ | {elapsed:.2f}s"
                except Exception as ex:
                    ui["lbl_split_status"].value = f"❌ พลาด: {ex}"; ui["lbl_split_status"].color = "red"
                finally:
                    dlg_loading.open = False; await set_busy(False); await page.update_async()

            actions["btn_open_src"] = btn_open_src; actions["run_split"] = run_split

        elif index == 2: # QR Generator
            ui["txt_qr"] = ft.TextField(label="URL หรือ ข้อความ", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["img_qr"] = ft.Image(src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==", width=250, height=250, visible=False)
            ui["lbl_qr_status"] = ft.Text("", color="white54")
            ui["qr_container"] = ft.Container(content=ui["img_qr"], alignment=getattr(ft.alignment, "center", ft.alignment.center_left), padding=20, bgcolor="white", border_radius=RADIUS_MD, visible=False)

            async def run_gen_qr(e):
                if await guard_busy(): return
                if not ui["txt_qr"].value: await show_toast("กรุณากรอกข้อความก่อน", False); return
                try:
                    b64_qr = generate_qr_base64(ui["txt_qr"].value)
                    if b64_qr:
                        ui["img_qr"].src_base64 = b64_qr
                        ui["img_qr"].visible = True
                        ui["qr_container"].visible = True
                        ui["lbl_qr_status"].value = "✅ สำเร็จ"
                        ui["lbl_qr_status"].color = COLOR_SECONDARY
                        await safe_update(ui["qr_container"])
                        await show_toast("สร้าง QR สำเร็จ")
                except Exception as ex:
                    ui["lbl_qr_status"].value = f"❌ Error: {ex}"
                    ui["lbl_qr_status"].color = "red"
                await safe_update(ui["img_qr"])
                await safe_update(ui["lbl_qr_status"])

            async def do_save_qr(path):
                if path:
                    with open(path, "wb") as f: f.write(base64.b64decode(ui["img_qr"].src_base64))
                    await show_toast("บันทึกรูปสำเร็จ")

            async def btn_save_qr(e):
                if await guard_busy(): return
                if not ui["img_qr"].src_base64: await show_toast("สร้าง QR ก่อน", False); return
                current_fp_context[fp_save] = {"type": "save", "callback": do_save_qr}
                await fp_save.save_file_async(file_name="qrcode.png", file_type=ft.FilePickerFileType.IMAGE, allowed_extensions=["png"])

            actions["run_gen_qr"] = run_gen_qr; actions["btn_save_qr"] = btn_save_qr

        elif index == 3: # JSON Tool
            ui["txt_line_numbers"] = ft.TextField(value="1", multiline=True, read_only=True, width=55, text_size=14, text_align=ft.TextAlign.RIGHT, border=ft.InputBorder.NONE, bgcolor=COLOR_TRANSPARENT, color=COLOR_PRIMARY, text_style=ft.TextStyle(font_family="Consolas", height=1.5), content_padding=ft.padding.only(top=12, right=10, bottom=12))
            ui["tree_container"] = ft.Column(scroll=ft.ScrollMode.ALWAYS, expand=True)
            
            async def update_tree():
                ui["tree_container"].controls.clear()
                val = ui["txt_json_input"].value.strip()
                if not val:
                    ui["tree_container"].controls.append(ft.Text("⚠️ ไม่มีข้อมูล", color="orange"))
                else:
                    try:
                        data = json.loads(val)
                        ui["tree_container"].controls.append(build_tree(data))
                    except Exception as ex:
                        ui["tree_container"].controls.append(ft.Text(f"❌ JSON Error: {ex}", color="red"))
                await safe_update(ui["tree_container"])

            def build_tree(data, label="root", highlighted_paths=None):
                if highlighted_paths is None: highlighted_paths = []
                is_highlighted = label in highlighted_paths or any(p.startswith(label + ".") or p.startswith(label + "[") for p in highlighted_paths)
                
                text_color = COLOR_PRIMARY if is_highlighted else COLOR_AMBER_300
                
                if isinstance(data, dict):
                    return ft.ExpansionTile(
                        title=ft.Text(label, color=text_color, weight="bold" if is_highlighted else "normal"),
                        subtitle=ft.Text(f"{{ {len(data)} items }}", size=10, italic=True),
                        initially_expanded=is_highlighted,
                        controls=[build_tree(v, f"{label}.{k}" if label != "root" else k, highlighted_paths) for k, v in data.items()]
                    )
                elif isinstance(data, list):
                    return ft.ExpansionTile(
                        title=ft.Text(label, color=COLOR_BLUE_300 if not is_highlighted else COLOR_PRIMARY, weight="bold" if is_highlighted else "normal"),
                        subtitle=ft.Text(f"[ {len(data)} items ]", size=10, italic=True),
                        initially_expanded=is_highlighted,
                        controls=[build_tree(v, f"{label}[{i}]" if label != "root" else f"[{i}]", highlighted_paths) for i, v in enumerate(data)]
                    )
                else:
                    return ft.ListTile(
                        title=ft.Text(f"{label}: ", size=13, weight="bold" if is_highlighted else "normal", color=COLOR_TEXT if not is_highlighted else COLOR_PRIMARY),
                        trailing=ft.Text(f"{data}", color=COLOR_GREEN_400 if not is_highlighted else COLOR_PRIMARY, selectable=True),
                        dense=True
                    )

            async def sync_and_detect(e):
                # 1. Sync line numbers
                cnt = len(ui["txt_json_input"].value.split('\n'))
                lines = "\n".join(str(i) for i in range(1, cnt + 1))
                if ui["txt_line_numbers"].value != lines: 
                    ui["txt_line_numbers"].value = lines
                    await safe_update(ui["txt_line_numbers"])
                
                # 2. Auto-detect Base64 JSON
                val = ui["txt_json_input"].value.strip()
                if is_base64_json(val):
                    await show_toast("💡 ตรวจพบ Base64 ที่อาจเป็น JSON! กดปุ่ม B64 Decode ได้ครับ", True)
                
                # 3. Update Tree (Debounced would be better, but let's do it simply for now)
                # For large JSON, we might want to only update on Format/submit
                # await update_tree()

            ui["txt_json_input"] = ft.TextField(multiline=True, min_lines=20, expand=True, border=ft.InputBorder.NONE, bgcolor="#1E231E", text_size=14, text_style=ft.TextStyle(font_family="Consolas", height=1.5), on_change=sync_and_detect, content_padding=ft.padding.only(top=12, left=10, right=10, bottom=12))

            async def run_fmt_json(e):
                if await guard_busy(): return
                try:
                    parsed = json.loads(ui["txt_json_input"].value)
                    ui["txt_json_input"].value = json.dumps(parsed, indent=4, ensure_ascii=False)
                    await sync_and_detect(None)
                    await update_tree()
                    await show_toast("✅ Format & Updated View")
                except json.JSONDecodeError as ex:
                    err_line = ex.lineno; await show_toast(f"❌ Error บรรทัด {err_line}", False)
                    lines = ui["txt_json_input"].value.split('\n')
                    pos = sum(len(l) + 1 for l in lines[:err_line-1])
                    ui["txt_json_input"].focus(); ui["txt_json_input"].selection_start = pos; ui["txt_json_input"].selection_end = pos + len(lines[err_line-1])
                except Exception as ex: await show_toast(f"❌ Error: {ex}", False)
                await safe_update(ui["txt_json_input"])

            async def run_minify_json(e):
                if await guard_busy(): return
                try: 
                    ui["txt_json_input"].value = json.dumps(json.loads(ui["txt_json_input"].value), separators=(',', ':'), ensure_ascii=False)
                    await show_toast("✅ Minify สำเร็จ")
                    await update_tree()
                    await safe_update(ui["txt_json_input"])
                except Exception as ex: await show_toast(f"❌ Error: {ex}", False)

            async def run_b64_decode_json(e):
                if await guard_busy(): return
                try:
                    val = ui["txt_json_input"].value.strip()
                    decoded = base64.b64decode(val).decode('utf-8')
                    # Try to format it if it's JSON
                    try:
                        parsed = json.loads(decoded)
                        ui["txt_json_input"].value = json.dumps(parsed, indent=4, ensure_ascii=False)
                    except:
                        ui["txt_json_input"].value = decoded
                    await sync_and_detect(None)
                    await update_tree()
                    await show_toast("🔓 Decode สำเร็จ")
                    await safe_update(ui["txt_json_input"])
                except:
                    await show_toast("❌ ไม่ใช่ Base64 ที่ถูกต้อง", False)

            async def run_search_json(e):
                keyword = ui["txt_json_search"].value.strip()
                if not keyword: return
                try:
                    data = json.loads(ui["txt_json_input"].value)
                    results = search_json(data, keyword)
                    if results:
                        ui["tree_container"].controls.clear()
                        ui["tree_container"].controls.append(build_tree(data, highlighted_paths=results))
                        await show_toast(f"🔎 พบ {len(results)} จุด")
                    else:
                        await show_toast("🔍 ไม่พบข้อมูล", False)
                    await safe_update(ui["tree_container"])
                except:
                    await show_toast("❌ กรุณา Format JSON ก่อนค้นหา", False)

            async def run_clear_json(e): 
                ui["txt_json_input"].value = ""; ui["txt_line_numbers"].value = "1"; ui["tree_container"].controls.clear()
                await safe_update(ui["txt_json_input"]); await safe_update(ui["txt_line_numbers"]); await safe_update(ui["tree_container"])
            
            async def run_load_json_data(e): 
                ui["txt_json_input"].value = '{"requestId": "REQ-20260427-0001", "customer": {"id": "CUST-10001", "name": "John Doe"}, "items": [{"sku": "SKU-001", "qty": 2}]}'
                await run_fmt_json(None)

            async def run_json_to_csv(e):
                if await guard_busy(): return
                try:
                    data = json.loads(ui["txt_json_input"].value)
                    csv_text = json_to_csv_text(data)
                    if csv_text:
                        ui["txt_json_input"].value = csv_text
                        await sync_and_detect(None)
                        ui["tree_container"].controls.clear()
                        ui["tree_container"].controls.append(ft.Text("📊 แปลงเป็น CSV เรียบร้อยแล้ว (Tree View ไม่รองรับ CSV)", color="orange"))
                        await show_toast("📊 แปลงเป็น CSV สำเร็จ")
                    else:
                        await show_toast("❌ JSON ต้องเป็นรูปแบบ List หรือ Dict เท่านั้น", False)
                except Exception as ex:
                    await show_toast(f"❌ Error: {ex}", False)
                await safe_update(ui["txt_json_input"]); await safe_update(ui["tree_container"])

            async def run_csv_to_json(e):
                if await guard_busy(): return
                try:
                    csv_text = ui["txt_json_input"].value.strip()
                    data = csv_to_json_data(csv_text)
                    ui["txt_json_input"].value = json.dumps(data, indent=4, ensure_ascii=False)
                    await sync_and_detect(None)
                    await update_tree()
                    await show_toast("🧾 แปลงเป็น JSON สำเร็จ")
                except Exception as ex:
                    await show_toast(f"❌ Error: {ex}", False)
                await safe_update(ui["txt_json_input"])

            async def run_diff_json(e):
                txt_diff_2 = ft.TextField(label="วาง JSON ตัวที่สองเพื่อเปรียบเทียบ (JSON 2)", multiline=True, min_lines=10, border_color=COLOR_PRIMARY, bgcolor="#1E231E")
                
                async def do_compare(ev):
                    try:
                        obj1 = json.loads(ui["txt_json_input"].value)
                        obj2 = json.loads(txt_diff_2.value)
                        diffs = compare_json(obj1, obj2)
                        
                        ui["tree_container"].controls.clear()
                        if not diffs:
                            ui["tree_container"].controls.append(ft.Text("✅ JSON ทั้งสองชุดมีโครงสร้างและค่าเหมือนกัน!", color=COLOR_SECONDARY, weight="bold"))
                        else:
                            ui["tree_container"].controls.append(ft.Text(f"🔎 พบจุดที่ต่างกัน {len(diffs)} รายการ:", color=COLOR_ACCENT, weight="bold"))
                            for d in diffs:
                                ui["tree_container"].controls.append(ft.Text(f"• {d}", size=13))
                        
                        await safe_update(ui["tree_container"])
                        diff_dlg.open = False
                        await page.update_async()
                    except Exception as ex:
                        await show_toast(f"❌ Error: {ex}", False)

                diff_dlg = ft.AlertDialog(
                    title=ft.Text("🔍 JSON Diff Tool", weight="bold"),
                    content=ft.Container(content=txt_diff_2, width=600),
                    actions=[
                        ft.TextButton("เปรียบเทียบ", on_click=do_compare),
                        ft.TextButton("ยกเลิก", on_click=lambda _: setattr(diff_dlg, 'open', False) or page.update())
                    ]
                )
                page.dialog = diff_dlg
                diff_dlg.open = True
                await page.update_async()

            async def run_validate_json(e):
                val = ui["txt_json_input"].value.strip()
                if not val: return
                try:
                    data = json.loads(val)
                    # Basic Validation: Check if it's a list or dict
                    msg = "✅ JSON Valid!"
                    if isinstance(data, dict):
                        msg += f" (Object with {len(data)} keys)"
                    elif isinstance(data, list):
                        msg += f" (Array with {len(data)} items)"
                    
                    # Optional: Add mandatory key check if needed in future
                    await show_toast(msg)
                    await update_tree()
                except json.JSONDecodeError as ex:
                    await show_toast(f"❌ Invalid JSON: บรรทัด {ex.lineno}", False)
                except Exception as ex:
                    await show_toast(f"❌ Error: {ex}", False)

            async def btn_copy_json(e):
                if await guard_busy(): return
                if not ui["txt_json_input"].value: await show_toast("ไม่มีข้อมูล", False); return
                page.set_clipboard(ui["txt_json_input"].value); await show_toast("📋 คัดลอกแล้ว")

            actions["run_fmt_json"] = run_fmt_json; actions["run_minify_json"] = run_minify_json; actions["run_clear_json"] = run_clear_json; actions["run_load_json_data"] = run_load_json_data; actions["btn_copy_json"] = btn_copy_json
            actions["run_search_json"] = run_search_json; actions["run_b64_decode_json"] = run_b64_decode_json
            actions["run_json_to_csv"] = run_json_to_csv; actions["run_csv_to_json"] = run_csv_to_json
            actions["run_diff_json"] = run_diff_json; actions["run_validate_json"] = run_validate_json

        elif index == 4: # Binary Tool
            ui["txt_dec"] = ft.TextField(label="เลขฐาน 10 (Decimal)", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["lbl_bin"] = ft.Text("Binary: -", size=20, weight="bold", color=COLOR_PRIMARY)
            ui["lbl_sum"] = ft.Text("ผลรวม: 0", size=20, weight="bold", color=COLOR_SECONDARY)
            ui["lbl_sql_warn"] = ft.Text("⚠️ ตำแหน่งที่เห็นถ้าเทียบกับ SQL จะต้องนำไป +1 เสมอ", color=COLOR_ACCENT, italic=True)
            ui["col_breakdown"] = ft.Column(spacing=5); ui["box_breakdown"] = ft.Container(content=ui["col_breakdown"], border=ft.border.all(1, COLOR_SECONDARY), bgcolor="#181F18", padding=15, border_radius=10, visible=False)
            async def calc_from_dec(e):
                val = ui["txt_dec"].value.replace(",", "")
                if val.isdigit():
                    num = int(val); ui["lbl_bin"].value = f"Binary: {bin(num)[2:]}"; ui["col_breakdown"].controls.clear()
                    for i, bit in enumerate(reversed(bin(num)[2:])):
                        if bit == '1': ui["col_breakdown"].controls.append(ft.Text(f"Bit {i}   >   {2**i}", color=COLOR_TEXT, weight="bold"))
                    ui["lbl_sum"].value = f"ผลรวม: {num:,}"; ui["box_breakdown"].visible = True
                else: ui["lbl_bin"].value = "Binary: -"; ui["lbl_sum"].value = "ผลรวม: 0"; ui["box_breakdown"].visible = False
                await safe_update(ui["lbl_bin"])
                await safe_update(ui["lbl_sum"])
                await safe_update(ui["box_breakdown"])
            ui["txt_dec"].on_change = calc_from_dec

        elif index == 5: # Time Converter
            ui["txt_epoch"] = ft.TextField(label="Unix Epoch", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["lbl_epoch"] = ft.Text("Local Time: -", color=COLOR_SECONDARY)
            ui["txt_ticks"] = ft.TextField(label=".NET Ticks", border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["lbl_ticks"] = ft.Text("Local Time: -", color=COLOR_SECONDARY)
            async def conv_ep(e):
                val = ui["txt_epoch"].value.replace(",", "").strip()
                ui["lbl_epoch"].value = f"Local Time: {epoch_to_local_datetime_text(int(val))}" if val.isdigit() else "❌ กรุณากรอกตัวเลข"
                await safe_update(ui["lbl_epoch"])
            async def conv_tk(e):
                val = ui["txt_ticks"].value.replace(",", "").strip()
                ui["lbl_ticks"].value = f"Local Time: {ticks_to_local_datetime_text(int(val))}" if val.isdigit() else "❌ กรุณากรอกตัวเลข"
                await safe_update(ui["lbl_ticks"])
            async def ld_ex(e): 
                ui["txt_epoch"].value = "1714272000"; ui["txt_ticks"].value = "638498592000000000"; await show_toast("📋 โหลดตัวอย่างแล้ว")
                await safe_update(ui["txt_epoch"]); await safe_update(ui["txt_ticks"])
            async def ld_cur(e):
                now = datetime.now()
                now_utc = datetime.now(timezone.utc)
                ui["txt_epoch"].value = str(int(now.timestamp()))
                # Calculate UTC Ticks: (seconds since 1970 * 10^7) + ticks at 1970
                ticks = (int(now_utc.timestamp()) * 10_000_000) + 621355968000000000
                ui["txt_ticks"].value = str(int(ticks))
                await show_toast("🕒 ดึงเวลาปัจจุบันแล้ว")
                await safe_update(ui["txt_epoch"]); await safe_update(ui["txt_ticks"])
            async def clr_t(e): 
                ui["txt_epoch"].value = ""; ui["lbl_epoch"].value = "Local Time: -"; ui["txt_ticks"].value = ""; ui["lbl_ticks"].value = "Local Time: -"; await show_toast("🗑️ ล้างแล้ว")
                await safe_update(ui["txt_epoch"]); await safe_update(ui["lbl_epoch"]); await safe_update(ui["txt_ticks"]); await safe_update(ui["lbl_ticks"])
            actions["conv_epoch"] = conv_ep; actions["conv_ticks"] = conv_tk; actions["run_load_time_ex"] = ld_ex; actions["run_load_current_time"] = ld_cur; actions["run_clear_time"] = clr_t

        elif index == 6: # Base64
            ui["txt_b64"] = ft.TextField(label="ข้อความ / Base64", multiline=True, min_lines=5, border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            async def enc(e):
                try: 
                    ui["txt_b64"].value = base64.b64encode(ui["txt_b64"].value.encode('utf-8')).decode('utf-8')
                    await show_toast("สำเร็จ"); await safe_update(ui["txt_b64"])
                except Exception as ex: await show_toast(f"Error: {ex}", False)
            async def dec(e):
                try: 
                    ui["txt_b64"].value = base64.b64decode(ui["txt_b64"].value.encode('utf-8')).decode('utf-8')
                    await show_toast("สำเร็จ"); await safe_update(ui["txt_b64"])
                except: await show_toast("❌ ผิดพลาด", False)
            async def ld_b(e): 
                ui["txt_b64"].value = '{"user": "admin", "status": "active"}'; await show_toast("📋 โหลดตัวอย่างแล้ว")
                await safe_update(ui["txt_b64"])
            async def clr_b(e): 
                ui["txt_b64"].value = ""; await show_toast("🗑️ ล้างแล้ว")
                await safe_update(ui["txt_b64"])
            actions["run_b64_enc"] = enc; actions["run_b64_dec"] = dec; actions["run_load_b64_ex"] = ld_b; actions["run_clear_b64"] = clr_b

        elif index == 7: # Password Gen
            ui["lbl_pass_len"] = ft.Text("ความยาวรหัสผ่าน: 16", weight="bold", size=16)
            ui["slider_len"] = ft.Slider(min=8, max=64, divisions=56, value=16, label="{value}", active_color=COLOR_PRIMARY)
            ui["chk_upper"] = ft.Checkbox(label="A-Z", value=True, fill_color=COLOR_PRIMARY); ui["chk_lower"] = ft.Checkbox(label="a-z", value=True, fill_color=COLOR_PRIMARY)
            ui["chk_nums"] = ft.Checkbox(label="0-9", value=True, fill_color=COLOR_PRIMARY); ui["chk_syms"] = ft.Checkbox(label="!@#$", value=True, fill_color=COLOR_PRIMARY)
            ui["txt_pass_out"] = ft.TextField(label="รหัสผ่าน", read_only=True, border_color=COLOR_PRIMARY, bgcolor="#181C18", border_radius=12, text_size=24, text_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
            async def sl_ch(e): 
                ui["lbl_pass_len"].value = f"ความยาวรหัสผ่าน: {int(e.control.value)}"
                await safe_update(ui["lbl_pass_len"])
            ui["slider_len"].on_change = sl_ch
            async def gen(e):
                pwd = build_password(int(ui["slider_len"].value), ui["chk_upper"].value, ui["chk_lower"].value, ui["chk_nums"].value, ui["chk_syms"].value)
                ui["txt_pass_out"].value = pwd if pwd else "❌ เลือกรูปแบบด้วยครับ"
                await show_toast("สำเร็จ" if pwd else "พลาด", bool(pwd))
                await safe_update(ui["txt_pass_out"])
            async def cp_p(e): 
                if ui["txt_pass_out"].value:
                    page.set_clipboard(ui["txt_pass_out"].value); await show_toast("คัดลอกแล้ว")
            actions["run_gen_pass"] = gen; actions["btn_copy_pass"] = cp_p

        elif index == 8: # Hidden Char
            ui["txt_hidden_in"] = ft.TextField(label="วางข้อความ", multiline=True, expand=True, border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12, text_style=ft.TextStyle(font_family="Consolas"))
            ui["txt_hidden_out"] = ft.TextField(label="ผลลัพธ์", multiline=True, read_only=True, expand=True, border_color=COLOR_ACCENT, bgcolor="#181C18", border_radius=12)
            ui["lbl_hidden_file"] = ft.Text("โหมดไฟล์: ยังไม่ได้เลือกไฟล์", color="white54"); ui["view_highlight"] = ft.Text(spans=[], visible=False)
            ANOMALIES = {'\u200B': 'Zero-Width Space', '\u200C': 'Zero-Width Non-Joiner', '\u200D': 'Zero-Width Joiner', '\uFEFF': 'BOM', '\u00A0': 'Non-Breaking Space', '\u0000': 'Null', '\u0007': 'Bell', '\u0008': 'Backspace', '\u000B': 'Vertical Tab', '\u000C': 'Form Feed', '\u001F': 'Unit Separator'}
            c_buf = [None]

            async def op_h(e):
                current_fp_context[fp_open] = {"ui": ui["lbl_hidden_file"], "type": "open"}
                await fp_open.pick_files_async(allowed_extensions=["xlsx", "xls", "csv", "txt"])
                # The rest happens in on_fp_result but we need to disable input
                ui["txt_hidden_in"].value = ""; ui["txt_hidden_in"].disabled = True
                await safe_update(ui["txt_hidden_in"])

            async def cl_h(e): 
                ui["lbl_hidden_file"].value = "โหมดไฟล์: ยังไม่ได้เลือกไฟล์"; ui["lbl_hidden_file"].color = "white54"; ui["txt_hidden_in"].disabled = False; ui["txt_hidden_out"].value = ""
                await safe_update(ui["lbl_hidden_file"]); await safe_update(ui["txt_hidden_in"]); await safe_update(ui["txt_hidden_out"])
            
            async def run_chk(e):
                if await guard_busy(): return
                p = ui["lbl_hidden_file"].value
                if p != "โหมดไฟล์: ยังไม่ได้เลือกไฟล์" and os.path.exists(p):
                    cleaned_data, status_msg = process_hidden_char_file(p, ANOMALIES)
                    c_buf[0] = cleaned_data
                    ui["txt_hidden_out"].value = status_msg
                else:
                    text = ui["txt_hidden_in"].value
                    cnt = 0; rep = []
                    for c, d in ANOMALIES.items():
                        if c in text:
                            n = text.count(c); rep.append(f"📍 พบ {d}: {n}"); cnt += n
                    ui["txt_hidden_out"].value = f"🔎 พบ {cnt} แห่ง:\n" + "\n".join(rep) if cnt > 0 else "✅ สะอาด!"
                await safe_update(ui["txt_hidden_out"])

            async def run_vis(e):
                if not ui["txt_hidden_in"].value: return
                spans = []
                for char in ui["txt_hidden_in"].value:
                    if char in ANOMALIES: spans.append(ft.TextSpan("[!]", style=ft.TextStyle(color="red", weight="bold", bgcolor="yellow100")))
                    else: spans.append(ft.TextSpan(char, style=ft.TextStyle(color=COLOR_TEXT)))
                ui["view_highlight"].spans = spans; ui["view_highlight"].visible = True; ui["txt_hidden_in"].visible = False
                await safe_update(ui["view_highlight"]); await safe_update(ui["txt_hidden_in"])

            async def run_save(e):
                if c_buf[0] is None: return
                p = ui["lbl_hidden_file"].value
                try:
                    if p.endswith(('.xlsx', '.xls')): c_buf[0].to_excel(p, index=False)
                    elif p.endswith('.csv'): c_buf[0].to_csv(p, index=False, encoding='utf-8-sig')
                    else:
                        with open(p, 'w', encoding='utf-8') as f: f.write(c_buf[0])
                    await show_toast("✅ บันทึกทับแล้ว!"); c_buf[0] = None
                except Exception as ex: await show_toast(f"❌ พลาด: {ex}", False)

            async def run_clean(e):
                if await guard_busy() or not ui["txt_hidden_in"].value or ui["txt_hidden_in"].disabled: return
                ui["txt_hidden_in"].value = clean_hidden_text(ui["txt_hidden_in"].value, ANOMALIES)
                ui["txt_hidden_out"].value = "🧹 ล้างแล้ว!"
                await safe_update(ui["txt_hidden_in"]); await safe_update(ui["txt_hidden_out"])

            async def clr_all(e): 
                ui["txt_hidden_in"].value = ""; ui["txt_hidden_out"].value = ""; ui["view_highlight"].visible = False; ui["txt_hidden_in"].visible = True; ui["lbl_hidden_file"].value = "โหมดไฟล์: ยังไม่ได้เลือกไฟล์"
                await safe_update(ui["txt_hidden_in"]); await safe_update(ui["txt_hidden_out"]); await safe_update(ui["view_highlight"]); await safe_update(ui["lbl_hidden_file"])

            async def cp_h(e): 
                if ui["txt_hidden_in"].value:
                    page.set_clipboard(ui["txt_hidden_in"].value); await show_toast("คัดลอกแล้ว")

            actions["btn_open_hidden"] = op_h; actions["btn_clear_hidden"] = cl_h; actions["run_check_hidden"] = run_chk; actions["run_visual_check"] = run_vis; actions["run_save_replace_hidden"] = run_save; actions["run_clean_hidden"] = run_clean; actions["run_clear_hidden_all"] = clr_all; actions["btn_copy_clean"] = cp_h

        elif index == 9: # Smart Formatter
            ui["txt_fmt_ticket"] = ft.TextField(label="เลข Ticket", hint_text="12345", width=180, border_color=COLOR_PRIMARY, bgcolor="#181C18", border_radius=8, text_size=13)
            ui["txt_fmt_subject"] = ft.TextField(label="หัวข้อ (Subject)", hint_text="เช่น [BKK] ปัญหาการใช้งาน...", border_color=COLOR_PRIMARY, bgcolor="#181C18", border_radius=8, text_size=13)
            ui["txt_fmt_date"] = ft.TextField(label="วันที่", hint_text="เช่น 28/04/2026", width=180, border_color=COLOR_PRIMARY, bgcolor="#181C18", border_radius=8, text_size=13)
            ui["txt_fmt_input"] = ft.TextField(label="คำตอบจาก Support", multiline=True, min_lines=3, max_lines=3, border_color=COLOR_PRIMARY, bgcolor="#181C18", border_radius=8, text_size=13)
            ui["txt_fmt_res"] = ft.TextField(label="ผลลัพธ์ (Copy ไปใช้ได้เลย)", multiline=True, min_lines=8, max_lines=12, read_only=True, border_color=COLOR_SECONDARY, bgcolor="#0A0C0A", text_style=ft.TextStyle(size=14, font_family="Tahoma", height=1.5), content_padding=15)
            
            TMPS = {
                "1": "Dear Valued Customer,\n\nBuzzebees Application Support acknowledged your request and recorded it in our system already. Please see information below for reference.\n\nCase No. {ticket_no} Subject “{subject}”\n\nThis case is in the progress of investigation/assigning to specialist at the moment. Our specialist will contact you with in 3-5 days.\n\nYours sincerely,\nBuzzebees Application Support\nEmail: app-support@buzzebees.com",
                "2": "ตามที่เราได้ขอข้อมูลเพิ่มเติมเกี่ยวกับ TicketID {ticket_no} เมื่อวันที่ {date} เพื่อดำเนินการแก้ไขปัญหาให้เสร็จสมบูรณ์ ขณะนี้ทางเรายังไม่ได้รับการตอบกลับจากท่านค่ะ\n\nรบกวนขอความกรุณาส่งข้อมูลภายใน 1 วัน ทำการเพื่อให้เราสามารถดำเนินการต่อได้ หากไม่มีการตอบกลับภายในเวลาที่กำหนด เคสนี้จะถูกปิดโดยอัตโนมัติ และท่านสามารถแจ้งเปิดเคสใหม่ได้เมื่อต้องการความช่วยเหลือ\n\nขอขอบคุณสำหรับความร่วมมือของท่าน",
                "3": "สำหรับการแจ้งปัญหาในครั้งถัดไป สามารถส่งรายละเอียดมาที่อีเมล\napplication-support@buzzebees.com และ app-support@buzzebees.com ได้เลยนะคะ\n\nเพื่อให้การตรวจสอบเป็นไปอย่างรวดเร็วและครบถ้วน รบกวนช่วยตรวจสอบข้อมูลดังนี้ค่ะ\n\nหัวข้ออีเมล (Subject) กรุณาไม่ใช้คำว่า Re, FWD หรือ FW นำหน้า\nรบกวนระบุรายละเอียดและข้อมูลให้ครบถ้วนตามเงื่อนไขที่กำหนด เพื่อป้องกันข้อมูลตกหล่นในการตรวจสอบปัญหา\n\nขอขอบคุณสำหรับความร่วมมือเป็นอย่างดีค่ะ",
                "4": "ขอความกรุณาให้คุณลูกค้าช่วยยืนยันกลับมาว่าการดำเนินการเสร็จสมบูรณ์แล้ว ภายในระยะเวลาไม่เกิน 1 วันทำการ เพื่อให้เราสามารถรับทราบถึงการแก้ไขปัญหาและปิดเคสได้ค่ะ\n\nขอบพระคุณค่ะ",
                "5": "ในครั้งต่อไปรบกวนแจ้งเข้ามาทาง Help Center ได้เลยค่ะ หรือสามารถแจ้งปัญหามาที่อีเมล์ app-support@buzzebees.com,application-support@buzzebees.com ค่ะ หากเร่งด่วนสามารถแจ้งเลขเคสเพื่อตรวจสอบด่วนได้เลยค่ะ เนื่องจากในการปฏิบัติงานจะต้องมีการเก็บ Log การทำงานไว้ทุกครั้งค่ะ ทางทีมจำเป็นต้องขอเลขใบงานเพื่อแจ้งทีมดำเนินการตรวจสอบค่ะ ขอบคุณค่ะ",
                "6": "เพื่อความสะดวกรวดเร็วในการติดตามเคส และเป็นไปตาม Policy ของบริษัท\nรบกวนทางคุณลูกค้าแจ้งปัญหาเข้ามาที่อีเมล์ app-support@buzzebees.com,application-support@buzzebees.com\n\nแล้วทางเราจะรีบแจ้งทีมช่วยตรวจสอบเพิ่มเติมให้ค่ะ",
                "7": "ทางทีมได้รับ Ticket : {ticket_no} แล้วเรียบร้อยค่ะ อย่างไรก็ตามทางทีมจะเร่งประสานงานตรวจสอบให้ ตามรายละเอียดที่ได้รับ หากมีความคืบหน้าอย่างไรทางทีมจะแจ้งให้ทราบอีกครั้งค่ะ"
            }

            async def apply_template(e):
                t_id = e.control.data
                ticket = ui["txt_fmt_ticket"].value.strip()
                subject = ui["txt_fmt_subject"].value.strip()
                date_val = ui["txt_fmt_date"].value.strip()
                
                try:
                    if t_id == "1":
                        if not ticket or not subject:
                            await show_toast("⚠️ กรุณากรอก Ticket No. และ Subject", False); return
                        ui["txt_fmt_res"].value = TMPS["1"].format(ticket_no=ticket, subject=subject)
                    elif t_id == "2":
                        if not ticket or not date_val:
                            await show_toast("⚠️ กรุณากรอก Ticket No. และ วันที่", False); return
                        ui["txt_fmt_res"].value = TMPS["2"].format(ticket_no=ticket, date=date_val)
                    elif t_id == "7":
                        if not ticket:
                            await show_toast("⚠️ กรุณากรอก Ticket No.", False); return
                        ui["txt_fmt_res"].value = TMPS["7"].format(ticket_no=ticket)
                    else:
                        ui["txt_fmt_res"].value = TMPS[t_id]
                    
                    await safe_update(ui["txt_fmt_res"])
                    await show_toast(f"✅ ใช้ Template #{t_id}")
                except Exception as ex:
                    await show_toast(f"❌ Template Error: {ex}", False)

            async def copy_output(e):
                if not ui["txt_fmt_res"].value: return
                page.set_clipboard(ui["txt_fmt_res"].value)
                await show_toast("📋 คัดลอกแล้ว")

            async def clear_fields(e):
                ui["txt_fmt_ticket"].value = ""; ui["txt_fmt_subject"].value = ""; ui["txt_fmt_date"].value = ""
                ui["txt_fmt_input"].value = ""; ui["txt_fmt_res"].value = ""
                await safe_update(ui["txt_fmt_ticket"]); await safe_update(ui["txt_fmt_subject"])
                await safe_update(ui["txt_fmt_date"]); await safe_update(ui["txt_fmt_input"])
                await safe_update(ui["txt_fmt_res"])

            async def format_custom(e):
                ans = ui["txt_fmt_input"].value.strip()
                if not ans: return
                ui["txt_fmt_res"].value = f"เรียน ทีมที่เกี่ยวข้อง\n\n          {ans}\n\nขอบคุณค่ะ"
                await safe_update(ui["txt_fmt_res"])
                await show_toast("📧 จัดรูปแบบคำตอบแล้ว")

            actions["apply_fmt"] = apply_template; actions["btn_copy_fmt"] = copy_output; actions["run_clear_fmt"] = clear_fields; actions["run_format_email"] = format_custom

        elif index == 10: # Bit Finder
            ui["txt_bin_in"] = ft.TextField(label="วางชุดตัวเลข (เช่น 010100001)", multiline=True, expand=True, border_color=COLOR_PRIMARY, bgcolor="#252B25", border_radius=12)
            ui["txt_bin_out"] = ft.TextField(label="ตำแหน่งของ 1 (เริ่มนับที่ 1 จากซ้ายไปขวา)", multiline=True, read_only=True, expand=True, border_color=COLOR_ACCENT, bgcolor="#181C18", border_radius=12)
            ui["txt_sql_out"] = ft.TextField(label="SQL Query", multiline=True, read_only=True, expand=True, border_color=COLOR_SECONDARY, bgcolor="#181C18", border_radius=12)
            ui["lbl_bin_count"] = ft.Text("พบเลข 1 จำนวน: 0 จุด", color="white54")

            async def run_find_bits(e):
                if not ui["txt_bin_in"].value: return
                val = ui["txt_bin_in"].value.strip().replace(" ", "").replace("\n", "").replace("\r", "")
                indices = find_binary_indices(val)
                
                if indices:
                    idx_str = ", ".join(map(str, indices))
                    ui["txt_bin_out"].value = idx_str
                    ui["txt_sql_out"].value = f"select AppName,VisibilityPosition from SponsorApps where VisibilityPosition in ({idx_str})"
                else:
                    ui["txt_bin_out"].value = "ไม่พบเลข 1"
                    ui["txt_sql_out"].value = ""
                
                ui["lbl_bin_count"].value = f"พบเลข 1 จำนวน: {len(indices)} จุด"
                await safe_update(ui["txt_bin_out"])
                await safe_update(ui["txt_sql_out"])
                await safe_update(ui["lbl_bin_count"])

            async def clr_bin(e):
                ui["txt_bin_in"].value = ""; ui["txt_bin_out"].value = ""; ui["txt_sql_out"].value = ""; ui["lbl_bin_count"].value = "พบเลข 1 จำนวน: 0 จุด"
                await safe_update(ui["txt_bin_in"]); await safe_update(ui["txt_bin_out"]); await safe_update(ui["txt_sql_out"]); await safe_update(ui["lbl_bin_count"])

            async def cp_bin(e):
                if ui["txt_bin_out"].value and ui["txt_bin_out"].value != "ไม่พบเลข 1":
                    page.set_clipboard(ui["txt_bin_out"].value); await show_toast("📋 คัดลอกตำแหน่งแล้ว")

            async def cp_sql(e):
                if ui["txt_sql_out"].value:
                    page.set_clipboard(ui["txt_sql_out"].value); await show_toast("📋 คัดลอก SQL แล้ว")

            actions["run_find_bits"] = run_find_bits; actions["run_clear_bits"] = clr_bin; actions["btn_copy_bits"] = cp_bin; actions["btn_copy_sql"] = cp_sql

        elif index == 11: # Compare Text
            ui["txt_compare_1"] = ft.TextField(label="ข้อความเดิม (Original)", multiline=True, min_lines=10, border_color=COLOR_PRIMARY, bgcolor="#1E231E", text_size=13)
            ui["txt_compare_2"] = ft.TextField(label="ข้อความใหม่ (Changed)", multiline=True, min_lines=10, border_color=COLOR_SECONDARY, bgcolor="#1E231E", text_size=13)
            ui["col_diff_main"] = ft.ListView(expand=True, spacing=1)

            async def run_compare_text(e):
                if await guard_busy(): return
                t1, t2 = ui["txt_compare_1"].value, ui["txt_compare_2"].value
                if not t1 and not t2: await show_toast("⚠️ กรุณากรอกข้อความก่อน", False); return
                
                try:
                    diff = get_text_diff(t1, t2)
                    ui["col_diff_main"].controls.clear()
                    
                    if not diff:
                        ui["col_diff_main"].controls.append(ft.Text("✅ ข้อมูลเหมือนกันทุกประการ", color=COLOR_SECONDARY, weight="bold", text_align=ft.TextAlign.CENTER))
                    else:
                        ln_left = 1
                        ln_right = 1
                        for line in diff:
                            tag = line[:2]
                            content = line[2:]
                            
                            l_num = " "
                            r_num = " "
                            l_text = " "
                            r_text = " "
                            l_bg = COLOR_TRANSPARENT
                            r_bg = COLOR_TRANSPARENT
                            l_color = "white54"
                            r_color = "white54"
                            ln_l_color = "white24"
                            ln_r_color = "white24"

                            if tag == "  ": # Unchanged
                                l_num = str(ln_left); r_num = str(ln_right)
                                l_text = r_text = content
                                ln_left += 1; ln_right += 1
                            elif tag == "- ": # Removed from Left
                                l_num = str(ln_left); l_text = content
                                l_bg = "#2E1A1A"; l_color = COLOR_RED_400; ln_l_color = "red400"
                                ln_left += 1
                            elif tag == "+ ": # Added to Right
                                r_num = str(ln_right); r_text = content
                                r_bg = "#1A2E1A"; r_color = COLOR_GREEN_400; ln_r_color = "green400"
                                ln_right += 1
                            elif tag == "? ": 
                                continue

                            # Create aligned row for this diff line
                            ui["col_diff_main"].controls.append(
                                ft.Row([
                                    # Left Side
                                    ft.Text(l_num, color=ln_l_color, font_family="Consolas", size=12, text_align=ft.TextAlign.RIGHT, width=35),
                                    ft.Container(content=ft.Text(l_text, color=l_color, font_family="Consolas", size=13), bgcolor=l_bg, expand=True, padding=ft.padding.only(left=5)),
                                    ft.VerticalDivider(width=1, color="white10"),
                                    # Right Side
                                    ft.Text(r_num, color=ln_r_color, font_family="Consolas", size=12, text_align=ft.TextAlign.RIGHT, width=35),
                                    ft.Container(content=ft.Text(r_text, color=r_color, font_family="Consolas", size=13), bgcolor=r_bg, expand=True, padding=ft.padding.only(left=5)),
                                ], spacing=5, vertical_alignment=ft.CrossAxisAlignment.START)
                            )
                    
                    await show_toast("🔍 เปรียบเทียบเสร็จสิ้น")
                    await safe_update(ui["col_diff_main"])
                except Exception as ex:
                    await show_toast(f"❌ Error: {ex}", False)

            async def run_clear_compare(e):
                ui["txt_compare_1"].value = ""; ui["txt_compare_2"].value = ""; ui["col_diff_main"].controls.clear()
                await safe_update(ui["txt_compare_1"]); await safe_update(ui["txt_compare_2"]); await safe_update(ui["col_diff_main"])
            
            actions["run_compare_text"] = run_compare_text; actions["run_clear_compare"] = run_clear_compare

        ui_cache[index] = ui; actions_cache[index] = actions
        return ui, actions

    # --- 🏗️ View Builder ---
    content_area = ft.Column(expand=True)
    
    # Load Patchnotes from local version.json
    try:
        with open("version.json", "r", encoding="utf-8") as f:
            v_data = json.load(f)
            CURRENT_PATCH_NOTES = v_data.get("change_log", "")
    except:
        CURRENT_PATCH_NOTES = ""

    async def update_view(index):
        content_area.controls.clear(); ui, actions = await get_tool_assets(index)
        view = build_tool_view(index, ui, actions, current_version=CURRENT_VERSION, patch_notes=CURRENT_PATCH_NOTES)
        if isinstance(view, ft.Container): view.expand = True
        content_area.controls.append(view); await page.update_async()

    # --- 🧭 Sidebar Navigation ---
    def make_nav(idx):
        async def on_nav(e):
            if await guard_busy(): return
            await update_view(idx)
        return on_nav

    nav_home = nav_btn(" Home", "🏠", make_nav(0))
    nav_merge = nav_btn(" Merge & Split", "🗂️", make_nav(1))
    nav_qr = nav_btn(" QR Generator", "🔳", make_nav(2))
    nav_json = nav_btn(" JSON Tool", "🧾", make_nav(3))
    nav_binary = nav_btn(" Binary Tool", "🧮", make_nav(4))
    nav_time = nav_btn(" Time Converter", "⏱️", make_nav(5))
    nav_b64 = nav_btn(" Base64 Tool", "🔐", make_nav(6))
    nav_pass = nav_btn(" Password Gen", "🔑", make_nav(7))
    nav_hidden = nav_btn(" Hidden Char Check", "🕵️", make_nav(8))
    nav_fmt = nav_btn(" Smart Formatter", "📝", make_nav(9))
    nav_bit_finder = nav_btn(" Bit Finder", "🔍", make_nav(10))
    nav_compare = nav_btn(" Compare Text", "🎭", make_nav(11))
    nav_jwt = nav_btn(" JWT Decoder", "🔐", make_nav(12))
    nav_img = nav_btn(" Image Optimizer", "🖼️", make_nav(13))
    nav_controls.extend([nav_home, nav_merge, nav_qr, nav_json, nav_binary, nav_time, nav_b64, nav_pass, nav_hidden, nav_fmt, nav_bit_finder, nav_compare, nav_jwt, nav_img])
    nav_labels = [
        (nav_home, " Home", "Home"),
        (nav_merge, " Merge & Split", "Merge"),
        (nav_qr, " QR Generator", "QR"),
        (nav_json, " JSON Tool", "JSON"),
        (nav_binary, " Binary Tool", "Binary"),
        (nav_time, " Time Converter", "Time"),
        (nav_b64, " Base64 Tool", "Base64"),
        (nav_pass, " Password Gen", "Password"),
        (nav_hidden, " Hidden Char Check", "Hidden"),
        (nav_fmt, " Smart Formatter", "Formatter"),
        (nav_bit_finder, " Bit Finder", "Bits"),
        (nav_compare, " Compare Text", "Compare"),
        (nav_jwt, " JWT Decoder", "JWT"),
        (nav_img, " Image Optimizer", "Image"),
    ]

    sidebar = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Text("🛠️", size=40, color=COLOR_PRIMARY),
                    ft.Column([
                        ft.Text("KhawOat", size=18, weight="bold", color=COLOR_TEXT),
                        ft.Text("Multi-Tools Pro", size=12, color=COLOR_PRIMARY),
                        ft.Text(f"v{CURRENT_VERSION}", size=10, color=COLOR_TEXT_DIM),
                    ], spacing=0)
                ]),
                padding=ft.padding.only(bottom=30, top=10)
            ),
            nav_home,
            ft.Divider(color=BORDER_SUBTLE, height=40),
            ft.Column([
                nav_merge, nav_qr, nav_json, nav_binary, nav_time, 
                nav_b64, nav_pass, nav_hidden, nav_fmt, 
                nav_bit_finder, nav_compare, nav_jwt, nav_img
            ], spacing=2, scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=0),
        width=300,
        bgcolor=COLOR_SIDEBAR,
        padding=20,
    )

    async def apply_responsive_layout():
        width = page.width or page.window_width or 1280
        compact = width < RESPONSIVE_THRESHOLD
        sidebar.width = 220 if compact else 300
        sidebar.padding = 12 if compact else 20
        for button, full_label, compact_label in nav_labels:
            label_control = button.content.controls[1]
            label_control.value = compact_label if compact else full_label
            label_control.size = 12 if compact else 14
        await safe_update(sidebar)

    async def handle_resize(e):
        await apply_responsive_layout()

    page.on_resize = handle_resize
    
    page.add(ft.Row([sidebar, ft.Container(content=content_area, expand=True)], expand=True, spacing=0, vertical_alignment=ft.CrossAxisAlignment.STRETCH))
    
    await apply_responsive_layout()
    await update_view(0)
    init_end_time = time.time(); print(f"Lazy Initialization took: {init_end_time - init_start_time:.4f}s")
    
    async def update_clock():
        while True:
            lbl_clock.value = datetime.now().strftime("%H:%M:%S")
            try: await safe_update(lbl_clock)
            except: break
            await asyncio.sleep(1)
    page.run_task(update_clock)

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
