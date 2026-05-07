import flet as ft

# --- 🎨 Midnight Earth Tone Palette ---
COLOR_BG = "#0D0F0D"
COLOR_SIDEBAR = "#141A14"
COLOR_CARD = "#1E231E"
COLOR_PRIMARY = "#DDA15E"
COLOR_SECONDARY = "#81B29A"
COLOR_ACCENT = "#BC6C25"
COLOR_TEXT = "#FDFBF7"


def configure_page(page: ft.Page):
    page.title = f"KhawOat Multi-Tools"
    page.bgcolor = COLOR_BG
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 1280   # แก้ตัวเลขตรงนี้เพื่อเปลี่ยนความกว้าง
    page.window_height = 800   # แก้ตัวเลขตรงนี้เพื่อเปลี่ยนความสูง

    # (เพิ่มเติม) หากต้องการล็อกขนาดไม่ให้ย่อ/ขยายได้เกินที่กำหนด
    page.window_min_width = 1000
    page.window_min_height = 700
    
    # หรือถ้าอยากให้เปิดมาแล้วขยายเต็มหน้าจอทันที (Maximized)
    # page.window_maximized = True

    page.update()
