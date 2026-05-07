import flet as ft
from ui_config import (
    COLOR_ACCENT,
    COLOR_BG,
    COLOR_CARD,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_TEXT,
)

def section_title(text: str, icon_text: str):
    return ft.Row([ft.Text(icon_text, size=26, color=COLOR_PRIMARY), ft.Text(text, size=28, weight="bold")])

def build_tool_view(index: int, ui: dict, actions: dict):
    # --- 🏠 0. Welcome / Dashboard Page (NEW v16.0) ---
    if index == 0:
        return ft.Container(
            content=ft.Column([
                ft.Column([
                    # 📌 ส่วนหัว: ปรับใหม่ให้อยู่ตรงกลางทั้งหมด (Logo -> Title -> Clock)
                    ft.Column([
                        # 1. Logo
                        ft.Text("🛠️", size=40),
                        
                        # 2. ชื่อโปรแกรมและรายละเอียด (Center Aligned)
                        ft.Column([
                            ft.Text(
                                "KhawOat Multi-Tools", 
                                size=30, 
                                weight="bold", 
                                color=COLOR_PRIMARY, 
                                text_align=ft.TextAlign.CENTER
                            ),
                            ft.Text(
                                "The Ultimate Application Support Arsenal", 
                                size=16, 
                                italic=True, 
                                color="white54", 
                                text_align=ft.TextAlign.CENTER
                            ),
                        ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        
                        # 3. เวลา (Live Clock) ย้ายมาไว้ใต้ชื่อโปรแกรม
                        ft.Row([
                            ft.Text("🕒 Current Time:", size=14, color="white54"),
                            ui["lbl_clock"] 
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15, width=float("inf")),

                    ft.Divider(height=20, color="white10"),

                    # 📌 ส่วน Greeting & GIF ดุ๊กดิ๊ก 
                    ft.Container(
                        content=ft.Column([
                            ft.Image(
                                src=ui["greeting_gif"], 
                                width=140, 
                                height=140,
                                fit=ft.ImageFit.CONTAIN
                            ),
                            ft.Text(ui["greeting_text"], size=18, weight="bold", color=COLOR_PRIMARY, text_align="center"),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        padding=20,
                        width=float("inf"), # กางให้เต็มความกว้าง
                    ),

                    # 📌 ส่วน Quick Stats Cards 
                    ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("11", size=40, weight="bold", color=COLOR_SECONDARY),
                            ft.Text("Active Tools", size=14, weight="bold")
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),

                            bgcolor="#1E231E", padding=20, border_radius=15, expand=True
                        ),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Ready", size=40, weight="bold", color=COLOR_ACCENT),
                                ft.Text("System Status", size=14, weight="bold")
                            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor="#1E231E", padding=20, border_radius=15, expand=True
                        ),
                    ], spacing=20),
                ], scroll=ft.ScrollMode.AUTO, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=25)
            ]),
            padding=50, 
            bgcolor=COLOR_CARD, 
            # 📌 ปรับมุมโค้งให้รับกับ Sidebar ฝั่งซ้าย 
            border_radius=ft.border_radius.only(top_left=0, bottom_left=0),
            expand=True
        )

    # --- 🗂️ 1. Merge & Split ---
    if index == 1:
        return ft.Container(
            content=ft.Column([
                section_title("Merge & Split File (Auto Output)", "🗂️"),
                ft.Row([ui["txt_src_dir"], ft.ElevatedButton("เลือกโฟลเดอร์", on_click=actions["btn_open_src"]), ui["dd_src_ext"]]),
                ft.Row([ui["txt_base_name"], ui["dd_out_ext"]]),
                ft.Row([ui["txt_lines"], ui["chk_header"]]),
                ft.ElevatedButton("🚀 เริ่มรวมและแบ่งไฟล์", on_click=actions["run_split"], bgcolor=COLOR_ACCENT, color=COLOR_BG, width=250, height=50),
                ui["lbl_split_status"],
                ui["lbl_split_summary"],
            ], spacing=20),
            padding=40, bgcolor=COLOR_CARD, border_radius=0
        )

    # --- 🔳 2. QR Generator ---
    if index == 2:
        return ft.Container(
            content=ft.Column([
                section_title("QR Generator", "🔳"),
                ui["txt_qr"],
                ft.Row([
                    ft.ElevatedButton("สร้าง QR Code", on_click=actions["run_gen_qr"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=50),
                    ft.ElevatedButton("💾 บันทึกรูปภาพ", on_click=actions["btn_save_qr"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=50),
                ]),
                ui["lbl_qr_status"],
                ft.Container(ui["img_qr"]),
            ], spacing=20),
            padding=40, bgcolor=COLOR_CARD, border_radius=0
        )

    # --- 🧾 3. JSON Tool (Viewer Pro Updated v16.8.1) ---
    if index == 3:
        # Search bar for Tree View
        ui["txt_json_search"] = ft.TextField(
            label="🔍 Search in Tree...",
            text_size=14,
            height=40,
            border_color=COLOR_PRIMARY,
            bgcolor="#252B25",
            border_radius=8,
            expand=True,
            on_submit=actions.get("run_search_json")
        )

        return ft.Container(
            content=ft.Column([
                section_title("JSON Viewer Pro", "🧾"),
                ft.Row([
                    ft.Text("💡 Side-by-Side Mode: Text Editor (Left) | Tree Viewer (Right)", color="white54", size=12),
                    ft.VerticalDivider(),
                    ui["txt_json_search"],
                    ft.IconButton(ft.icons.SEARCH, on_click=actions.get("run_search_json"), icon_color=COLOR_PRIMARY)
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),

                ft.Row([
                    ft.TextButton("📋 Copy", on_click=actions["btn_copy_json"], icon=ft.icons.COPY),
                    ft.TextButton("✨ Format", on_click=actions["run_fmt_json"], icon=ft.icons.FORMAT_ALIGN_LEFT),
                    ft.TextButton("🧹 Minify", on_click=actions["run_minify_json"], icon=ft.icons.COMPRESS),
                    ft.TextButton("🔓 B64 Decode", on_click=actions.get("run_b64_decode_json"), icon=ft.icons.UNARCHIVE),
                    ft.VerticalDivider(),
                    ft.TextButton("📊 JSON ➔ CSV", on_click=actions.get("run_json_to_csv"), icon=ft.icons.TABLE_VIEW, icon_color=COLOR_SECONDARY),
                    ft.TextButton("🧾 CSV ➔ JSON", on_click=actions.get("run_csv_to_json"), icon=ft.icons.DATA_OBJECT, icon_color=COLOR_SECONDARY),
                    ft.VerticalDivider(),
                    ft.TextButton("🔍 Diff", on_click=actions.get("run_diff_json"), icon=ft.icons.COMPARE_ARROWS, icon_color=COLOR_ACCENT),
                    ft.TextButton("✅ Validate", on_click=actions.get("run_validate_json"), icon=ft.icons.RULE, icon_color=COLOR_ACCENT),
                    ft.VerticalDivider(),
                    ft.TextButton("🗑️ Clear", on_click=actions["run_clear_json"], icon=ft.icons.DELETE_OUTLINE, icon_color="red"),
                    ft.TextButton("📄 Demo", on_click=actions["run_load_json_data"], icon=ft.icons.FILE_DOWNLOAD),
                ], spacing=5, wrap=True, scroll=ft.ScrollMode.AUTO),
                
                # Side-by-Side Layout
                ft.Row([
                    # Left: Text Editor
                    ft.Container(
                        content=ft.Column([
                            ft.Row([ui["txt_line_numbers"], ui["txt_json_input"]], spacing=0, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
                        ]),
                        expand=1,
                        border=ft.border.all(1, "white10"),
                        border_radius=10,
                        bgcolor="#1E231E",
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    ),
                    # Right: Tree Viewer
                    ft.Container(
                        content=ui["tree_container"],
                        expand=1,
                        border=ft.border.all(1, "white10"),
                        border_radius=10,
                        bgcolor="#161A16",
                        padding=10,
                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    )
                ], expand=True, spacing=10)
            ], spacing=15),
            padding=40, 
            bgcolor=COLOR_CARD, 
            border_radius=0, # รักษาความเหลี่ยมตามคอนเซปต์ v16.4
            expand=True
        )

    # --- 🧮 4. Binary Tool ---
    if index == 4:
        return ft.Container(
            content=ft.Column([
                section_title("Binary & Bit Calculator", "🧮"),
                ft.Text("💡 พิมพ์เลขฐาน 10 ระบบจะแยก Bit ให้ดูอัตโนมัติ", color="white54"),
                ui["txt_dec"], ui["lbl_bin"],
                ft.Divider(color="white10"),
                ui["lbl_sum"], ui["lbl_sql_warn"], ui["box_breakdown"],
            ], spacing=20),
            padding=40, bgcolor=COLOR_CARD, border_radius=0
        )

    # --- ⏱️ 5. Time Converter ---
    if index == 5:
        return ft.Container(
            content=ft.Column([
                section_title("Time Converter", "⏱️"),
                
                # แถวปุ่มลัด (เพิ่มปุ่ม Clear สีแดงเพื่อให้เด่นครับ)
                ft.Row([
                    ft.TextButton("📄 Load Examples", icon=ft.icons.REPLY_ALL, on_click=actions["run_load_time_ex"]),
                    ft.TextButton("🕒 Use Current Time", icon=ft.icons.ACCESS_TIME, on_click=actions["run_load_current_time"]),
                    ft.TextButton("🗑️ Clear All", icon=ft.icons.DELETE_FOREVER, on_click=actions["run_clear_time"], icon_color="red"),
                ], spacing=10),

                ft.Divider(color="white10"),

                # 1. Unix Epoch Section
                ft.Text("🌐 Unix Epoch (Seconds)", weight="bold", color=COLOR_PRIMARY),
                ft.Text("พบได้บ่อยใน API ทั่วไป และฐานข้อมูล MySQL/PostgreSQL", size=12, color="white54"),
                ft.Row([
                    ui["txt_epoch"], 
                    ft.ElevatedButton("Convert", on_click=actions["conv_epoch"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=40)
                ]),
                ui["lbl_epoch"],

                ft.Container(height=5),

                # 2. .NET Ticks Section
                ft.Text("💻 .NET Ticks", weight="bold", color=COLOR_PRIMARY),
                ft.Text("มักพบในระบบที่พัฒนาด้วย C# / .NET หรือ Log จากบางพาร์ทเนอร์", size=12, color="white54"),
                ft.Row([
                    ui["txt_ticks"], 
                    ft.ElevatedButton("Convert", on_click=actions["conv_ticks"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=40)
                ]),
                ui["lbl_ticks"],

                ft.Divider(color="white10"),

                # 📌 3. ตารางตัวอย่างอ้างอิง (Reference Table)
                ft.Text("📊 Quick Reference Table", weight="bold"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Format")),
                        ft.DataColumn(ft.Text("Example Value")),
                        ft.DataColumn(ft.Text("Description")),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Unix")),
                            ft.DataCell(ft.Text("1714272000")),
                            ft.DataCell(ft.Text("April 28, 2026")),
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Ticks")),
                            ft.DataCell(ft.Text("638...000")),
                            ft.DataCell(ft.Text("100-ns Intervals")),
                        ]),
                    ],
                    border=ft.border.all(1, "white10"),
                    border_radius=10,
                )

            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 🔐 6. Base64 Tool (Enhanced v16.10) ---
    if index == 6:
        return ft.Container(
            content=ft.Column([
                section_title("Base64 Encode/Decode", "🔐"),
                
                # แถวปุ่มควบคุม
                ft.Row([
                    ft.TextButton("📄 Load Example", icon=ft.icons.REPLY_ALL, on_click=actions["run_load_b64_ex"]),
                    ft.TextButton("🗑️ Clear All", icon=ft.icons.DELETE_FOREVER, on_click=actions["run_clear_b64"], icon_color="red"),
                ], spacing=10),

                ft.Divider(color="white10"),

                ft.Text("💡 วางข้อความที่ต้องการเข้ารหัส หรือวาง Base64 ที่ต้องการถอดรหัส", size=12, color="white54"),
                ui["txt_b64"],

                ft.Row([
                    ft.ElevatedButton("Encode (เข้ารหัส)", on_click=actions["run_b64_enc"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=50, expand=True),
                    ft.ElevatedButton("Decode (ถอดรหัส)", on_click=actions["run_b64_dec"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=50, expand=True),
                ], spacing=20),

                ft.Divider(color="white10"),

                # 📌 ตารางอ้างอิงสำหรับมือใหม่ในทีม
                ft.Text("📊 Base64 Quick Reference", weight="bold"),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Plain Text")),
                        ft.DataColumn(ft.Text("Base64 Result")),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("admin:1234")),
                            ft.DataCell(ft.Text("YWRtaW46MTIzNA==")),
                        ]),
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("Hello")),
                            ft.DataCell(ft.Text("SGVsbG8=")),
                        ]),
                    ],
                    border=ft.border.all(1, "white10"),
                    border_radius=10,
                )
            ], spacing=15, scroll=ft.ScrollMode.AUTO),
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 🔑 7. Password Gen ---
    if index == 7:
        return ft.Container(
            content=ft.Column([
                section_title("Password Generator", "🔑"),
                ui["lbl_pass_len"], ui["slider_len"],
                ft.Row([ui["chk_upper"], ui["chk_lower"], ui["chk_nums"], ui["chk_syms"]], wrap=True),
                ft.ElevatedButton("🎲 Generate Password", on_click=actions["run_gen_pass"], bgcolor=COLOR_ACCENT, color=COLOR_BG, height=50),
                ui["txt_pass_out"],
                ft.ElevatedButton("📋 Copy Password", on_click=actions["btn_copy_pass"], bgcolor=COLOR_SECONDARY, color=COLOR_BG, height=50),
            ], spacing=20),
            padding=40, bgcolor=COLOR_CARD, border_radius=0
        )

    # --- 🕵️ 8. Hidden Char Check (Fixed Overlap) ---
    if index == 8:
        return ft.Container(
            content=ft.Column([
                section_title("Hidden Char Checker", "🕵️"),
                
                # 1. ส่วนเลือกไฟล์
                ft.Row([
                    ft.ElevatedButton("📁 เลือกไฟล์", icon=ft.icons.FOLDER_OPEN, on_click=actions["btn_open_hidden"], bgcolor="#1E231E"),
                    ft.ElevatedButton("❌ ยกเลิกโหมดไฟล์", on_click=actions["btn_clear_hidden"], icon=ft.icons.CLOSE, icon_color="red"),
                ], spacing=20),
                
                ui["lbl_hidden_file"],
                
                # 2. ส่วน Input (กรอบบน)
                ft.Container(
                    content=ft.Stack([
                        ui["txt_hidden_in"], 
                        ft.Column([ui["view_highlight"]], scroll=ft.ScrollMode.AUTO, expand=True)
                    ]), 
                    expand=3,
                ),
                
                # 3. ปุ่ม Action
                ft.Row([
                    ft.ElevatedButton("🔍 ตรวจสอบอักขระ", icon=ft.icons.SEARCH, on_click=actions["run_check_hidden"], bgcolor="#95D5B2", color="black"),
                    ft.ElevatedButton("💾 🛠️ บันทึกทับไฟล์", icon=ft.icons.SAVE, on_click=actions["run_save_replace_hidden"], bgcolor="#B23A48", color="white"),
                    ft.ElevatedButton("👁️ Visual Mode", icon=ft.icons.REMOVE_RED_EYE, on_click=actions["run_visual_check"], bgcolor="blue700"),
                    ft.ElevatedButton("✨ Clean Text", icon=ft.icons.CLEANING_SERVICES, on_click=actions["run_clean_hidden"], bgcolor="#D4A373", color="black"),
                ], spacing=10, scroll=ft.ScrollMode.AUTO),

                ft.Text("ผลการตรวจสอบ:", weight="bold", color="white54"),
                
                # 📌 4. ส่วนแสดงผลลัพธ์ (กรอบล่าง - ลบตัวซ้ำออกแล้ว)
                ft.Container(
                    content=ui["txt_hidden_out"],
                    expand=2, # ปรับสัดส่วนให้เหมาะสม
                    border=ft.border.all(1, "white10"),
                    border_radius=10,
                    padding=5
                ),
                
                # 5. ปุ่ม Bottom Actions
                ft.Row([
                    ft.ElevatedButton("🗑️ Clear", icon=ft.icons.DELETE_FOREVER, on_click=actions["run_clear_hidden_all"], bgcolor="red700"), 
                    ft.ElevatedButton("📋 Copy ผลลัพธ์", icon=ft.icons.COPY, on_click=actions["btn_copy_clean"], bgcolor=COLOR_PRIMARY, color="black"),
                ], alignment=ft.MainAxisAlignment.END),

            ], expand=True, spacing=15),
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 📝 9. Smart Formatter (Extended Width v16.16) ---
    if index == 9:
        # 📌 ปรับความกว้าง (Width) และ ความสูง (Height) ให้สมมาตรและยาวขึ้นตามสั่งครับ
        ui["txt_fmt_ticket"].width = 250
        ui["txt_fmt_ticket"].height = 45
        
        ui["txt_fmt_date"].width = 250
        ui["txt_fmt_date"].height = 45
        
        ui["txt_fmt_subject"].height = 45

        return ft.Container(
            content=ft.Column([
                section_title("Smart Formatter", "📝"),
                
                # 1. ส่วนกรอกข้อมูลพื้นฐาน (ปรับความสูงให้บางลง)
                ft.Row([
                    ui["txt_fmt_ticket"],
                    ui["txt_fmt_date"],
                    ft.ElevatedButton("🗑️ Clear", icon=ft.icons.DELETE_SWEEP, on_click=actions["run_clear_fmt"], bgcolor="red700", height=45),
                ], spacing=10),
                
                # 2. ช่อง Subject และแผง Template (ขยับมาชิดกัน)
                ui["txt_fmt_subject"],
                
                ft.Column([
                    ft.Text("เลือก Quick Template:", weight="bold", color=COLOR_PRIMARY, size=12),
                    ft.Row(
                        wrap=True, spacing=10, run_spacing=8,
                        controls=[
                            ft.ElevatedButton("#1 รับทราบ (EN)", on_click=actions["apply_fmt"], data="1", bgcolor="#2D3E50", height=35),
                            ft.ElevatedButton("#2 ขอข้อมูลเพิ่ม", on_click=actions["apply_fmt"], data="2", bgcolor="#2D3E50", height=35),
                            ft.ElevatedButton("#3 แนะนำอีเมล", on_click=actions["apply_fmt"], data="3", bgcolor="#1E231E", height=35),
                            ft.ElevatedButton("#4 ขอยืนยันปิด", on_click=actions["apply_fmt"], data="4", bgcolor="#1E231E", height=35),
                            ft.ElevatedButton("#5 Help Center", on_click=actions["apply_fmt"], data="5", bgcolor="#1E231E", height=35),
                            ft.ElevatedButton("#6 Policy", on_click=actions["apply_fmt"], data="6", bgcolor="#1E231E", height=35),
                            ft.ElevatedButton("#7 รับทราบ/เร่งตรวจ (LINE)", on_click=actions["apply_fmt"], data="7", bgcolor="#06C755", height=35),
                        ]
                    ),
                ], spacing=5), # บังคับระยะห่างระหว่าง Label กับปุ่มให้ชิดกัน

                ft.Divider(height=5, color="white10"), # ลดความสูง Divider เพื่อประหยัดพื้นที่
                
                # 3. ส่วน Input คำตอบ Email
                ft.Row([
                    ft.Text("📧 ส่วนจัด Format คำตอบ Email", weight="bold", color=COLOR_ACCENT),
                    ft.ElevatedButton("🚀 จัดฟอร์แมตอีเมล", icon=ft.icons.EMAIL_OUTLINED, on_click=actions["run_format_email"], bgcolor=COLOR_PRIMARY, color="black", height=40),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    content=ui["txt_fmt_input"], 
                    height=100, 
                ),
                
                ft.Divider(height=5, color="white10"),

                # 4. ส่วนผลลัพธ์ (ขยายเต็มพื้นที่ที่เหลือ)
                ft.Row([
                    ft.Text("ผลลัพธ์พร้อมใช้งาน:", weight="bold", color="white54"),
                    ft.ElevatedButton("📋 Copy Result", icon=ft.icons.COPY, on_click=actions["btn_copy_fmt"], bgcolor=COLOR_SECONDARY, color="black", height=40),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    content=ui["txt_fmt_res"],
                    expand=True, 
                    border=ft.border.all(1, "white10"),
                    border_radius=10,
                    padding=5,
                    bgcolor="#161A16"
                ),

            ], expand=True, spacing=10), # spacing ระหว่างชุดคำสั่งหลัก
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 🔍 10. Bit Finder ---
    if index == 10:
        return ft.Container(
            content=ft.Column([
                section_title("Bit Index Finder", "🔍"),
                ft.Text("💡 ค้นหาตำแหน่งของเลข 1 จากซ้ายไปขวา (เริ่มที่ Index 1)", color="white54"),
                
                ft.Container(
                    content=ui["txt_bin_in"],
                    height=120,
                ),
                
                ft.Row([
                    ft.ElevatedButton("🔍 ค้นหาตำแหน่ง", on_click=actions["run_find_bits"], bgcolor=COLOR_PRIMARY, color="black", height=40),
                    ft.ElevatedButton("🗑️ ล้างข้อมูล", on_click=actions["run_clear_bits"], bgcolor="red700", height=40),
                    ui["lbl_bin_count"]
                ], spacing=15, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                
                ft.Divider(color="white10"),
                
                # Raw Indices Output
                ft.Row([
                    ft.Text("ผลลัพธ์ (Raw Index):", weight="bold", color="white54"),
                    ft.ElevatedButton("📋 Copy Positions", icon=ft.icons.COPY, on_click=actions["btn_copy_bits"], bgcolor=COLOR_SECONDARY, color="black", height=35),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    content=ui["txt_bin_out"],
                    height=80,
                ),

                # SQL Query Output
                ft.Row([
                    ft.Text("SQL Query:", weight="bold", color="white54"),
                    ft.ElevatedButton("📋 Copy SQL Query", icon=ft.icons.COPY, on_click=actions["btn_copy_sql"], bgcolor=COLOR_PRIMARY, color="black", height=35),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(
                    content=ui["txt_sql_out"],
                    expand=True,
                ),
                
            ], expand=True, spacing=10),
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 🎭 11. Compare Text (NEW) ---
    if index == 11:
        return ft.Container(
            content=ft.Column([
                section_title("Compare Text", "🎭"),
                ft.Row([
                    ft.Text("💡 วางข้อความที่ต้องการเปรียบเทียบในช่องซ้ายและขวา", color="white54", size=12),
                    ft.ElevatedButton("🗑️ Clear All", on_click=actions["run_clear_compare"], icon=ft.icons.DELETE_OUTLINE, bgcolor="red700"),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                # Input Row
                ft.Row([
                    ft.Column([
                        ft.Text("Original Text", weight="bold", color=COLOR_PRIMARY),
                        ui["txt_compare_1"]
                    ], expand=1),
                    ft.Column([
                        ft.Text("Changed Text", weight="bold", color=COLOR_SECONDARY),
                        ui["txt_compare_2"]
                    ], expand=1),
                ], expand=True, spacing=20),

                ft.ElevatedButton(
                    "🔍 Compare & Find Differences", 
                    on_click=actions["run_compare_text"], 
                    bgcolor=COLOR_ACCENT, 
                    color=COLOR_BG, 
                    height=50,
                    width=float("inf")
                ),

                ft.Text("Diff Result (Side-by-Side):", weight="bold", color="white54"),
                
                # Result Area (Row-based Synchronized View)
                ft.Container(
                    content=ui["col_diff_main"],
                    expand=True,
                    border=ft.border.all(1, "white10"),
                    border_radius=10,
                    padding=10,
                    bgcolor="#161A16",
                )
            ], expand=True, spacing=15),
            padding=40, bgcolor=COLOR_CARD, border_radius=0, expand=True
        )

    # --- 🚧 อื่นๆ ---
    return ft.Container(
        content=ft.Column([
            ft.Text("🚧", size=80, color=COLOR_PRIMARY),
            ft.Text("อยู่ระหว่างการพัฒนา 🚧", size=32, weight="bold", color=COLOR_TEXT),
        ], spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=100,
    )

def nav_btn(text: str, icon_text: str, on_click):
    return ft.TextButton(content=ft.Row([ft.Text(icon_text, color=COLOR_TEXT), ft.Text(text, color=COLOR_TEXT, weight="bold")]), on_click=on_click)