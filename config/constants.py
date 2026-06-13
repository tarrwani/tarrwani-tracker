import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent.parent
INTERFACE_DIR = BASE_DIR / "ui"
ASSETS_DIR    = BASE_DIR / "assets"

# ── App ───────────────────────────────────────────────────────
APP_NAME    = "Tarrwani Tracker"
APP_VERSION = "0.1.2"
ICON_PATH   = ASSETS_DIR / "icon.png"
APP_BORDER_RADIUS = 12

# ── Database ──────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     os.getenv("DB_PORT", 54321),
    "dbname":   os.getenv("DB_NAME", "timetracker"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# ── Shadow ────────────────────────────────────────────────────
SHADOW_BLUR_NORMAL   = 12
SHADOW_OFFSET_NORMAL = 4
SHADOW_ALPHA_NORMAL  = 80
SHADOW_BLUR_HOVER    = 28
SHADOW_OFFSET_HOVER  = 10
SHADOW_ALPHA_HOVER   = 140

# ── Card ──────────────────────────────────────────────────────
CARD_HEIGHT    = 320
CARD_MIN_WIDTH = 270
CARD_BORDER_R  = 12

# ── Buttons ───────────────────────────────────────────────────
BTN_ICON_SIZE    = 20
BTN_ROUND_SIZE   = 40
BTN_ROUND_RADIUS = 20

BTN_REMOVE_SIZE       = 15
BTN_REMOVE_ROUND_SIZE = 30
BTN_REMOVE_RADIUS     = 30

# ── Sidebar ───────────────────────────────────────────────────
SIDEBAR_EXPANDED       = 260
SIDEBAR_COLLAPSED      = 70
SIDEBAR_ANIM_MS        = 280
SIDEBAR_TEXT_THRESHOLD = 120

# ── Add button ────────────────────────────────────────────────
ADD_BTN_SIZE   = 36
ADD_BTN_RADIUS = 18

# ── CircleTimer ───────────────────────────────────────────────
CIRCLE_TIMER_SIZE      = 200
CIRCLE_TIMER_THICKNESS = 8
CIRCLE_TIMER_ANIM_MS   = 1000
CIRCLE_TIMER_FONT_SIZE = 20
CIRCLE_FONT_FAMILY     = "Segoe UI"

# ── Dialog ────────────────────────────────────────────────────
DIALOG_W            = 300
DIALOG_H            = 400
DIALOG_PADDING      = 24
DIALOG_SPACING      = 16
DIALOG_INPUT_RADIUS = 8
DIALOG_INPUT_FONT   = 14

# ── TimeInput ─────────────────────────────────────────────────
TIME_INPUT_BTN_W      = 40
TIME_INPUT_BTN_H      = 24
TIME_INPUT_FONT       = 32
TIME_INPUT_LABEL_FONT = 12
TIME_INPUT_ARROW_FONT = 10

# ── Grid ──────────────────────────────────────────────────────
GRID_SPACING = 16

# ── Drag & Drop ───────────────────────────────────────────────
DRAG_MIN_DISTANCE = 12
DRAG_OPACITY      = 0.75

# ── Hover animation ───────────────────────────────────────────
CARD_HOVER_ANIM_MS = 180
CARD_HOVER_OFFSET  = -6

# ── Window / resize ───────────────────────────────────────────
# Зона ресайза делится пополам: RESIZE_OUTER px снаружи визуального края
# (прозрачная рамка окна) и RESIZE_INNER px внутри (видимая зона).
RESIZE_MARGIN = 20
RESIZE_OUTER  = RESIZE_MARGIN // 2   # прозрачная рамка окна
RESIZE_INNER  = RESIZE_MARGIN // 2   # видимая часть зоны

TITLEBAR_H    = 36    # высота заголовка окна (px)

# ── Overlay sidebar ───────────────────────────────────────────
# Ширина оверлейного сайдбара в режиме force-collapsed.
# Реальная ширина ограничена снизу SIDEBAR_EXPANDED и сверху этим значением,
# и дополнительно не превышает 78% от ширины окна (см. _overlay_target_width).
OVERLAY_WIDTH = 220