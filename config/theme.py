from dataclasses import dataclass


@dataclass
class ThemeConfig:
    """All visual theme values. Serialised to/from JSON by SettingsManager."""

    # ── Backgrounds ───────────────────────────────────────────
    bg_primary:       str = "#191921"
    bg_card:          str = "#262628"
    bg_surface:       str = "#2d2d3a"
    bg_btn:           str = "#323234"
    bg_btn_hover:     str = "#3a3a3c"
    bg_nav:           str = "#2a2a3e"
    bg_nav_hover:     str = "#3a3a55"
    bg_nav_active:    str = "#2e2e50"
    bg_nav_pressed:   str = "#4a4a6a"
    bg_surface_hover: str = "#3d3d4a"

    # ── Accent ────────────────────────────────────────────────
    accent:          str = "#1D9E75"
    accent_hover:    str = "#17835f"
    accent_disabled: str = "#1a3d30"

    # ── Text ──────────────────────────────────────────────────
    text_primary:   str = "#ffffff"
    text_secondary: str = "#aaaaaa"
    text_muted:     str = "#888888"
    text_disabled:  str = "#555555"

    # ── Scrollbar ─────────────────────────────────────────────
    scrollbar_bg:    str = "#1e1e24"
    scrollbar_track: str = "#252530"
    scrollbar_thumb: str = "#444454"
    scrollbar_hover: str = "#575770"

    # ── Overlays ──────────────────────────────────────────────
    # Semi-transparent hover used on ghost/icon buttons (e.g. TimeInput arrows)
    bg_overlay_hover: str = "rgba(255, 255, 255, 30)"


# ── Default instance ──────────────────────────────────────────
_t = ThemeConfig()

# Flat re-exports — `from config import COLOR_ACCENT` keeps working everywhere.
# These reflect the DEFAULT theme; for a live/mutable theme use settings_manager.theme
COLOR_BG_PRIMARY       = _t.bg_primary
COLOR_BG_CARD          = _t.bg_card
COLOR_BG_SURFACE       = _t.bg_surface
COLOR_BG_BTN           = _t.bg_btn
COLOR_BG_BTN_HOVER     = _t.bg_btn_hover
COLOR_BG_NAV           = _t.bg_nav
COLOR_BG_NAV_HOVER     = _t.bg_nav_hover
COLOR_BG_NAV_ACTIVE    = _t.bg_nav_active
COLOR_BG_NAV_PRESSED   = _t.bg_nav_pressed
COLOR_BG_SURFACE_HOVER = _t.bg_surface_hover

COLOR_ACCENT           = _t.accent
COLOR_ACCENT_HOVER     = _t.accent_hover
COLOR_ACCENT_DISABLED  = _t.accent_disabled

COLOR_TEXT_PRIMARY     = _t.text_primary
COLOR_TEXT_SECONDARY   = _t.text_secondary
COLOR_TEXT_MUTED       = _t.text_muted
COLOR_TEXT_DISABLED    = _t.text_disabled

COLOR_SCROLLBAR_BG      = _t.scrollbar_bg
COLOR_SCROLLBAR_TRACK   = _t.scrollbar_track
COLOR_SCROLLBAR_THUMB   = _t.scrollbar_thumb
COLOR_SCROLLBAR_HOVER   = _t.scrollbar_hover
COLOR_BG_OVERLAY_HOVER  = _t.bg_overlay_hover