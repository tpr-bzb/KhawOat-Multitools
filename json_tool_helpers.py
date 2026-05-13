import flet as ft

from tool_context import HandlerContext


async def sync_json_line_numbers(ui: dict, deps: HandlerContext) -> None:
    line_count = len(ui["txt_json_input"].value.split("\n"))
    lines = "\n".join(str(index) for index in range(1, line_count + 1))
    if ui["txt_line_numbers"].value != lines:
        ui["txt_line_numbers"].value = lines
        await deps.safe_update(ui["txt_line_numbers"])


async def reset_json_tool_state(ui: dict, deps: HandlerContext) -> None:
    ui["txt_json_input"].value = ""
    ui["txt_line_numbers"].value = "1"
    ui["tree_container"].controls.clear()
    await deps.safe_update(ui["txt_json_input"])
    await deps.safe_update(ui["txt_line_numbers"])
    await deps.safe_update(ui["tree_container"])


def build_json_diff_controls(diffs: list[str], deps: HandlerContext) -> list:
    if not diffs:
        return [
            ft.Text(
                "✅ JSON ทั้งสองชุดมีโครงสร้างและค่าเหมือนกัน!",
                color=deps.color_secondary,
                weight="bold",
            )
        ]

    controls = [
        ft.Text(
            f"🔎 พบจุดที่ต่างกัน {len(diffs)} รายการ:",
            color=deps.color_accent,
            weight="bold",
        )
    ]
    controls.extend(ft.Text(f"• {diff}", size=13) for diff in diffs)
    return controls


def build_csv_tree_notice():
    return ft.Text("📊 แปลงเป็น CSV เรียบร้อยแล้ว (Tree View ไม่รองรับ CSV)", color="orange")


async def focus_json_error_line(ui: dict, error_line: int, deps: HandlerContext) -> None:
    lines = ui["txt_json_input"].value.split("\n")
    position = sum(len(line) + 1 for line in lines[: error_line - 1])
    ui["txt_json_input"].focus()
    ui["txt_json_input"].selection_start = position
    ui["txt_json_input"].selection_end = position + len(lines[error_line - 1])
    await deps.safe_update(ui["txt_json_input"])


async def open_json_diff_dialog(
    deps: HandlerContext,
    compare_input: ft.Control,
    on_compare,
) -> None:
    dialog = ft.AlertDialog(
        title=ft.Text("🔍 JSON Diff Tool", weight="bold"),
        content=ft.Container(content=compare_input, width=600),
        actions=[],
    )

    async def close_dialog(_event):
        dialog.open = False
        await deps.page.update_async()

    async def handle_compare(event):
        await on_compare(event, dialog)

    dialog.actions = [
        ft.TextButton("เปรียบเทียบ", on_click=handle_compare),
        ft.TextButton("ยกเลิก", on_click=close_dialog),
    ]
    deps.page.dialog = dialog
    dialog.open = True
    await deps.page.update_async()
