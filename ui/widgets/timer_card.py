from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGraphicsDropShadowEffect,
)
from PySide6.QtCore import (
    Qt, QTimer, Signal, QMimeData, QPoint,
    QPropertyAnimation, QEasingCurve, Property, QSize,
)
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor, QIcon

from ui.widgets.circle_timer import CircleTimer
from config import (
    ASSETS_DIR,
    SHADOW_BLUR_NORMAL, SHADOW_OFFSET_NORMAL, SHADOW_ALPHA_NORMAL,
    SHADOW_BLUR_HOVER,  SHADOW_OFFSET_HOVER,  SHADOW_ALPHA_HOVER,
    CARD_HEIGHT, CARD_MIN_WIDTH, CARD_BORDER_R,
    BTN_ICON_SIZE, BTN_ROUND_SIZE, BTN_ROUND_RADIUS,
    CARD_HOVER_ANIM_MS, CARD_HOVER_OFFSET,
    DRAG_MIN_DISTANCE, DRAG_OPACITY,
    settings_manager,
)


class TimerCard(QWidget):
    favoriteChanged = Signal(object)

    def __init__(self, label: str, seconds: int, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedHeight(CARD_HEIGHT)
        self.setMinimumWidth(CARD_MIN_WIDTH)

        self._offset_y       = 0
        self._total          = seconds
        self._remaining      = seconds
        self._is_favorite    = False
        self._drag_start_pos = QPoint()

        # Shadow
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        self._shadow.setOffset(0, SHADOW_OFFSET_NORMAL)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_NORMAL))
        self.setGraphicsEffect(self._shadow)

        # Hover animation
        self._anim = QPropertyAnimation(self, b"offsetY")
        self._anim.setDuration(CARD_HOVER_ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # Tick timer
        self._ticker = QTimer()
        self._ticker.setInterval(1000)
        self._ticker.timeout.connect(self._tick)

        # Icons
        self._icon_play  = QIcon(str(ASSETS_DIR / "play.svg"))
        self._icon_pause = QIcon(str(ASSETS_DIR / "pause.svg"))
        self._icon_reset = QIcon(str(ASSETS_DIR / "reset.svg"))

        # Layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(8, 0, 8, 0)

        self.title = QLabel(label)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(self.title, stretch=1)

        self.circle = CircleTimer()
        self.circle.set_progress(self._remaining, self._total)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_btn = QPushButton()
        self.start_btn.setIcon(self._icon_play)
        self.start_btn.setIconSize(QSize(BTN_ICON_SIZE, BTN_ICON_SIZE))
        self.start_btn.setFixedSize(BTN_ROUND_SIZE, BTN_ROUND_SIZE)
        self.start_btn.clicked.connect(self._toggle)

        self.reset_btn = QPushButton()
        self.reset_btn.setIcon(self._icon_reset)
        self.reset_btn.setIconSize(QSize(BTN_ICON_SIZE, BTN_ICON_SIZE))
        self.reset_btn.setFixedSize(BTN_ROUND_SIZE, BTN_ROUND_SIZE)
        self.reset_btn.clicked.connect(self._reset)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(top_layout)
        layout.addWidget(self.circle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(btn_layout)

        self._apply_styles()

    # Theming

    def _apply_styles(self) -> None:
        """Build all stylesheets from the live theme. Call after theme change."""
        t = settings_manager.theme

        self.setStyleSheet(f"""
            TimerCard {{
                background-color: {t.bg_card};
                border-radius: {CARD_BORDER_R}px;
            }}
        """)

        self.title.setStyleSheet(
            f"color: {t.text_secondary}; font-size: 14px;"
        )

        btn_style = f"""
            QPushButton {{
                border-radius: {BTN_ROUND_RADIUS}px;
                background-color: {t.bg_btn};
                border: none;
            }}
            QPushButton:hover {{ background-color: {t.bg_btn_hover}; }}
        """
        self.start_btn.setStyleSheet(btn_style)
        self.reset_btn.setStyleSheet(btn_style)

    def refresh_theme(self) -> None:
        """Public slot — connect to a themeChanged signal to hot-reload colours."""
        self._apply_styles()

    # Drag & Drop 

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if (event.position().toPoint() - self._drag_start_pos).manhattanLength() < DRAG_MIN_DISTANCE:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText("timer_card")
        drag.setMimeData(mime)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        self.render(pixmap, QPoint(), self.rect())

        faded = QPixmap(pixmap.size())
        faded.fill(Qt.GlobalColor.transparent)
        painter = QPainter(faded)
        painter.setOpacity(DRAG_OPACITY)
        painter.drawPixmap(QPoint(), pixmap)
        painter.end()

        drag.setPixmap(faded)
        drag.setHotSpot(self._drag_start_pos)
        drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    # Hover animation

    @Property(int)
    def offsetY(self) -> int:
        return self._offset_y

    @offsetY.setter
    def offsetY(self, value: int) -> None:
        self._offset_y = value
        self.setContentsMargins(0, max(0, -value), 0, max(0, value))

    def enterEvent(self, event) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset_y)
        self._anim.setEndValue(CARD_HOVER_OFFSET)
        self._shadow.setBlurRadius(SHADOW_BLUR_HOVER)
        self._shadow.setOffset(0, SHADOW_OFFSET_HOVER)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_HOVER))
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._anim.stop()
        self._anim.setStartValue(self._offset_y)
        self._anim.setEndValue(0)
        self._shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        self._shadow.setOffset(0, SHADOW_OFFSET_NORMAL)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_NORMAL))
        self._anim.start()
        super().leaveEvent(event)

    # Timer logic

    def is_favorite(self) -> bool:
        return self._is_favorite

    def _toggle(self) -> None:
        if self._ticker.isActive():
            self._ticker.stop()
            self.start_btn.setIcon(self._icon_play)
        else:
            self._ticker.start()
            self.start_btn.setIcon(self._icon_pause)
            self._tick()

    def _reset(self) -> None:
        self._ticker.stop()
        self.start_btn.setIcon(self._icon_play)
        self._remaining = self._total
        self.circle.set_progress(self._remaining, self._total)

    def _tick(self) -> None:
        self._remaining = max(0, self._remaining - 1)
        if self._remaining == 0:
            self._ticker.stop()
            self.start_btn.setIcon(self._icon_play)
        self.circle.set_progress(self._remaining, self._total)