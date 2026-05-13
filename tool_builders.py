from datetime import datetime

import flet as ft

from tool_context import HandlerContext, ToolBuildContext
from handlers_basic import (
    register_base64_handlers,
    register_compare_text_handlers,
    register_json_tool_handlers,
    register_jwt_handlers,
    register_time_converter_handlers,
)
from handlers_tools import (
    register_bit_finder_handlers,
    register_binary_tool_handlers,
    register_hidden_char_handlers,
    register_image_optimizer_handlers,
    register_merge_split_handlers,
    register_password_handlers,
    register_qr_handlers,
    register_smart_formatter_handlers,
)


def build_base_tool_assets(*, lbl_clock, dlg_loading):
    return {"lbl_clock": lbl_clock, "dlg_loading": dlg_loading}, {}


def create_tool_builders(ctx: ToolBuildContext) -> dict:
    deps = ctx
    handler_deps = HandlerContext.from_build_context(ctx)
    ft_module = ctx.ft

    def setup_home(ui, actions):
        def get_greeting_data():
            hour = datetime.now().hour
            if 5 <= hour < 12:
                return ("อรุณสวัสดิ์ครับ! พร้อมลุยงานเช้านี้แล้วจ้า", "morning.gif")
            if 12 <= hour < 18:
                return ("สวัสดียามบ่ายครับ! อย่าลืมดื่มน้ำพักสายตานะ", "afternoon.gif")
            return ("คืนนี้อีกยาวไกล... รักษาสุขภาพด้วยนะครับ", "night.gif")

        gt, gg = get_greeting_data()
        ui["greeting_text"] = gt
        ui["greeting_gif"] = gg

        async def nav_to_tool(e):
            idx = int(e.control.data)
            await deps["update_view"](idx)

        actions["nav_tool"] = nav_to_tool

    def setup_merge_split(ui, actions):
        ui["txt_src_dir"] = ft_module.TextField(label="โฟลเดอร์ต้นทาง", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, expand=True)
        ui["dd_src_ext"] = ft_module.Dropdown(label="นามสกุลต้นทาง", options=[ft_module.dropdown.Option("CSV"), ft_module.dropdown.Option("EXCEL"), ft_module.dropdown.Option("TXT"), ft_module.dropdown.Option("NO EXT")], value="CSV", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, width=150)
        ui["dd_out_ext"] = ft_module.Dropdown(label="นามสกุลปลายทาง", options=[ft_module.dropdown.Option("CSV"), ft_module.dropdown.Option("EXCEL"), ft_module.dropdown.Option("TXT"), ft_module.dropdown.Option("NO EXT")], value="CSV", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, width=150)
        ui["txt_base_name"] = ft_module.TextField(label="ชื่อไฟล์ผลลัพธ์", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, expand=True)
        ui["txt_lines"] = ft_module.TextField(label="จำนวนแถวต่อไฟล์", value="1,000", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, width=200)
        ui["chk_header"] = ft_module.Checkbox(label="ข้อมูลมี Header (แถวแรก)", value=True, fill_color=deps["COLOR_PRIMARY"])
        ui["lbl_split_status"] = ft_module.Text("สถานะ: พร้อมทำงาน", color="white54")
        ui["lbl_split_summary"] = ft_module.Text("", color=deps["COLOR_PRIMARY"], weight="bold")
        register_merge_split_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_qr(ui, actions):
        ui["txt_qr"] = ft_module.TextField(label="URL หรือ ข้อความ", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["img_qr"] = ft_module.Image(src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw==", width=250, height=250, visible=False)
        ui["lbl_qr_status"] = ft_module.Text("", color="white54")
        ui["qr_container"] = ft_module.Container(content=ui["img_qr"], alignment=getattr(ft_module.alignment, "center", ft_module.alignment.center_left), padding=20, bgcolor="white", border_radius=deps["RADIUS_MD"], visible=False)
        register_qr_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_json_tool(ui, actions):
        ui["txt_line_numbers"] = ft_module.TextField(value="1", multiline=True, read_only=True, width=55, text_size=14, text_align=ft_module.TextAlign.RIGHT, border=ft_module.InputBorder.NONE, bgcolor=deps["COLOR_TRANSPARENT"], color=deps["COLOR_PRIMARY"], text_style=ft_module.TextStyle(font_family="Consolas", height=1.5), content_padding=ft_module.padding.only(top=12, right=10, bottom=12))
        ui["tree_container"] = ft_module.Column(scroll=ft_module.ScrollMode.ALWAYS, expand=True)
        ui["txt_json_input"] = ft_module.TextField(multiline=True, min_lines=20, expand=True, border=ft_module.InputBorder.NONE, bgcolor="#1E231E", text_size=14, text_style=ft_module.TextStyle(font_family="Consolas", height=1.5), content_padding=ft_module.padding.only(top=12, left=10, right=10, bottom=12))
        register_json_tool_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_binary_tool(ui, actions):
        ui["txt_dec"] = ft_module.TextField(label="เลขฐาน 10 (Decimal)", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["lbl_bin"] = ft_module.Text("Binary: -", size=20, weight="bold", color=deps["COLOR_PRIMARY"])
        ui["lbl_sum"] = ft_module.Text("ผลรวม: 0", size=20, weight="bold", color=deps["COLOR_SECONDARY"])
        ui["lbl_sql_warn"] = ft_module.Text("⚠️ ตำแหน่งที่เห็นถ้าเทียบกับ SQL จะต้องนำไป +1 เสมอ", color=deps["COLOR_ACCENT"], italic=True)
        ui["col_breakdown"] = ft_module.Column(spacing=5)
        ui["box_breakdown"] = ft_module.Container(content=ui["col_breakdown"], border=ft_module.border.all(1, deps["COLOR_SECONDARY"]), bgcolor="#181F18", padding=15, border_radius=10, visible=False)
        register_binary_tool_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_time_converter(ui, actions):
        ui["txt_epoch"] = ft_module.TextField(label="Unix Epoch", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["lbl_epoch"] = ft_module.Text("Local Time: -", color=deps["COLOR_SECONDARY"])
        ui["txt_ticks"] = ft_module.TextField(label=".NET Ticks", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["lbl_ticks"] = ft_module.Text("Local Time: -", color=deps["COLOR_SECONDARY"])
        register_time_converter_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_base64(ui, actions):
        ui["txt_b64"] = ft_module.TextField(label="ข้อความ / Base64", multiline=True, min_lines=5, border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        register_base64_handlers(ui, actions, deps=handler_deps)

    def setup_password(ui, actions):
        ui["lbl_pass_len"] = ft_module.Text("ความยาวรหัสผ่าน: 16", weight="bold", size=16)
        ui["slider_len"] = ft_module.Slider(min=8, max=64, divisions=56, value=16, label="{value}", active_color=deps["COLOR_PRIMARY"])
        ui["chk_upper"] = ft_module.Checkbox(label="A-Z", value=True, fill_color=deps["COLOR_PRIMARY"])
        ui["chk_lower"] = ft_module.Checkbox(label="a-z", value=True, fill_color=deps["COLOR_PRIMARY"])
        ui["chk_nums"] = ft_module.Checkbox(label="0-9", value=True, fill_color=deps["COLOR_PRIMARY"])
        ui["chk_syms"] = ft_module.Checkbox(label="!@#$", value=True, fill_color=deps["COLOR_PRIMARY"])
        ui["txt_pass_out"] = ft_module.TextField(label="รหัสผ่าน", read_only=True, border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", border_radius=12, text_size=24, text_style=ft_module.TextStyle(weight=ft_module.FontWeight.BOLD))
        register_password_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_hidden_char(ui, actions):
        ui["txt_hidden_in"] = ft_module.TextField(label="วางข้อความ", multiline=True, expand=True, border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, text_style=ft_module.TextStyle(font_family="Consolas"))
        ui["txt_hidden_out"] = ft_module.TextField(label="ผลลัพธ์", multiline=True, read_only=True, expand=True, border_color=deps["COLOR_ACCENT"], bgcolor="#181C18", border_radius=12)
        ui["lbl_hidden_file"] = ft_module.Text("โหมดไฟล์: ยังไม่ได้เลือกไฟล์", color="white54")
        ui["view_highlight"] = ft_module.Text(spans=[], visible=False)
        register_hidden_char_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_smart_formatter(ui, actions):
        ui["txt_fmt_ticket"] = ft_module.TextField(label="เลข Ticket", hint_text="12345", width=180, border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", border_radius=8, text_size=13)
        ui["txt_fmt_subject"] = ft_module.TextField(label="หัวข้อ (Subject)", hint_text="เช่น [BKK] ปัญหาการใช้งาน...", border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", border_radius=8, text_size=13)
        ui["txt_fmt_date"] = ft_module.TextField(label="วันที่", hint_text="เช่น 28/04/2026", width=180, border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", border_radius=8, text_size=13)
        ui["txt_fmt_input"] = ft_module.TextField(label="คำตอบจาก Support", multiline=True, min_lines=3, max_lines=3, border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", border_radius=8, text_size=13)
        ui["txt_fmt_res"] = ft_module.TextField(label="ผลลัพธ์ (Copy ไปใช้ได้เลย)", multiline=True, min_lines=8, max_lines=12, read_only=True, border_color=deps["COLOR_SECONDARY"], bgcolor="#0A0C0A", text_style=ft_module.TextStyle(size=14, font_family="Tahoma", height=1.5), content_padding=15)
        register_smart_formatter_handlers(ui, actions, deps=handler_deps)

    def setup_bit_finder(ui, actions):
        ui["txt_bin_in"] = ft_module.TextField(label="วางชุดตัวเลข (เช่น 010100001)", multiline=True, expand=True, border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["txt_bin_out"] = ft_module.TextField(label="ตำแหน่งของ 1 (เริ่มนับที่ 1 จากซ้ายไปขวา)", multiline=True, read_only=True, expand=True, border_color=deps["COLOR_ACCENT"], bgcolor="#181C18", border_radius=12)
        ui["txt_sql_out"] = ft_module.TextField(label="SQL Query", multiline=True, read_only=True, expand=True, border_color=deps["COLOR_SECONDARY"], bgcolor="#181C18", border_radius=12)
        ui["lbl_bin_count"] = ft_module.Text("พบเลข 1 จำนวน: 0 จุด", color="white54")
        register_bit_finder_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_compare_text(ui, actions):
        ui["txt_compare_1"] = ft_module.TextField(label="ข้อความเดิม (Original)", multiline=True, min_lines=10, border_color=deps["COLOR_PRIMARY"], bgcolor="#1E231E", text_size=13)
        ui["txt_compare_2"] = ft_module.TextField(label="ข้อความใหม่ (Changed)", multiline=True, min_lines=10, border_color=deps["COLOR_SECONDARY"], bgcolor="#1E231E", text_size=13)
        ui["col_diff_main"] = ft_module.ListView(expand=True, spacing=1)
        register_compare_text_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_jwt(ui, actions):
        ui["txt_jwt_input"] = ft_module.TextField(label="JWT Token", multiline=True, min_lines=5, border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["txt_jwt_header"] = ft_module.TextField(label="Header (JSON)", multiline=True, read_only=True, min_lines=5, border_color=deps["COLOR_PRIMARY"], bgcolor="#181C18", text_style=ft_module.TextStyle(font_family="Consolas"))
        ui["txt_jwt_payload"] = ft_module.TextField(label="Payload (JSON)", multiline=True, read_only=True, min_lines=10, border_color=deps["COLOR_SECONDARY"], bgcolor="#181C18", text_style=ft_module.TextStyle(font_family="Consolas"))
        ui["lbl_jwt_status"] = ft_module.Text("", weight="bold")
        register_jwt_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    def setup_image_optimizer(ui, actions):
        ui["txt_img_src"] = ft_module.TextField(label="ที่อยู่ไฟล์รูปภาพ", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12, expand=True)
        ui["slider_img_quality"] = ft_module.Slider(min=10, max=100, divisions=18, value=80, label="{value}%", active_color=deps["COLOR_PRIMARY"])
        ui["dd_img_format"] = ft_module.Dropdown(label="นามสกุลเป้าหมาย", options=[ft_module.dropdown.Option("Original"), ft_module.dropdown.Option("JPEG"), ft_module.dropdown.Option("PNG"), ft_module.dropdown.Option("WEBP")], value="Original", border_color=deps["COLOR_PRIMARY"], bgcolor="#252B25", border_radius=12)
        ui["lbl_img_status"] = ft_module.Text("สถานะ: พร้อม", color="white54")
        ui["img_preview"] = ft_module.Image(src="", width=300, height=300, fit=ft_module.ImageFit.CONTAIN)
        register_image_optimizer_handlers(
            ui,
            actions,
            deps=handler_deps,
        )

    return {
        0: setup_home,
        1: setup_merge_split,
        2: setup_qr,
        3: setup_json_tool,
        4: setup_binary_tool,
        5: setup_time_converter,
        6: setup_base64,
        7: setup_password,
        8: setup_hidden_char,
        9: setup_smart_formatter,
        10: setup_bit_finder,
        11: setup_compare_text,
        12: setup_jwt,
        13: setup_image_optimizer,
    }
