from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt

from ui.widgets.time_input import TimeInput
from config import (
    DIALOG_W, DIALOG_H, DIALOG_PADDING, DIALOG_SPACING,
    DIALOG_INPUT_RADIUS, DIALOG_INPUT_FONT,
    DEFAULT_TIMER_MINUTES,
    settings_manager,
)


class TimerDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Новый таймер")
        self.setFixedSize(DIALOG_W, DIALOG_H)

        layout = QVBoxLayout(self)
        layout.setSpacing(DIALOG_SPACING)
        layout.setContentsMargins(DIALOG_PADDING, DIALOG_PADDING,
                                  DIALOG_PADDING, DIALOG_PADDING)

        # Name
        self.name_label = QLabel("Название")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Обед")

        # Time
        self.time_label    = QLabel("Время")
        self.hours_input   = TimeInput("Hours",   0, 23)
        self.minutes_input = TimeInput("Minutes", 0, 59, default=DEFAULT_TIMER_MINUTES)
        self.seconds_input = TimeInput("Seconds", 0, 59)

        self.sep1 = QLabel(":")
        self.sep2 = QLabel(":")
        for sep in (self.sep1, self.sep2):
            sep.setAlignment(Qt.AlignmentFlag.AlignCenter)

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hours_input)
        time_layout.addWidget(self.sep1)
        time_layout.addWidget(self.minutes_input)
        time_layout.addWidget(self.sep2)
        time_layout.addWidget(self.seconds_input)

        # Buttons
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)

        self.ok_btn = QPushButton("Добавить")
        self.ok_btn.clicked.connect(self.accept)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.time_label)
        layout.addLayout(time_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)

        self.hours_input.valueChanged.connect(self._validate)
        self.minutes_input.valueChanged.connect(self._validate)
        self.seconds_input.valueChanged.connect(self._validate)

        self._apply_styles()
        self._validate()

    # Theme
    def _apply_styles(self) -> None:
        t = settings_manager.theme
        r = DIALOG_INPUT_RADIUS

        self.name_label.setStyleSheet(
            f"color: {t.text_secondary}; font-size: 12px;"
        )
        self.time_label.setStyleSheet(
            f"color: {t.text_secondary}; font-size: 12px;"
        )
        for sep in (self.sep1, self.sep2):
            sep.setStyleSheet(f"color: {t.text_secondary}; font-size: 20px;")

        self.name_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {t.bg_surface};
                border: none;
                border-radius: {r}px;
                padding: 8px;
                color: {t.text_primary};
                font-size: {DIALOG_INPUT_FONT}px;
            }}
        """)

        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t.bg_surface};
                border: none;
                border-radius: {r}px;
                padding: 8px 16px;
                color: {t.text_primary};
            }}
            QPushButton:hover {{ background-color: {t.bg_surface_hover}; }}
        """)

    def _validate(self) -> None:
        t = settings_manager.theme
        r = DIALOG_INPUT_RADIUS

        total = (self.hours_input.value() * 3600
                 + self.minutes_input.value() * 60
                 + self.seconds_input.value())
        valid = total > 0
        self.ok_btn.setEnabled(valid)

        bg    = t.accent          if valid else t.accent_disabled
        bg_h  = t.accent_hover    if valid else t.accent_disabled
        color = t.text_primary    if valid else t.text_disabled

        self.ok_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                border: none;
                border-radius: {r}px;
                padding: 8px 16px;
                color: {color};
            }}
            QPushButton:hover {{ background-color: {bg_h}; }}
        """)

    # Result
    def get_values(self) -> tuple[str, int]:
        seconds = (self.hours_input.value() * 3600
                   + self.minutes_input.value() * 60
                   + self.seconds_input.value())
        name = self.name_input.text() or "Таймер"
        return name, max(1, seconds)