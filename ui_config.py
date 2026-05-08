import flet as ft


def _get_colors_module():
    return getattr(ft, "colors", getattr(ft, "Colors", None))


def _transparent_color():
    colors_mod = _get_colors_module()
    return getattr(colors_mod, "TRANSPARENT", "transparent")


def _with_opacity(opacity: float, color: str):
    colors_mod = _get_colors_module()
    if colors_mod and hasattr(colors_mod, "with_opacity"):
        return colors_mod.with_opacity(opacity, color)
    return color

# --- 🎨 Velvet Amethyst Pro Palette ---
# Base Colors
COLOR_BG = "#10002B"          # Deep Velvet Obsidian
COLOR_SIDEBAR = "#160036"      # Slightly lighter for contrast
COLOR_CARD = "#240046"         # Rich Royal Purple
COLOR_SURFACE = "#3C096C"      # Amethyst Elevation
COLOR_PANEL = "#2D0A4F"        # Rich panel surface
COLOR_PANEL_ALT = "#35105C"    # Alternate panel surface

# Brand Colors
COLOR_PRIMARY = "#9D4EDD"      # Bright Amethyst
COLOR_PRIMARY_MUTED = "#7B2CBF"
COLOR_SECONDARY = "#E0AAFF"    # Soft Lavender
COLOR_ACCENT = "#FFD700"       # Champagne Gold
COLOR_ERROR = "#FF4D6D"        # Raspberry Red (fits purple better)
COLOR_SUCCESS = "#72EFDD"      # Aqua Teal

# Text Colors
COLOR_TEXT = "#FDFBF7"         # Warm white
COLOR_TEXT_DIM = "#A0A0A0"     # Gray for secondary info
COLOR_TEXT_MUTED = "#606060"   # Dim gray for hints

# --- 📐 Design Tokens ---
# Border Radius
RADIUS_SM = 8
RADIUS_MD = 12
RADIUS_LG = 16

# Spacing
SPACE_XS = 5
SPACE_SM = 10
SPACE_MD = 20
SPACE_LG = 30
SPACE_XL = 40

# Shadows & Depth (Flet doesn't have native box-shadow yet, but we use subtle borders)
BORDER_SUBTLE = "white10"
BORDER_FOCUS = COLOR_PRIMARY

# --- 📱 Responsive Config ---
RESPONSIVE_THRESHOLD = 900 # Width at which UI should simplify

# --- 🔡 Typography ---
FONT_SIZE_H1 = 28
FONT_SIZE_H2 = 22
FONT_SIZE_H3 = 18
FONT_SIZE_BODY = 14
FONT_SIZE_SMALL = 12
FONT_SIZE_TINY = 11

def configure_page(page: ft.Page):
    page.title = "KhawOat Multi-Tools Pro"
    page.bgcolor = COLOR_BG
    page.theme_mode = ft.ThemeMode.DARK

    # Keep theme setup tolerant to nearby Flet API changes.
    theme_kwargs = {"color_scheme_seed": COLOR_PRIMARY}

    if hasattr(ft, "ThemeVisualDensity"):
        theme_kwargs["visual_density"] = ft.ThemeVisualDensity.COMFORTABLE

    if hasattr(ft, "ScrollbarTheme"):
        theme_kwargs["scrollbar_theme"] = ft.ScrollbarTheme(
            track_color=_transparent_color(),
            thumb_color=_with_opacity(0.1, COLOR_TEXT),
            thickness=8,
            radius=10,
        )

    if hasattr(ft, "Theme"):
        page.theme = ft.Theme(**theme_kwargs)

    page.window_width = 1280
    page.window_height = 800
    page.window_min_width = 800
    page.window_min_height = 600
    
    page.update()
