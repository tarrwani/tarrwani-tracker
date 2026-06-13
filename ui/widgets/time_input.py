from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

from config import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_BG_SURFACE, COLOR_BG_SURFACE_HOVER, COLOR_ACCENT,
    COLOR_BG_OVERLAY_HOVER,
    TIME_INPUT_BTN_W, TIME_INPUT_BTN_H,
    TIME_INPUT_FONT, TIME_INPUT_LABEL_FONT, TIME_INPUT_ARROW_FONT,
)


class TimeInputWidget(QWidget):
    """Vertical spinbox for entering a minute value (1–999)."""

    value_changed = Signal(int)

    def __init__(
        self,
        label: str = "",
        min_val: int = 1,
        max_val: int = 999,
        value: int = 25,
        parent=None,
    ):
        super().__init__(parent)
        self._min   = min_val
        self._max   = max_val
        self._value = max(min_val, min(max_val, value))
        self._label = label
        self._setup_ui()

    # ── Build ──────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        if self._label:
            lbl = QLabel(self._label)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setStyleSheet(
                f"color: {COLOR_TEXT_MUTED}; font-size: {TIME_INPUT_LABEL_FONT}px;"
                " background: transparent;"
            )
            layout.addWidget(lbl)

        self._up_btn = self._arrow_btn("▲")
        self._up_btn.clicked.connect(self._increment)
        layout.addWidget(self._up_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        self._val_lbl = QLabel(str(self._value))
        self._val_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._val_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: {TIME_INPUT_FONT}px;"
            f" font-weight: bold; background: transparent; min-width: 72px;"
        )
        layout.addWidget(self._val_lbl)

        self._down_btn = self._arrow_btn("▼")
        self._down_btn.clicked.connect(self._decrement)
        layout.addWidget(self._down_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

    def _arrow_btn(self, text: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedSize(TIME_INPUT_BTN_W, TIME_INPUT_BTN_H)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_BG_OVERLAY_HOVER};
                border: none;
                border-radius: 6px;
                color: {COLOR_TEXT_SECONDARY};
                font-size: {TIME_INPUT_ARROW_FONT}px;
            }}
            QPushButton:hover {{
                background: {COLOR_BG_SURFACE_HOVER};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QPushButton:pressed {{
                background: {COLOR_ACCENT};
                color: #ffffff;
            }}
        """)
        return btn

    # ── Logic ──────────────────────────────────────────────────
    def _increment(self) -> None:
        self.set_value(self._value + 1)

    def _decrement(self) -> None:
        self.set_value(self._value - 1)

    def set_value(self, v: int) -> None:
        self._value = max(self._min, min(self._max, v))
        self._val_lbl.setText(str(self._value))
        self.value_changed.emit(self._value)

    def value(self) -> int:
        return self._value
    
    def wheelEvent(self, event) -> None:
        if event.angleDelta().y() > 0:
            self._increment()
        else:
            self._decrement()