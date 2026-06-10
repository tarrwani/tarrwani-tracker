from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QPushButton, QLabel
from PySide6.QtCore import Qt, QTimer
from ui.widgets.circle_timer import CircleTimer

class TimerView(QWidget):
    def __init__(self):
        super().__init__()

        self._value = 25 * 60
        self._remaining = self._value

        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Круг
        self.circle = CircleTimer()
        self.circle.set_progress(self._remaining, self._value)
        layout.addWidget(self.circle, alignment=Qt.AlignmentFlag.AlignCenter)

        # Поля ввода
        time_layout = QHBoxLayout()

        self.hours_input = QSpinBox()
        self.hours_input.setRange(0, 23)
        self.hours_input.valueChanged.connect(self._update_from_inputs)

        self.minutes_input = QSpinBox()
        self.minutes_input.setRange(0, 59)
        self.minutes_input.setValue(25)
        self.minutes_input.valueChanged.connect(self._update_from_inputs)

        self.seconds_input = QSpinBox()
        self.seconds_input.setRange(0, 59)
        self.seconds_input.valueChanged.connect(self._update_from_inputs)

        time_layout.addWidget(self.hours_input)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.minutes_input)
        time_layout.addWidget(QLabel(":"))
        time_layout.addWidget(self.seconds_input)

        # Кнопка
        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self._start)

        layout.addLayout(time_layout)
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def _update_from_inputs(self):
        self._remaining = (self.hours_input.value() * 3600 +
                           self.minutes_input.value() * 60 +
                           self.seconds_input.value())
        self._value = self._remaining
        self.circle.set_progress(self._remaining, self._value)

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._remaining = 0
            self._timer.stop()
        self.circle.set_progress(self._remaining, self._value)

    def _start(self):
        self._value = (self.hours_input.value() * 3600 +
                       self.minutes_input.value() * 60 +
                       self.seconds_input.value())
        self._remaining = self._value
        self._timer.start()