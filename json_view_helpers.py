import json

import flet as ft

from tool_context import HandlerContext


def build_json_tree(data, deps: HandlerContext, label="root", highlighted_paths=None):
    highlighted_paths = highlighted_paths or []
    is_highlighted = label in highlighted_paths or any(
        path.startswith(label + ".") or path.startswith(label + "[")
        for path in highlighted_paths
    )
    text_color = deps.color_primary if is_highlighted else deps.color_amber_300

    if isinstance(data, dict):
        return ft.ExpansionTile(
            title=ft.Text(label, color=text_color, weight="bold" if is_highlighted else "normal"),
            subtitle=ft.Text(f"{{ {len(data)} items }}", size=10, italic=True),
            initially_expanded=is_highlighted,
            controls=[
                build_json_tree(value, deps, f"{label}.{key}" if label != "root" else key, highlighted_paths)
                for key, value in data.items()
            ],
        )

    if isinstance(data, list):
        return ft.ExpansionTile(
            title=ft.Text(
                label,
                color=deps.color_primary if is_highlighted else deps.color_blue_300,
                weight="bold" if is_highlighted else "normal",
            ),
            subtitle=ft.Text(f"[ {len(data)} items ]", size=10, italic=True),
            initially_expanded=is_highlighted,
            controls=[
                build_json_tree(
                    value,
                    deps,
                    f"{label}[{index}]" if label != "root" else f"[{index}]",
                    highlighted_paths,
                )
                for index, value in enumerate(data)
            ],
        )

    return ft.ListTile(
        title=ft.Text(
            f"{label}: ",
            size=13,
            weight="bold" if is_highlighted else "normal",
            color=deps.color_primary if is_highlighted else deps.color_text,
        ),
        trailing=ft.Text(
            f"{data}",
            color=deps.color_primary if is_highlighted else deps.color_green_400,
            selectable=True,
        ),
        dense=True,
    )


def build_json_tree_from_text(raw_value: str, deps: HandlerContext):
    value = raw_value.strip()
    if not value:
        return ft.Text("⚠️ ไม่มีข้อมูล", color="orange")

    try:
        data = json.loads(value)
    except Exception as exc:
        return ft.Text(f"❌ JSON Error: {exc}", color="red")

    return build_json_tree(data, deps)
