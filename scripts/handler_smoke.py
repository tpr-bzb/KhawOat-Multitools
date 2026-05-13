import asyncio
import base64
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

import flet as ft

PROJECT_ROOT = Path(__file__).resolve().parent.parent
import sys

sys.path.insert(0, str(PROJECT_ROOT))

from handlers_basic import register_json_tool_handlers
from handlers_tools import register_merge_split_handlers


class FakeButton:
    def __init__(self):
        self.disabled = False
        self.on_click = None


class FakeDialog:
    def __init__(self):
        self.open = False


class FakePage:
    def __init__(self):
        self.dialog = None
        self.clipboard = None
        self.update_calls = 0

    async def update_async(self):
        self.update_calls += 1

    def set_clipboard(self, value):
        self.clipboard = value


def build_handler_deps(**overrides):
    page = overrides.pop("page", FakePage())
    deps = dict(
        ft=ft,
        page=page,
        guard_busy=lambda: _false_async(),
        set_busy=lambda value: _noop_async(),
        safe_update=lambda control: _noop_async(),
        show_toast=lambda message, ok=True: _noop_async(),
        current_fp_context={},
        fp_dir=SimpleNamespace(),
        fp_open=SimpleNamespace(),
        fp_save=SimpleNamespace(),
        btn_cancel_process=FakeButton(),
        lbl_modal_status=ft.Text(""),
        dlg_loading=FakeDialog(),
        get_extension=lambda value: ".csv" if value == "CSV" else "",
        list_files_to_process=lambda src_dir, src_type, src_ext: [],
        process_file_split_streaming=lambda **kwargs: {"total_rows": 0, "files_created": 0, "errors": []},
        generate_qr_base64=lambda value: "",
        search_json=lambda data, keyword: [],
        is_base64_json=lambda text: False,
        json_to_csv_text=lambda data: "",
        csv_to_json_data=lambda text: [],
        compare_json=lambda obj1, obj2: [],
        epoch_to_local_datetime_text=lambda value: "",
        ticks_to_local_datetime_text=lambda value: "",
        build_password=lambda *args: "",
        process_hidden_char_file=lambda *args: (None, ""),
        clean_hidden_text=lambda text, anomalies: text,
        find_binary_indices=lambda value: [],
        get_text_diff=lambda text1, text2: [],
        decode_jwt=lambda token: {},
        optimize_image=lambda *args: (False, ""),
        color_primary="#00ff99",
        color_secondary="#00ffaa",
        color_accent="#ffaa00",
        color_text="#ffffff",
        color_transparent="transparent",
        color_red_400="#ff5252",
        color_amber_300="#ffcc00",
        color_blue_300="#66ccff",
        color_green_400="#66ff66",
    )
    deps.update(overrides)
    return SimpleNamespace(**deps)


async def _noop_async():
    return None


async def _false_async():
    return False


async def test_json_handlers():
    toasts = []

    async def show_toast(message, ok=True):
        toasts.append((message, ok))

    ui = {
        "txt_line_numbers": ft.TextField(value="1"),
        "tree_container": ft.Column(),
        "txt_json_input": ft.TextField(value='{"name":"Alice","items":[1,2]}'),
        "txt_json_search": ft.TextField(value="items"),
    }
    actions = {}
    deps = build_handler_deps(
        show_toast=show_toast,
        search_json=lambda data, keyword: ["items"] if keyword == "items" else [],
        is_base64_json=lambda text: False,
        json_to_csv_text=lambda data: "name\nAlice\n",
        csv_to_json_data=lambda text: [{"name": "Alice"}],
        compare_json=lambda obj1, obj2: [] if obj1 == obj2 else ["diff"],
    )

    register_json_tool_handlers(ui, actions, deps=deps)

    await actions["run_fmt_json"](None)
    assert "    " in ui["txt_json_input"].value
    assert len(ui["tree_container"].controls) == 1

    await actions["run_search_json"](None)
    assert any("🔎 พบ" in message for message, _ok in toasts)

    encoded = base64.b64encode(b'{"ok":true}').decode("utf-8")
    ui["txt_json_input"].value = encoded
    await actions["run_b64_decode_json"](None)
    assert '"ok": true' in ui["txt_json_input"].value

    await actions["run_json_to_csv"](None)
    assert "name" in ui["txt_json_input"].value

    ui["txt_json_input"].value = "name\nAlice\n"
    await actions["run_csv_to_json"](None)
    assert '"name": "Alice"' in ui["txt_json_input"].value

    await actions["btn_copy_json"](None)
    assert deps.page.clipboard == ui["txt_json_input"].value

    await actions["run_clear_json"](None)
    assert ui["txt_json_input"].value == ""
    assert ui["txt_line_numbers"].value == "1"


async def test_merge_split_success_and_cancel():
    busy_values = []

    async def set_busy(value):
        busy_values.append(value)

    with tempfile.TemporaryDirectory() as src_dir:
        ui = {
            "txt_src_dir": ft.TextField(value=src_dir),
            "dd_src_ext": ft.Dropdown(value="CSV"),
            "dd_out_ext": ft.Dropdown(value="CSV"),
            "txt_base_name": ft.TextField(value="batch"),
            "txt_lines": ft.TextField(value="1,000"),
            "chk_header": ft.Checkbox(value=True),
            "lbl_split_status": ft.Text(""),
            "lbl_split_summary": ft.Text(""),
        }
        actions = {}
        deps = build_handler_deps(
            set_busy=set_busy,
            list_files_to_process=lambda src_dir, src_type, src_ext: ["a.csv", "b.csv"],
            process_file_split_streaming=lambda **kwargs: {
                "total_rows": 2500,
                "files_created": 3,
                "errors": [],
            },
        )

        register_merge_split_handlers(ui, actions, deps=deps)
        await actions["run_split"](None)

        assert ui["lbl_split_status"].value.startswith("✅")
        assert "2 ไฟล์" in ui["lbl_split_summary"].value
        assert busy_values == [True, False]

    async def set_busy_cancel(value):
        return None

    def cancellable_process(**kwargs):
        for _index in range(50):
            if kwargs["cancel_check"]():
                return {"total_rows": 100, "files_created": 1, "errors": []}
            time.sleep(0.01)
            kwargs["status_callback"]("working")
        return {"total_rows": 100, "files_created": 1, "errors": []}

    with tempfile.TemporaryDirectory() as src_dir:
        ui = {
            "txt_src_dir": ft.TextField(value=src_dir),
            "dd_src_ext": ft.Dropdown(value="CSV"),
            "dd_out_ext": ft.Dropdown(value="CSV"),
            "txt_base_name": ft.TextField(value="batch"),
            "txt_lines": ft.TextField(value="500"),
            "chk_header": ft.Checkbox(value=True),
            "lbl_split_status": ft.Text(""),
            "lbl_split_summary": ft.Text(""),
        }
        actions = {}
        deps = build_handler_deps(
            set_busy=set_busy_cancel,
            list_files_to_process=lambda src_dir, src_type, src_ext: ["a.csv"],
            process_file_split_streaming=cancellable_process,
        )

        register_merge_split_handlers(ui, actions, deps=deps)
        split_task = asyncio.create_task(actions["run_split"](None))
        await asyncio.sleep(0.05)
        await deps.btn_cancel_process.on_click(None)
        await split_task

        assert ui["lbl_split_status"].value == "⚠️ ผู้ใช้ยกเลิก"
        assert "🛑 หยุดที่:" in ui["lbl_split_summary"].value
        assert deps.btn_cancel_process.disabled is True


async def main():
    await test_json_handlers()
    await test_merge_split_success_and_cancel()
    print("handler_smoke_ok")


if __name__ == "__main__":
    asyncio.run(main())
