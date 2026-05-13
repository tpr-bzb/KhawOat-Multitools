from dataclasses import dataclass
from typing import Any, Callable


@dataclass(slots=True)
class ToolBuildContext:
    ft: Any
    page: Any
    update_view: Callable
    guard_busy: Callable
    set_busy: Callable
    safe_update: Callable
    show_toast: Callable
    current_fp_context: dict
    fp_dir: Any
    fp_open: Any
    fp_save: Any
    btn_cancel_process: Any
    lbl_modal_status: Any
    dlg_loading: Any
    get_extension: Callable
    list_files_to_process: Callable
    process_file_split_streaming: Callable
    generate_qr_base64: Callable
    search_json: Callable
    is_base64_json: Callable
    json_to_csv_text: Callable
    csv_to_json_data: Callable
    compare_json: Callable
    epoch_to_local_datetime_text: Callable
    ticks_to_local_datetime_text: Callable
    build_password: Callable
    process_hidden_char_file: Callable
    clean_hidden_text: Callable
    find_binary_indices: Callable
    get_text_diff: Callable
    decode_jwt: Callable
    optimize_image: Callable
    color_primary: str
    color_secondary: str
    color_accent: str
    color_text: str
    color_transparent: str
    color_red_400: str
    color_amber_300: str
    color_blue_300: str
    color_green_400: str
    radius_md: int

    def __getitem__(self, key: str) -> Any:
        legacy_map = {
            "COLOR_PRIMARY": "color_primary",
            "COLOR_SECONDARY": "color_secondary",
            "COLOR_ACCENT": "color_accent",
            "COLOR_TEXT": "color_text",
            "COLOR_TRANSPARENT": "color_transparent",
            "COLOR_RED_400": "color_red_400",
            "COLOR_AMBER_300": "color_amber_300",
            "COLOR_BLUE_300": "color_blue_300",
            "COLOR_GREEN_400": "color_green_400",
            "RADIUS_MD": "radius_md",
        }
        return getattr(self, legacy_map.get(key, key))


@dataclass(slots=True)
class HandlerContext:
    ft: Any
    page: Any
    guard_busy: Callable
    set_busy: Callable
    safe_update: Callable
    show_toast: Callable
    current_fp_context: dict
    fp_dir: Any
    fp_open: Any
    fp_save: Any
    btn_cancel_process: Any
    lbl_modal_status: Any
    dlg_loading: Any
    get_extension: Callable
    list_files_to_process: Callable
    process_file_split_streaming: Callable
    generate_qr_base64: Callable
    search_json: Callable
    is_base64_json: Callable
    json_to_csv_text: Callable
    csv_to_json_data: Callable
    compare_json: Callable
    epoch_to_local_datetime_text: Callable
    ticks_to_local_datetime_text: Callable
    build_password: Callable
    process_hidden_char_file: Callable
    clean_hidden_text: Callable
    find_binary_indices: Callable
    get_text_diff: Callable
    decode_jwt: Callable
    optimize_image: Callable
    color_primary: str
    color_secondary: str
    color_accent: str
    color_text: str
    color_transparent: str
    color_red_400: str
    color_amber_300: str
    color_blue_300: str
    color_green_400: str

    @classmethod
    def from_build_context(cls, ctx: ToolBuildContext) -> "HandlerContext":
        return cls(
            ft=ctx.ft,
            page=ctx.page,
            guard_busy=ctx.guard_busy,
            set_busy=ctx.set_busy,
            safe_update=ctx.safe_update,
            show_toast=ctx.show_toast,
            current_fp_context=ctx.current_fp_context,
            fp_dir=ctx.fp_dir,
            fp_open=ctx.fp_open,
            fp_save=ctx.fp_save,
            btn_cancel_process=ctx.btn_cancel_process,
            lbl_modal_status=ctx.lbl_modal_status,
            dlg_loading=ctx.dlg_loading,
            get_extension=ctx.get_extension,
            list_files_to_process=ctx.list_files_to_process,
            process_file_split_streaming=ctx.process_file_split_streaming,
            generate_qr_base64=ctx.generate_qr_base64,
            search_json=ctx.search_json,
            is_base64_json=ctx.is_base64_json,
            json_to_csv_text=ctx.json_to_csv_text,
            csv_to_json_data=ctx.csv_to_json_data,
            compare_json=ctx.compare_json,
            epoch_to_local_datetime_text=ctx.epoch_to_local_datetime_text,
            ticks_to_local_datetime_text=ctx.ticks_to_local_datetime_text,
            build_password=ctx.build_password,
            process_hidden_char_file=ctx.process_hidden_char_file,
            clean_hidden_text=ctx.clean_hidden_text,
            find_binary_indices=ctx.find_binary_indices,
            get_text_diff=ctx.get_text_diff,
            decode_jwt=ctx.decode_jwt,
            optimize_image=ctx.optimize_image,
            color_primary=ctx.color_primary,
            color_secondary=ctx.color_secondary,
            color_accent=ctx.color_accent,
            color_text=ctx.color_text,
            color_transparent=ctx.color_transparent,
            color_red_400=ctx.color_red_400,
            color_amber_300=ctx.color_amber_300,
            color_blue_300=ctx.color_blue_300,
            color_green_400=ctx.color_green_400,
        )
