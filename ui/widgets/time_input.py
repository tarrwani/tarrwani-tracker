from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt, Signal

from config import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_MUTED,
    TIME_INPUT_BTN_W, TIME_INPUT_BTN_H,
    TIME_INPUT_FONT, TIME_INPUT_LABEL_FONT, TIME_INPUT_ARROW_FONT,
    settings_manager,
)


class TimeInput(QWidget):
    valueChanged = Signal()

    def __init__(self, label: str, min_val: int, max_val: int,
                 default: int = 0, parent=None) -> None:
        super().__init__(parent)
        self._value = default
        self._min   = min_val
        self._max   = max_val

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        self.title = QLabel(label)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(TIME_INPUT_BTN_W, TIME_INPUT_BTN_H)
        self.up_btn.clicked.connect(self._increment)

        self.value_label = QLabel(f"{default:02d}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.down_btn = QPushButton("▼")
        self.down_btn.setFixedSize(TIME_INPUT_BTN_W, TIME_INPUT_BTN_H)
        self.down_btn.clicked.connect(self._decrement)

        layout.addWidget(self.title)
        layout.addWidget(self.up_btn,    alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        layout.addWidget(self.down_btn,  alignment=Qt.AlignmentFlag.AlignCenter)

        self._apply_styles()

    # Theme

    def _apply_styles(self) -> None:
        t = settings_manager.theme

        self.title.setStyleSheet(
            f"color: {t.text_muted}; font-size: {TIME_INPUT_LABEL_FONT}px;"
        )

        self.value_label.setStyleSheet(
            f"color: {t.text_primary};"
            f"font-size: {TIME_INPUT_FONT}px;"
            f"font-weight: bold;"
        )

        arrow_style = f"""
            QPushButton {{
                border: none;
                color: {t.text_muted};
                font-size: {TIME_INPUT_ARROW_FONT}px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: {t.bg_overlay_hover};
                color: {t.text_primary};
            }}
        """
        self.up_btn.setStyleSheet(arrow_style)
        self.down_btn.setStyleSheet(arrow_style)

    def refresh_theme(self) -> None:
        self._apply_styles()

    # Value control

    def _increment(self) -> None:
        if self._value < self._max:
            self._value += 1
            self.value_label.setText(f"{self._value:02d}")
            self.valueChanged.emit()

    def _decrement(self) -> None:
        if self._value > self._min:
            self._value -= 1
            self.value_label.setText(f"{self._value:02d}")
            self.valueChanged.emit()

    def value(self) -> int:
        return self._value

    def wheelEvent(self, event) -> None:
        if event.angleDelta().y() > 0:
            self._increment()
        else:
            self._decrement()