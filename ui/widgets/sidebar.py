from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve, Signal, QSize
from PySide6.QtGui import QIcon
from config import (
    COLOR_SIDEBAR, COLOR_BG_NAV, COLOR_BG_NAV_ACTIVE,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    SIDEBAR_EXPANDED, SIDEBAR_COLLAPSED,
    SIDEBAR_ANIM_MS, SIDEBAR_TEXT_THRESHOLD, ASSETS_DIR,
    APP_BORDER_RADIUS # ИЗМЕНЕНИЕ: Импортировали радиус скругления из конфига
)

class SidebarWidget(QWidget):
    view_changed = Signal(int)
    _NAV_ITEMS = [
        (0, "focus", "Периоды фокусировки"),
        (1, "statistics", "Статистика"),
        (2, "hourglass", "Марафон"),
    ]
    def __init__(self):
        super().__init__()

        self.setFixedWidth(SIDEBAR_COLLAPSED)
        
        self.setStyleSheet(f"""
            background-color: {COLOR_SIDEBAR};
            border-top-left-radius: {APP_BORDER_RADIUS}px;
            border-bottom-left-radius: {APP_BORDER_RADIUS}px;
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self._expanded      = False
        self._animating     = False
        self._current_idx   = 0

        self._buttons: list[QPushButton] = []
        self._setup_ui()
        self._setup_animation()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 42, 10, 10)
        layout.setSpacing(4)

        style = self._btn_style()
        for idx, icon, label in self._NAV_ITEMS:
            btn = QPushButton()
            btn.setIcon(QIcon(str(ASSETS_DIR / f"{icon}.svg")))
            btn.setIconSize(QSize(20, 20))
            btn.setCheckable(True)
            btn.setChecked(idx == self._current_idx)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(style)
            btn.clicked.connect(lambda _checked, i=idx: self._on_btn_clicked(i))
            layout.addWidget(btn)
            self._buttons.append(btn)
        
        layout.addStretch()

    def _btn_style(self) -> str:
        return f"""
            QPushButton {{
                text-align: left;
                padding: 10px 14px;
                background: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                font-size: 15px;
            }}
            QPushButton:hover   {{ background: {COLOR_BG_NAV};        color: {COLOR_TEXT_PRIMARY}; }}
            QPushButton:checked {{ background: {COLOR_BG_NAV_ACTIVE}; color: {COLOR_TEXT_PRIMARY}; }}
        """
    
    def _on_btn_clicked(self, index: int):
        self.set_active(index)
        self.view_changed.emit(index)

    def _setup_animation(self):
        self._anim = QVariantAnimation()
        self._anim.setDuration(SIDEBAR_ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.finished.connect(lambda: setattr(self, "_animating", False))

    def _on_anim_value(self, value: float):
        w = int(value)
        self.setFixedWidth(w)
        show_text = w >= SIDEBAR_TEXT_THRESHOLD
        for i, btn in enumerate(self._buttons):
            label = self._NAV_ITEMS[i][2]
            btn.setText(label if show_text else "")

    def toggle(self):
        if self._animating:
            return
        self._animating = True
        self._expanded  = not self._expanded
        self._anim.setStartValue(float(self.width()))
        self._anim.setEndValue(float(SIDEBAR_EXPANDED if self._expanded else SIDEBAR_COLLAPSED))
        self._anim.start()

    def set_active(self, index: int):
        self._current_idx = index
        for i, btn in enumerate(self._buttons):
            btn.setChecked(i == index)

    def collapse_instant(self):
        self._anim.stop()
        self._animating = False
        self.setFixedWidth(0)
        for i, btn in enumerate(self._buttons):
            btn.setText("")

    def expand_to(self, width: int):
        self.setFixedWidth(width)
        show_text = width >= SIDEBAR_TEXT_THRESHOLD
        for i, btn in enumerate(self._buttons):
            label = self._NAV_ITEMS[i][2]
            btn.setText(label if show_text else "")