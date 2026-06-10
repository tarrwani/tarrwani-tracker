from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal

class TimeInput(QWidget):
    valueChanged = Signal()
    def __init__(self, label, min_val, max_val, default=0, parent=None):
        super().__init__(parent)

        self._value = default
        self._min = min_val
        self._max = max_val

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        self.title = QLabel(label)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #888888; font-size: 12px;")

        self.up_btn = QPushButton("▲")
        self.up_btn.setFixedSize(40, 24)
        self.up_btn.clicked.connect(self._increment)
        self.up_btn.setStyleSheet("""
            QPushButton { border: none; color: #888888; font-size: 10px; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); color: #ffffff; }
        """)

        # Число
        self.value_label = QLabel(f"{default:02d}")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("color: #ffffff; font-size: 32px; font-weight: bold;")

        # Кнопка вниз
        self.down_btn = QPushButton("▼")
        self.down_btn.setFixedSize(40, 24)
        self.down_btn.clicked.connect(self._decrement)
        self.down_btn.setStyleSheet("""
            QPushButton { border: none; color: #888888; font-size: 10px; border-radius: 4px; }
            QPushButton:hover { background-color: rgba(255, 255, 255, 30); color: #ffffff; }
        """)
        layout.addWidget(self.title)
        layout.addWidget(self.up_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)
        layout.addWidget(self.down_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _increment(self):
        if self._value < self._max:
            self._value += 1
            self.value_label.setText(f"{self._value:02d}")
            self.valueChanged.emit()

    def _decrement(self):
        if self._value > self._min:
            self._value -= 1
            self.value_label.setText(f"{self._value:02d}")
            self.valueChanged.emit()

    def value(self):
        return self._value
    
    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            self._increment()
        else:
            self._decrement()