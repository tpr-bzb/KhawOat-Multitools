import asyncio
import time

import flet as ft
from tool_builders import build_base_tool_assets, create_tool_builders
from tool_context import ToolBuildContext
from tool_registry import TOOL_SPECS
from ui_helpers import build_file_picker_hub, build_loading_dialog
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
from app_release import RELEASE_METADATA, run_auto_update as perform_auto_update
from app_runtime import UiRuntime, ensure_page_update_async
from ui_views import build_tool_view, nav_btn
from services import (
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
    search_json,
    is_base64_json,
    json_to_csv_text,
    csv_to_json_data,
    compare_json,
    get_text_diff,
    decode_jwt,
    optimize_image,
)
from datetime import datetime

COLORS = getattr(ft, "colors", getattr(ft, "Colors", None))
COLOR_TRANSPARENT = getattr(COLORS, "TRANSPARENT", "transparent")
COLOR_RED_400 = getattr(COLORS, "RED_400", "#ef5350")
COLOR_AMBER_300 = getattr(COLORS, "AMBER_300", "#ffd54f")
COLOR_BLUE_300 = getattr(COLORS, "BLUE_300", "#64b5f6")
COLOR_GREEN_400 = getattr(COLORS, "GREEN_400", "#66bb6a")

CURRENT_VERSION = RELEASE_METADATA.version
CURRENT_PATCH_NOTES = RELEASE_METADATA.change_log

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

    await perform_auto_update(
        page=page,
        splash_content=splash_content,
        lbl_splash_status=lbl_splash_status,
        progress_bar=pb_splash,
        current_version=CURRENT_VERSION,
        release_metadata=RELEASE_METADATA,
        accent_color=COLOR_ACCENT,
        primary_color=COLOR_PRIMARY,
    )
    lbl_splash_status.value = "🎯 Ready to Deploy..."
    pb_splash.value = 1
    page.update()
    await asyncio.sleep(0.5)
    splash_overlay.visible = False
    page.update()

    # --- ⚙️ Configuration ---
    configure_page(page)

    ensure_page_update_async(page)

    # --- 🕒 Shared State & Helpers ---
    runtime = UiRuntime(page)
    nav_controls = runtime.nav_controls
    ui_cache = {}
    actions_cache = {}
    async def safe_update(control):
        await runtime.safe_update(control)

    async def set_busy(value: bool):
        await runtime.set_busy(value)

    async def show_toast(message: str, ok: bool = True):
        await runtime.show_toast(message, ok=ok, success_color=COLOR_SECONDARY)

    async def guard_busy() -> bool:
        if runtime.busy:
            await show_toast("กำลังประมวลผลอยู่ กรุณารอสักครู่...", ok=False)
            return True
        return False

    async def close_banner(e):
        await runtime.close_banner(e)

    # Shared UI Elements
    lbl_clock = ft.Text("", size=20, weight="bold", color=COLOR_PRIMARY, font_family="Consolas")
    loading_controls = build_loading_dialog(ft=ft, color_primary=COLOR_PRIMARY, color_accent=COLOR_ACCENT)
    btn_cancel_process = loading_controls.cancel_button
    lbl_modal_status = loading_controls.status_label
    dlg_loading = loading_controls.dialog

    file_picker_hub = build_file_picker_hub(ft=ft, page=page, safe_update=safe_update)
    current_fp_context = file_picker_hub.current_context
    fp_dir = file_picker_hub.directory_picker
    fp_open = file_picker_hub.open_picker
    fp_save = file_picker_hub.save_picker

    # --- 🧩 Lazy Loading Engine ---
    async def get_tool_assets(index):
        if index in ui_cache:
            return ui_cache[index], actions_cache[index]

        ui, actions = build_base_tool_assets(lbl_clock=lbl_clock, dlg_loading=dlg_loading)
        TOOL_BUILDERS[index](ui, actions)

        ui_cache[index] = ui; actions_cache[index] = actions
        return ui, actions

    # --- 🏗️ View Builder ---
    content_area = ft.Column(expand=True)
    
    current_view_index = 0
    is_compact_layout = False

    async def update_view(index):
        nonlocal current_view_index
        current_view_index = index
        content_area.controls.clear(); ui, actions = await get_tool_assets(index)
        view = build_tool_view(
            index,
            ui,
            actions,
            current_version=CURRENT_VERSION,
            patch_notes=CURRENT_PATCH_NOTES,
            is_compact=is_compact_layout,
        )
        if isinstance(view, ft.Container): view.expand = True
        content_area.controls.append(view); await page.update_async()

    # --- 🧭 Sidebar Navigation ---
    def make_nav(idx):
        async def on_nav(e):
            if await guard_busy(): return
            await update_view(idx)
        return on_nav

    TOOL_BUILDERS = create_tool_builders(
        ToolBuildContext(
            ft=ft,
            page=page,
            update_view=update_view,
            guard_busy=guard_busy,
            set_busy=set_busy,
            safe_update=safe_update,
            show_toast=show_toast,
            current_fp_context=current_fp_context,
            fp_dir=fp_dir,
            fp_open=fp_open,
            fp_save=fp_save,
            btn_cancel_process=btn_cancel_process,
            lbl_modal_status=lbl_modal_status,
            dlg_loading=dlg_loading,
            get_extension=get_extension,
            list_files_to_process=list_files_to_process,
            process_file_split_streaming=process_file_split_streaming,
            generate_qr_base64=generate_qr_base64,
            search_json=search_json,
            is_base64_json=is_base64_json,
            json_to_csv_text=json_to_csv_text,
            csv_to_json_data=csv_to_json_data,
            compare_json=compare_json,
            epoch_to_local_datetime_text=epoch_to_local_datetime_text,
            ticks_to_local_datetime_text=ticks_to_local_datetime_text,
            build_password=build_password,
            process_hidden_char_file=process_hidden_char_file,
            clean_hidden_text=clean_hidden_text,
            find_binary_indices=find_binary_indices,
            get_text_diff=get_text_diff,
            decode_jwt=decode_jwt,
            optimize_image=optimize_image,
            color_primary=COLOR_PRIMARY,
            color_secondary=COLOR_SECONDARY,
            color_accent=COLOR_ACCENT,
            color_text=COLOR_TEXT,
            color_transparent=COLOR_TRANSPARENT,
            color_red_400=COLOR_RED_400,
            color_amber_300=COLOR_AMBER_300,
            color_blue_300=COLOR_BLUE_300,
            color_green_400=COLOR_GREEN_400,
            radius_md=RADIUS_MD,
        )
    )

    nav_buttons = {
        spec["id"]: nav_btn(spec["full_label"], spec["icon"], make_nav(spec["id"]))
        for spec in TOOL_SPECS
    }
    nav_controls.extend(nav_buttons.values())
    nav_labels = [
        (nav_buttons[spec["id"]], spec["full_label"], spec["compact_label"])
        for spec in TOOL_SPECS
    ]
    top_nav_buttons = [nav_buttons[spec["id"]] for spec in TOOL_SPECS if spec["sidebar"] == "top"]
    main_nav_buttons = [nav_buttons[spec["id"]] for spec in TOOL_SPECS if spec["sidebar"] == "main"]

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
            *top_nav_buttons,
            ft.Divider(color=BORDER_SUBTLE, height=40),
            ft.Column([
                *main_nav_buttons
            ], spacing=2, scroll=ft.ScrollMode.AUTO, expand=True),
        ], spacing=0),
        width=300,
        bgcolor=COLOR_SIDEBAR,
        padding=20,
    )

    async def apply_responsive_layout():
        nonlocal is_compact_layout
        width = page.width or page.window_width or 1280
        compact = width < RESPONSIVE_THRESHOLD
        layout_changed = compact != is_compact_layout
        is_compact_layout = compact
        sidebar.width = 220 if compact else 300
        sidebar.padding = 12 if compact else 20
        for button, full_label, compact_label in nav_labels:
            label_control = button.content.controls[1]
            label_control.value = compact_label if compact else full_label
            label_control.size = 12 if compact else 14
        await safe_update(sidebar)
        if layout_changed and content_area.controls:
            await update_view(current_view_index)

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
