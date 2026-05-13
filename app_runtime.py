import flet as ft


class UiRuntime:
    def __init__(self, page: ft.Page):
        self.page = page
        self.busy = False
        self.nav_controls: list[ft.Control] = []

    async def safe_update(self, control):
        if not control:
            return
        try:
            if hasattr(control, "page") and control.page:
                if hasattr(control, "update_async"):
                    await control.update_async()
                else:
                    control.update()
            else:
                await self.page.update_async()
        except Exception:
            pass

    async def set_busy(self, value: bool):
        self.busy = value
        for control in self.nav_controls:
            control.disabled = value
            await self.safe_update(control)

    async def show_toast(self, message: str, *, ok: bool = True, success_color: str = "#4caf50"):
        self.page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=success_color if ok else "red",
            open=True,
        )
        await self.page.update_async()

    async def close_banner(self, _event):
        self.page.banner.open = False
        await self.page.update_async()


def ensure_page_update_async(page: ft.Page):
    if hasattr(page, "update_async"):
        return

    async def _page_update_async():
        page.update()

    page.update_async = _page_update_async
