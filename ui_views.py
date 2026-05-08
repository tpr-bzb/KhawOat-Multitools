import flet as ft
from ui_config import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_CARD,
    COLOR_PANEL,
    COLOR_PANEL_ALT,
    COLOR_SURFACE,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TEXT,
    COLOR_TEXT_DIM,
    COLOR_ERROR,
    COLOR_SUCCESS,
    RADIUS_SM,
    RADIUS_MD,
    RADIUS_LG,
    SPACE_MD,
    SPACE_LG,
    FONT_SIZE_H2,
    FONT_SIZE_H3,
    FONT_SIZE_BODY,
    FONT_SIZE_SMALL,
    FONT_SIZE_TINY,
    BORDER_SUBTLE
)

# --- 🚀 Compatibility Helper for Flet Versions ---
STATE_CLASS = getattr(ft, "ControlState", getattr(ft, "MaterialState", None))
COLORS = getattr(ft, "colors", getattr(ft, "Colors", None))
TRANSPARENT = getattr(COLORS, "TRANSPARENT", "transparent")

def section_title(text: str, icon_text: str):
    return ft.Column([
        ft.Row([
            ft.Text(icon_text, size=30),
            ft.Text(text, size=FONT_SIZE_H2, weight="bold", color=COLOR_PRIMARY)
        ], spacing=15),
        ft.Container(height=3, width=60, bgcolor=COLOR_ACCENT, border_radius=5)
    ], spacing=5)


def panel(content, padding=SPACE_MD, bgcolor=COLOR_PANEL, expand=False, height=None):
    return ft.Container(
        content=content,
        padding=padding,
        bgcolor=bgcolor,
        border_radius=RADIUS_LG,
        border=ft.border.all(1, BORDER_SUBTLE),
        expand=expand,
        height=height,
    )


def badge(text: str, tone: str = "default"):
    bgcolor = "white08"
    color = COLOR_TEXT_DIM
    if tone == "accent":
        bgcolor = COLOR_ACCENT
        color = COLOR_BG
    elif tone == "primary":
        bgcolor = COLOR_PRIMARY
        color = COLOR_BG
    elif tone == "soft":
        bgcolor = "white10"
        color = COLOR_TEXT
    return ft.Container(
        content=ft.Text(text, size=FONT_SIZE_TINY, color=color, weight="w600"),
        padding=ft.padding.symmetric(horizontal=10, vertical=6),
        bgcolor=bgcolor,
        border_radius=999,
    )


def info_stat(label: str, value: str, icon: str, accent=COLOR_PRIMARY):
    return panel(
        ft.Row([
            ft.Container(
                content=ft.Text(icon, size=18),
                width=42,
                height=42,
                alignment=getattr(ft.alignment, "center", ft.alignment.center_left),
                bgcolor="white08",
                border_radius=12,
            ),
            ft.Column([
                ft.Text(label, size=FONT_SIZE_TINY, color=COLOR_TEXT_DIM),
                ft.Text(value, size=FONT_SIZE_BODY, weight="bold", color=accent),
            ], spacing=2, expand=True),
        ], spacing=12),
        padding=14,
        bgcolor=COLOR_PANEL_ALT,
        expand=True,
    )

def nav_btn(text: str, icon_text: str, on_click):
    return ft.TextButton(
        content=ft.Row([
            ft.Container(content=ft.Text(icon_text, size=18), width=30),
            ft.Text(text, size=FONT_SIZE_BODY, weight="w500", color=COLOR_TEXT)
        ], spacing=10),
        on_click=on_click,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=RADIUS_SM),
            overlay_color={
                STATE_CLASS.HOVERED: "white10",
                STATE_CLASS.DEFAULT: TRANSPARENT,
            } if STATE_CLASS else "white10",
            padding=ft.padding.symmetric(vertical=15, horizontal=15)
        )
    )

def build_tool_view(index: int, ui: dict, actions: dict, current_version: str = "1.0", patch_notes: str = ""):
    # Standard Card Wrapper for consistency
    def card_container(content, expand=True):
        return ft.Container(
            content=content,
            padding=SPACE_LG,
            bgcolor=COLOR_CARD,
            border_radius=ft.border_radius.only(top_left=RADIUS_LG) if index != 0 else 0,
            expand=expand,
            border=ft.border.all(1, BORDER_SUBTLE) if index != 0 else None,
            margin=ft.margin.only(left=2) if index != 0 else 0 # Prevent border overlap with sidebar
        )

    # --- 🏠 0. Welcome / Dashboard Page ---
    if index == 0:
        def quick_tool_card(title, icon, desc, idx):
            def on_hover(e):
                e.control.scale = 1.02 if e.data == "true" else 1.0
                e.control.border = ft.border.all(2, COLOR_PRIMARY) if e.data == "true" else ft.border.all(1, BORDER_SUBTLE)
                e.control.bgcolor = COLOR_PANEL_ALT if e.data == "true" else COLOR_PANEL
                e.control.update()

            return ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text(icon, size=22),
                        width=42,
                        height=42,
                        alignment=getattr(ft.alignment, "center", ft.alignment.center_left),
                        bgcolor="white08",
                        border_radius=12,
                    ),
                    ft.Text(title, size=13, weight="bold", color=COLOR_TEXT, text_align=ft.TextAlign.CENTER),
                    ft.Text(desc, size=10, color=COLOR_TEXT_DIM, text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                bgcolor=COLOR_PANEL,
                padding=14,
                border_radius=RADIUS_LG,
                border=ft.border.all(1, BORDER_SUBTLE),
                on_click=actions["nav_tool"],
                on_hover=on_hover,
                data=str(idx),
                width=158,
                height=132,
                animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE),
            )

        return ft.Container(
            content=ft.Column([
                # Hero Header
                panel(
                    ft.Column([
                        ft.Row([
                            badge("Modern Midnight Workspace", tone="soft"),
                            badge(f"Version {current_version}", tone="accent"),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([
                            ft.Column([
                                ft.Text("ศูนย์บัญชาการเครื่องมือประจำวัน", size=FONT_SIZE_SMALL, color=COLOR_SECONDARY, weight="bold"),
                                ft.Text(ui["greeting_text"], size=32, weight="bold", color=COLOR_TEXT),
                                ft.Text(
                                    "พื้นที่รวมเครื่องมือสำหรับงาน support, data cleanup, conversion และ quick diagnostics ในหน้าตาเดียว",
                                    size=FONT_SIZE_BODY,
                                    color=COLOR_TEXT_DIM,
                                ),
                            ], spacing=8, expand=True),
                            panel(
                                ft.Column([
                                    ft.Text("LOCAL TIME", size=FONT_SIZE_TINY, color=COLOR_TEXT_DIM, weight="bold"),
                                    ui["lbl_clock"],
                                    ft.Text("พร้อมใช้งานทันที", size=FONT_SIZE_TINY, color=COLOR_SECONDARY),
                                ], spacing=4, horizontal_alignment=ft.CrossAxisAlignment.END),
                                padding=18,
                                bgcolor=COLOR_PANEL_ALT,
                            ),
                        ], spacing=20, alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Row([
                            info_stat("Health", "Stable", "🛡️"),
                            info_stat("Update Mode", "Patch-ready", "⚙️", accent=COLOR_SECONDARY),
                            info_stat("Workspace", "14 tools live", "🧰", accent=COLOR_ACCENT),
                        ], spacing=15),
                    ], spacing=18),
                    padding=24,
                    bgcolor=COLOR_SURFACE,
                ),

                # Quick Access Section
                ft.Row([
                    ft.Text("🚀 Quick Access Tools", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                    ft.Text("คลิกเพื่อเปิดเครื่องมือที่ใช้บ่อยที่สุด", size=FONT_SIZE_SMALL, color=COLOR_TEXT_DIM),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Column([
                    ft.Row([
                        quick_tool_card("JSON Tool", "🧾", "Format & Validate", 3),
                        quick_tool_card("QR GEN", "🔳", "Create & Save QR", 2),
                        quick_tool_card("Password Gen", "🔑", "Secure Generator", 7),
                    ], spacing=15, alignment=ft.MainAxisAlignment.START),
                    ft.Row([
                        quick_tool_card("Time Converter", "⏱️", "Unix & Ticks", 5),
                        quick_tool_card("Binary Tools", "🧮", "Base Calculation", 4),
                    ], spacing=15, alignment=ft.MainAxisAlignment.START),
                ], spacing=15),

                # Middle Banner (GIF + Stats)
                ft.Row([
                    panel(
                        ft.Image(src=ui["greeting_gif"], width=190, height=150, fit=ft.ImageFit.CONTAIN),
                        bgcolor=COLOR_PANEL_ALT,
                        expand=True,
                        height=220,
                    ),
                    panel(
                        ft.Column([
                            ft.Text("Operation Snapshot", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                            ft.Text("ตัวแอปพร้อมสำหรับงาน quick utility และ support workflow ที่ต้องการความเร็ว", size=FONT_SIZE_SMALL, color=COLOR_TEXT_DIM),
                            ft.Row([
                                badge("Streaming file split", tone="primary"),
                                badge("JWT inspection", tone="soft"),
                                badge("Diff & compare", tone="soft"),
                            ], spacing=10, scroll=ft.ScrollMode.AUTO),
                            ft.Divider(color=BORDER_SUBTLE, height=18),
                            ft.Text("แนะนำ: เริ่มจาก Quick Access ด้านบนเพื่อเข้าเครื่องมือที่ใช้บ่อยที่สุด", size=FONT_SIZE_BODY, color=COLOR_TEXT),
                        ], spacing=12),
                        bgcolor=COLOR_PANEL,
                        expand=True,
                        height=220,
                    ),
                ], spacing=20),

                # Patchnotes / Latest Update Section
                panel(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.NEW_RELEASES, color=COLOR_ACCENT, size=20),
                            ft.Text("Latest Updates / Patch Notes", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ], spacing=10),
                        ft.Text(patch_notes or "No patch notes available.", size=FONT_SIZE_BODY, color=COLOR_TEXT_DIM, italic=True),
                    ], spacing=10),
                    bgcolor=COLOR_PANEL,
                ),

                # Bottom Status Cards
                ft.Row([
                    info_stat("Tool Count", "14 Active Tools", "🧩", accent=COLOR_ACCENT),
                    info_stat("Auto-Update", "Manifest-backed", "🔄", accent=COLOR_SECONDARY),
                ], spacing=20),

            ], scroll=ft.ScrollMode.AUTO, expand=True, spacing=10),
            padding=30, 
            bgcolor=COLOR_CARD, 
            border_radius=ft.border_radius.only(top_left=RADIUS_LG),
            expand=True,
            border=ft.Border(left=ft.BorderSide(1, BORDER_SUBTLE), top=ft.BorderSide(1, BORDER_SUBTLE))
        )


    # --- 🗂️ 1. Merge & Split ---
    if index == 1:
        return card_container(ft.Column([
            section_title("Merge & Split File", "🗂️"),
            ft.Text("💡 จัดการไฟล์ขนาดใหญ่ด้วยระบบ Streaming เพื่อประสิทธิภาพสูงสุด", color=COLOR_TEXT_DIM),
            
            ft.Container(
                content=ft.Column([
                    ft.Row([
                        ui["txt_src_dir"],
                        ft.ElevatedButton(
                            "เลือกโฟลเดอร์",
                            icon=ft.icons.FOLDER,
                            on_click=actions["btn_open_src"],
                            bgcolor=COLOR_SECONDARY,
                            color="black",
                        ),
                    ], spacing=SPACE_MD),
                    ft.Row([
                        ui["dd_src_ext"],
                        ui["dd_out_ext"],
                    ], spacing=SPACE_MD),
                    ft.Row([
                        ui["txt_base_name"],
                    ], spacing=SPACE_MD),
                    ft.Row([
                        ui["txt_lines"],
                        ui["chk_header"],
                    ], spacing=SPACE_MD),
                ], spacing=SPACE_MD),
                padding=SPACE_MD, bgcolor=COLOR_SURFACE, border_radius=RADIUS_MD, border=ft.border.all(1, BORDER_SUBTLE)
            ),
            
            ft.Row([
                ft.ElevatedButton(
                    "🚀 เริ่มประมวลผลไฟล์",
                    on_click=actions["run_split"],
                    bgcolor=COLOR_ACCENT,
                    color=COLOR_BG,
                    height=55,
                    expand=True,
                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=RADIUS_SM)),
                )
            ]),
            
            ft.Column([ui["lbl_split_status"], ui["lbl_split_summary"]], spacing=5)
        ], spacing=SPACE_LG, scroll=ft.ScrollMode.AUTO, expand=True))

    # --- 🔳 2. QR Generator ---
    if index == 2:
        return card_container(ft.Column([
            section_title("QR Generator", "🔳"),
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("สร้าง QR พร้อมใช้งานทันที", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("รองรับข้อความทั่วไปและลิงก์ พร้อมปุ่มบันทึกภาพในหน้าเดียว", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    badge("PNG ready", tone="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            panel(
                content=ft.Column([
                    ui["txt_qr"],
                    ft.Row([
                        ft.ElevatedButton("Generate QR", icon=ft.icons.PLAY_ARROW, on_click=actions["run_gen_qr"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=45, expand=True),
                        ft.ElevatedButton("Save Image", icon=ft.icons.SAVE, on_click=actions["btn_save_qr"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=45, expand=True),
                    ], spacing=15),
                ], spacing=SPACE_MD),
                bgcolor=COLOR_PANEL,
            ),
            
            ui["lbl_qr_status"],
            panel(ui["qr_container"], bgcolor=COLOR_PANEL_ALT), # Use the container defined in main.py
        ], spacing=SPACE_LG, scroll=ft.ScrollMode.AUTO))

    # --- 🧾 3. JSON Tool ---
    if index == 3:
        ui["txt_json_search"] = ft.TextField(
            label="Search nodes...", prefix_icon=ft.icons.SEARCH,
            text_size=14, height=45, border_color=COLOR_PRIMARY, bgcolor=COLOR_SURFACE, border_radius=RADIUS_SM,
            expand=True, on_submit=actions.get("run_search_json")
        )

        return card_container(ft.Column([
            section_title("JSON Viewer Pro", "🧾"),
            
            ft.Row([
                ui["txt_json_search"],
                ft.ElevatedButton("Search", on_click=actions.get("run_search_json"), bgcolor=COLOR_PRIMARY, color="black", height=45)
            ], spacing=10),

            ft.Container(
                content=ft.Row([
                    ft.IconButton(ft.icons.COPY, on_click=actions["btn_copy_json"], tooltip="Copy"),
                    ft.IconButton(ft.icons.FORMAT_ALIGN_LEFT, on_click=actions["run_fmt_json"], tooltip="Format"),
                    ft.IconButton(ft.icons.COMPRESS, on_click=actions["run_minify_json"], tooltip="Minify"),
                    ft.IconButton(ft.icons.UNARCHIVE, on_click=actions.get("run_b64_decode_json"), tooltip="B64 Decode"),
                    ft.VerticalDivider(color=BORDER_SUBTLE),
                    ft.TextButton("JSON ➔ CSV", icon=ft.icons.TABLE_VIEW, on_click=actions.get("run_json_to_csv")),
                    ft.TextButton("CSV ➔ JSON", icon=ft.icons.DATA_OBJECT, on_click=actions.get("run_csv_to_json")),
                    ft.VerticalDivider(color=BORDER_SUBTLE),
                    ft.IconButton(ft.icons.COMPARE_ARROWS, on_click=actions.get("run_diff_json"), tooltip="Diff", icon_color=COLOR_ACCENT),
                    ft.IconButton(ft.icons.RULE, on_click=actions.get("run_validate_json"), tooltip="Validate", icon_color=COLOR_SUCCESS),
                    ft.VerticalDivider(color=BORDER_SUBTLE),
                    ft.IconButton(ft.icons.DELETE_OUTLINE, on_click=actions["run_clear_json"], tooltip="Clear", icon_color=COLOR_ERROR),
                    ft.IconButton(ft.icons.FILE_DOWNLOAD, on_click=actions["run_load_json_data"], tooltip="Demo"),
                ], spacing=5, scroll=ft.ScrollMode.AUTO),
                padding=ft.padding.symmetric(horizontal=10),
                bgcolor=COLOR_SURFACE,
                border_radius=RADIUS_SM,
                border=ft.border.all(1, BORDER_SUBTLE)
            ),
            
            ft.Row([
                ft.Container(
                    content=ft.Row([ui["txt_line_numbers"], ui["txt_json_input"]], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
                    expand=1, border=ft.border.all(1, BORDER_SUBTLE), border_radius=RADIUS_SM, bgcolor=COLOR_SURFACE, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
                ft.Container(
                    content=ui["tree_container"],
                    expand=1, border=ft.border.all(1, BORDER_SUBTLE), border_radius=RADIUS_SM, bgcolor=COLOR_BG, padding=10, clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                )
            ], expand=True, spacing=15)
        ], spacing=15))

    # --- 🧮 4. Binary Tool ---
    if index == 4:
        return card_container(ft.Column([
            section_title("Binary Calculator", "🧮"),
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("เลขฐานสิบเป็นเลขฐานสอง", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("เหมาะสำหรับดูผลลัพธ์แบบเร็วและไล่ breakdown ของแต่ละ bit", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    badge("Bit view", tone="soft"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            panel(
                content=ft.Column([
                    ui["txt_dec"], 
                    ft.Container(content=ui["lbl_bin"], padding=15, bgcolor=COLOR_BG, border_radius=RADIUS_SM, border=ft.border.all(1, BORDER_SUBTLE)),
                ], spacing=SPACE_MD),
                bgcolor=COLOR_PANEL,
            ),
            
            ft.Column([
                ft.Row([ft.Icon(ft.icons.FUNCTIONS, color=COLOR_SECONDARY), ui["lbl_sum"]]),
                ft.Row([ft.Icon(ft.icons.INFO_OUTLINE, color=COLOR_ACCENT, size=16), ui["lbl_sql_warn"]]),
            ], spacing=10),
            
            ui["box_breakdown"],
        ], spacing=SPACE_LG, scroll=ft.ScrollMode.AUTO))

    # --- ⏱️ 5. Time Converter ---
    if index == 5:
        return card_container(ft.Column([
            section_title("Time Converter", "⏱️"),
            panel(
                ft.Text("แปลง Unix Epoch และ .NET Ticks เป็นเวลาท้องถิ่นได้จากหน้าเดียว พร้อมตัวอย่างอ้างอิง", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            ft.Row([
                ft.TextButton("Load Demo", icon=ft.icons.PLAY_CIRCLE, on_click=actions["run_load_time_ex"]),
                ft.TextButton("Current Time", icon=ft.icons.ACCESS_TIME, on_click=actions["run_load_current_time"]),
                ft.TextButton("Clear", icon=ft.icons.DELETE, on_click=actions["run_clear_time"], icon_color=COLOR_ERROR),
            ], spacing=10),

            panel(
                content=ft.Column([
                    ft.Text("Unix Epoch", weight="bold", color=COLOR_PRIMARY),
                    ft.Row([ui["txt_epoch"], ft.ElevatedButton("Convert", on_click=actions["conv_epoch"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=45)]),
                    ui["lbl_epoch"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),

            panel(
                content=ft.Column([
                    ft.Text(".NET Ticks", weight="bold", color=COLOR_PRIMARY),
                    ft.Row([ui["txt_ticks"], ft.ElevatedButton("Convert", on_click=actions["conv_ticks"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=45)]),
                    ui["lbl_ticks"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),

            # Reference Table
            ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Type")), ft.DataColumn(ft.Text("Example")), ft.DataColumn(ft.Text("Description"))],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Unix")), ft.DataCell(ft.Text("1714272000")), ft.DataCell(ft.Text("Standard API"))]),
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Ticks")), ft.DataCell(ft.Text("638...000")), ft.DataCell(ft.Text(".NET Systems"))]),
                ],
                border=ft.border.all(1, BORDER_SUBTLE),
                border_radius=RADIUS_MD,
                heading_row_color="white05"
            )
        ], spacing=SPACE_LG, scroll=ft.ScrollMode.AUTO))

    # --- 🔐 6. Base64 Tool ---
    if index == 6:
        return card_container(ft.Column([
            section_title("Base64 Tool", "🔐"),
            panel(
                ft.Text("เข้ารหัสหรือถอดรหัสข้อความแบบ Base64 ได้อย่างรวดเร็ว เหมาะกับงาน support และ debugging", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            ft.Row([
                ft.TextButton("Demo", icon=ft.icons.PLAY_CIRCLE, on_click=actions["run_load_b64_ex"]),
                ft.TextButton("Clear", icon=ft.icons.DELETE, on_click=actions["run_clear_b64"], icon_color=COLOR_ERROR),
            ], spacing=10),

            panel(
                content=ui["txt_b64"],
                padding=5, bgcolor=COLOR_PANEL
            ),

            ft.Row([
                ft.ElevatedButton("Encode", on_click=actions["run_b64_enc"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=50, expand=True),
                ft.ElevatedButton("Decode", on_click=actions["run_b64_dec"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=50, expand=True),
            ], spacing=20),

            ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Format")), ft.DataColumn(ft.Text("Example"))],
                rows=[
                    ft.DataRow(cells=[ft.DataCell(ft.Text("Auth")), ft.DataCell(ft.Text("YWRtaW46MTIzNA=="))]),
                ],
                border=ft.border.all(1, BORDER_SUBTLE),
                border_radius=RADIUS_MD,
                heading_row_color="white05"
            )
        ], spacing=SPACE_LG, scroll=ft.ScrollMode.AUTO))

    # --- 🔑 7. Password Gen ---
    if index == 7:
        return card_container(ft.Column([
            section_title("Password Generator", "🔑"),
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("สร้างรหัสผ่านตามเงื่อนไขที่ต้องการ", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("กำหนดความยาวและชุดอักขระที่ต้องการก่อนสร้างรหัสผ่าน", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    badge("Secure", tone="accent"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            panel(
                content=ft.Column([
                    ui["lbl_pass_len"], ui["slider_len"],
                    ft.Row([ui["chk_upper"], ui["chk_lower"]], spacing=20),
                    ft.Row([ui["chk_nums"], ui["chk_syms"]], spacing=20),
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),
            
            ft.Row([
                ft.ElevatedButton("🎲 Generate Secure Password", on_click=actions["run_gen_pass"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=55, expand=True),
            ]),
            
            ft.Container(
                content=ft.Row([ui["txt_pass_out"], ft.IconButton(ft.icons.COPY, on_click=actions["btn_copy_pass"], icon_color=COLOR_PRIMARY)], spacing=10),
                padding=10, bgcolor=COLOR_BG, border_radius=RADIUS_SM, border=ft.border.all(1, BORDER_SUBTLE)
            ),
        ], spacing=SPACE_LG))

    # --- 🕵️ 8. Hidden Char Check ---
    if index == 8:
        return card_container(ft.Column([
            section_title("Hidden Char Checker", "🕵️"),
            
            ft.Row([
                ft.ElevatedButton("Open File", icon=ft.icons.FILE_OPEN, on_click=actions["btn_open_hidden"], bgcolor=COLOR_SURFACE, color=COLOR_TEXT),
                ft.TextButton("Reset Mode", icon=ft.icons.REFRESH, on_click=actions["btn_clear_hidden"], icon_color=COLOR_ERROR),
            ], spacing=15),
            
            ui["lbl_hidden_file"],
            
            ft.Container(
                content=ft.Stack([
                    ui["txt_hidden_in"], 
                    ft.Column([ui["view_highlight"]], scroll=ft.ScrollMode.AUTO, expand=True)
                ]), 
                expand=2, padding=10, bgcolor=COLOR_SURFACE, border_radius=RADIUS_MD, border=ft.border.all(1, BORDER_SUBTLE)
            ),
            
            ft.Row([
                ft.ElevatedButton("Analyze", icon=ft.icons.ANALYTICS, on_click=actions["run_check_hidden"], bgcolor=COLOR_SECONDARY, color="black"),
                ft.ElevatedButton("Apply & Save", icon=ft.icons.SAVE, on_click=actions["run_save_replace_hidden"], bgcolor=COLOR_ERROR, color="white"),
                ft.ElevatedButton("Visual Mode", icon=ft.icons.VISIBILITY, on_click=actions["run_visual_check"], bgcolor="blue700"),
                ft.ElevatedButton("Clean", icon=ft.icons.CLEANING_SERVICES, on_click=actions["run_clean_hidden"], bgcolor=COLOR_ACCENT, color="black"),
            ], spacing=10, scroll=ft.ScrollMode.AUTO),

            ft.Container(
                content=ui["txt_hidden_out"],
                expand=1, padding=10, bgcolor=COLOR_BG, border_radius=RADIUS_MD, border=ft.border.all(1, BORDER_SUBTLE)
            ),
            
            ft.Row([
                ft.TextButton("Clear All", icon=ft.icons.DELETE, on_click=actions["run_clear_hidden_all"], icon_color=COLOR_ERROR), 
                ft.ElevatedButton("Copy Result", icon=ft.icons.COPY, on_click=actions["btn_copy_clean"], bgcolor=COLOR_PRIMARY, color="black"),
            ], alignment=ft.MainAxisAlignment.END),

        ], expand=True, spacing=15))

    # --- 📝 9. Smart Formatter ---
    if index == 9:
        return card_container(ft.Column([
            section_title("Smart Formatter", "📝"),
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("ชุดเทมเพลตตอบกลับสำหรับทีม support", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("กรอกข้อมูลสั้นๆ แล้วเลือก template หรือจัดรูปแบบคำตอบแบบ custom ได้ทันที", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    badge("Support ops", tone="primary"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            # Direct Input Group
            panel(
                ft.Column([
                    ft.Row([
                        ui["txt_fmt_ticket"], 
                        ui["txt_fmt_date"], 
                        ft.IconButton(ft.icons.DELETE_SWEEP, on_click=actions["run_clear_fmt"], icon_color=COLOR_ERROR)
                    ], spacing=10),
                    ui["txt_fmt_subject"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),
            
            panel(ft.Column([
                ft.Text("Templates:", size=12, weight="bold", color=COLOR_PRIMARY),
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton("#1 Ack", on_click=actions["apply_fmt"], data="1", bgcolor=COLOR_SURFACE, height=35),
                        ft.ElevatedButton("#2 Need Info", on_click=actions["apply_fmt"], data="2", bgcolor=COLOR_SURFACE, height=35),
                        ft.ElevatedButton("#3 New Email", on_click=actions["apply_fmt"], data="3", bgcolor=COLOR_SURFACE, height=35),
                    ], spacing=8),
                    ft.Row([
                        ft.ElevatedButton("#4 Confirm", on_click=actions["apply_fmt"], data="4", bgcolor=COLOR_SURFACE, height=35),
                        ft.ElevatedButton("#5 Help Center", on_click=actions["apply_fmt"], data="5", bgcolor=COLOR_SURFACE, height=35),
                        ft.ElevatedButton("#6 Policy", on_click=actions["apply_fmt"], data="6", bgcolor=COLOR_SURFACE, height=35),
                    ], spacing=8),
                    ft.Row([
                        ft.ElevatedButton("#7 LINE Notice", on_click=actions["apply_fmt"], data="7", bgcolor="#06C755", height=35),
                    ], spacing=8),
                ], spacing=8),
            ], spacing=5), bgcolor=COLOR_PANEL_ALT),

            ft.Divider(color=BORDER_SUBTLE, height=10),

            ft.Row([
                ft.Text("Custom Response", weight="bold", color=COLOR_ACCENT),
                ft.ElevatedButton("Format", icon=ft.icons.AUTO_FIX_HIGH, on_click=actions["run_format_email"], bgcolor=COLOR_PRIMARY, color="black", height=35),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            panel(ui["txt_fmt_input"], padding=5, bgcolor=COLOR_PANEL),
            
            ft.Row([
                ft.Text("Ready Output", weight="bold", color=COLOR_TEXT_DIM),
                ft.ElevatedButton("Copy Result", icon=ft.icons.COPY, on_click=actions["btn_copy_fmt"], bgcolor=COLOR_SECONDARY, color="black", height=35),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            
            panel(ui["txt_fmt_res"], padding=5, bgcolor=COLOR_PANEL_ALT), # This will now expand to fill the rest of the space
        ], spacing=10, scroll=ft.ScrollMode.AUTO))

    # --- 🔍 10. Bit Finder ---
    if index == 10:
        return card_container(ft.Column([
            section_title("Bit Index Finder", "🔍"),
            
            ft.Container(content=ui["txt_bin_in"], height=120, bgcolor=COLOR_SURFACE, border_radius=RADIUS_MD),
            
            ft.Row([
                ft.ElevatedButton("Find Indices", icon=ft.icons.SEARCH, on_click=actions["run_find_bits"], bgcolor=COLOR_PRIMARY, color="black", height=45),
                ft.TextButton("Clear", icon=ft.icons.DELETE, on_click=actions["run_clear_bits"], icon_color=COLOR_ERROR),
                ui["lbl_bin_count"]
            ], spacing=15),
            
            ft.Divider(color=BORDER_SUBTLE),
            
            ft.Text("Raw Indices", size=12, weight="bold", color=COLOR_TEXT_DIM),
            ft.Container(content=ft.Row([ui["txt_bin_out"], ft.IconButton(ft.icons.COPY, on_click=actions["btn_copy_bits"])], spacing=10), bgcolor=COLOR_SURFACE, padding=5, border_radius=RADIUS_SM),

            ft.Text("SQL Query", size=12, weight="bold", color=COLOR_TEXT_DIM),
            ft.Container(content=ft.Row([ui["txt_sql_out"], ft.IconButton(ft.icons.COPY, on_click=actions["btn_copy_sql"])], spacing=10), bgcolor=COLOR_SURFACE, padding=5, border_radius=RADIUS_SM, expand=True),
            
        ], expand=True, spacing=10))

    # --- 🎭 11. Compare Text ---
    if index == 11:
        return card_container(ft.Column([
            section_title("Text Diff Tool", "🎭"),
            
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("เปรียบเทียบข้อความแบบอ่านง่าย", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("วางข้อความต้นฉบับและข้อความใหม่ จากนั้นดูผลต่างแบบ line-by-line ด้านล่าง", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    ft.TextButton("Clear All", on_click=actions["run_clear_compare"], icon=ft.icons.DELETE, icon_color=COLOR_ERROR),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                bgcolor=COLOR_PANEL_ALT,
            ),

            panel(
                ft.Column([
                    ft.Text("Original", size=FONT_SIZE_SMALL, weight="bold", color=COLOR_PRIMARY),
                    ui["txt_compare_1"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),
            panel(
                ft.Column([
                    ft.Text("Changed", size=FONT_SIZE_SMALL, weight="bold", color=COLOR_SECONDARY),
                    ui["txt_compare_2"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),

            ft.Row([
                ft.ElevatedButton("🔍 Analyze Differences", on_click=actions["run_compare_text"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=50, expand=True),
            ]),

            panel(
                ft.Column([
                    ft.Text("Diff Result", size=FONT_SIZE_SMALL, weight="bold", color=COLOR_TEXT),
                    ft.Container(
                        content=ui["col_diff_main"],
                        height=320,
                        border=ft.border.all(1, BORDER_SUBTLE),
                        border_radius=RADIUS_MD,
                        padding=10,
                        bgcolor=COLOR_BG,
                    ),
                ], spacing=10),
                bgcolor=COLOR_PANEL_ALT,
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO))

    # --- 🔐 12. JWT Decoder ---
    if index == 12:
        return card_container(ft.Column([
            section_title("JWT Decoder", "🔐"),
            
            panel(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("Token Intake", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                            ft.Text("วาง JWT เพื่อถอด Header และ Payload พร้อมตรวจสถานะการหมดอายุ", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                        ], spacing=4, expand=True),
                        badge("Local decode", tone="primary"),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ui["txt_jwt_input"],
                    ft.Row([
                        ft.ElevatedButton("Decode Token", icon=ft.icons.LOCK_OPEN, on_click=actions["run_decode_jwt"], bgcolor=COLOR_PRIMARY, color="black", height=45, expand=True),
                        ft.IconButton(ft.icons.DELETE, on_click=actions["run_clear_jwt"], icon_color=COLOR_ERROR),
                    ], spacing=10),
                ], spacing=15),
                bgcolor=COLOR_PANEL_ALT,
            ),

            panel(
                ft.Column([
                    ft.Text("Header", size=FONT_SIZE_SMALL, weight="bold", color=COLOR_PRIMARY),
                    ui["txt_jwt_header"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),

            panel(
                ft.Column([
                    ft.Text("Payload", size=FONT_SIZE_SMALL, weight="bold", color=COLOR_SECONDARY),
                    ui["txt_jwt_payload"],
                ], spacing=10),
                bgcolor=COLOR_PANEL,
            ),

            panel(
                ft.Row([
                    badge("Decode status", tone="soft"),
                    ui["lbl_jwt_status"],
                ], spacing=12),
                bgcolor=COLOR_PANEL_ALT,
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO))

    # --- 🖼️ 13. Image Optimizer ---
    if index == 13:
        return card_container(ft.Column([
            section_title("Image Optimizer", "🖼️"),
            panel(
                ft.Row([
                    ft.Column([
                        ft.Text("บีบอัดและแปลงไฟล์ภาพอย่างรวดเร็ว", size=FONT_SIZE_H3, weight="bold", color=COLOR_TEXT),
                        ft.Text("เลือกไฟล์ ปรับ quality และเลือกรูปแบบผลลัพธ์ ก่อน optimize ได้จากหน้าเดียว", color=COLOR_TEXT_DIM, size=FONT_SIZE_SMALL),
                    ], spacing=4, expand=True),
                    badge("PNG / JPG / WEBP", tone="soft"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor=COLOR_PANEL_ALT,
            ),
            
            panel(
                content=ft.Column([
                    ft.Row([ui["txt_img_src"], ft.ElevatedButton("Select", icon=ft.icons.IMAGE, on_click=actions["btn_open_img"], bgcolor=COLOR_SECONDARY, color="black")]),
                    ft.Row([
                        ft.Column([ft.Text("Quality", size=12), ui["slider_img_quality"]], expand=2),
                        ft.Column([ft.Text("Format", size=12), ui["dd_img_format"]], expand=1),
                    ], spacing=20),
                ], spacing=15),
                bgcolor=COLOR_PANEL,
            ),

            ft.Row([
                ft.ElevatedButton("🚀 Optimize Image", icon=ft.icons.AUTO_FIX_NORMAL, on_click=actions["run_optimize_img"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=55, expand=True),
            ]),
            
            ui["lbl_img_status"],
            
            ft.Container(
                content=ft.Column([ft.Text("Original Preview", size=12, color=COLOR_TEXT_DIM), ui["img_preview"]], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                height=320, border=ft.border.all(1, BORDER_SUBTLE), border_radius=RADIUS_MD, padding=10, bgcolor=COLOR_BG, visible=False
            )
        ], spacing=15, scroll=ft.ScrollMode.AUTO))

    # --- 🚧 Default ---
    return card_container(ft.Column([
        ft.Text("🚧", size=80),
        ft.Text("Under Development", size=FONT_SIZE_H2, weight="bold"),
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20), expand=False)
