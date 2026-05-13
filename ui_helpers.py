from dataclasses import dataclass
from typing import Any, Awaitable, Callable


@dataclass(slots=True)
class LoadingDialogControls:
    dialog: Any
    cancel_button: Any
    status_label: Any


@dataclass(slots=True)
class FilePickerHub:
    current_context: dict
    directory_picker: Any
    open_picker: Any
    save_picker: Any


def build_loading_dialog(*, ft, color_primary: str, color_accent: str) -> LoadingDialogControls:
    cancel_button = ft.ElevatedButton("❌ ยกเลิก", color="white", bgcolor="#8B0000")
    status_label = ft.Text("กำลังเตรียมการ...", color="white", text_align=ft.TextAlign.CENTER)
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("⏳ System Processing", weight="bold", color=color_primary),
        content=ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(color=color_accent, stroke_width=5),
                    ft.Container(height=10),
                    status_label,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            height=120,
            width=300,
        ),
        actions=[ft.Row([cancel_button], alignment=ft.MainAxisAlignment.CENTER)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    return LoadingDialogControls(dialog=dialog, cancel_button=cancel_button, status_label=status_label)


def build_file_picker_hub(
    *,
    ft,
    page,
    safe_update: Callable[[Any], Awaitable[None]],
) -> FilePickerHub:
    current_context = {}

    async def on_result(event):
        if not event.path and not event.files:
            return

        context = current_context.get(event.control)
        if not context:
            return

        target_ui = context.get("ui")
        if context["type"] == "dir" and event.path:
            if target_ui is not None:
                target_ui.value = event.path
        elif context["type"] == "open" and event.files:
            if target_ui is not None:
                target_ui.value = event.files[0].path
        elif context["type"] == "save":
            save_path = event.path or (event.files[0].path if event.files else None)
            if save_path and "callback" in context:
                await context["callback"](save_path)
            return

        if target_ui is not None:
            await safe_update(target_ui)

    directory_picker = ft.FilePicker(on_result=on_result)
    open_picker = ft.FilePicker(on_result=on_result)
    save_picker = ft.FilePicker(on_result=on_result)
    page.overlay.extend([directory_picker, open_picker, save_picker])

    return FilePickerHub(
        current_context=current_context,
        directory_picker=directory_picker,
        open_picker=open_picker,
        save_picker=save_picker,
    )
