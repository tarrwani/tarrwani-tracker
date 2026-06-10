from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QLabel
from PySide6.QtCore import Qt
from ui.widgets.time_input import TimeInput

class TimerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Новый таймер")
        self.setFixedSize(300, 400)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Поле названия
        name_label = QLabel("Название")
        name_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Обед")
        self.name_input.setStyleSheet("""
            QLineEdit {
                background-color: #2d2d3a;
                border: none;
                border-radius: 8px;
                padding: 8px;
                color: #ffffff;
                font-size: 14px;
            }
        """)

        # Поля времени
        time_label = QLabel("Время")
        time_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")

        time_layout = QHBoxLayout()
        self.hours_input = TimeInput("Hours", 0, 23)
        self.minutes_input = TimeInput("Minutes", 0, 59, default=5)
        self.seconds_input = TimeInput("Seconds", 0, 59)

        time_layout.addWidget(self.hours_input)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minutes_input)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.seconds_input)

        # Кнопки
        btn_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton { background-color: #2d2d3a; border: none; border-radius: 8px; padding: 8px 16px; color: #ffffff; }
            QPushButton:hover { background-color: #3d3d4a; }
        """)

        self.ok_btn = QPushButton("Добавить")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setStyleSheet("""
            QPushButton { background-color: #1D9E75; border: none; border-radius: 8px; padding: 8px 16px; color: #ffffff; }
            QPushButton:hover { background-color: #17835f; }
        """)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(self.ok_btn)

        layout.addWidget(name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(time_label)
        layout.addLayout(time_layout)
        layout.addStretch()
        layout.addLayout(btn_layout)

        self.hours_input.valueChanged.connect(self._validate)
        self.minutes_input.valueChanged.connect(self._validate)
        self.seconds_input.valueChanged.connect(self._validate)
        self._validate()

    def get_values(self):
        seconds = (self.hours_input.value() * 3600 +
                   self.minutes_input.value() * 60 +
                   self.seconds_input.value())
        name = self.name_input.text() or f"Таймер"
        return name, max(1, seconds)
    
    def _validate(self):
        total = (self.hours_input.value() * 3600 +
                 self.minutes_input.value() * 60 +
                 self.seconds_input.value())
        valid = total > 0
        self.ok_btn.setEnabled(valid)
        self.ok_btn.setStyleSheet(f"""
            QPushButton {{ background-color: {"#1D9E75" if valid else "#1a3d30"}; border: none; border-radius: 8px; padding: 8px 16px; color: {"#ffffff" if valid else "#555555"}; }}
            QPushButton:hover {{ background-color: {"#17835f" if valid else "#1a3d30"}; }}
        """)