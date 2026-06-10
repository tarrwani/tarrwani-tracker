from PySide6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QScrollArea, QPushButton
from PySide6.QtCore import Qt
from ui.widgets.timer_card import TimerCard
from ui.widgets.timer_dialog import TimerDialog

class TimerView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        self.grid = QGridLayout(container)
        self.grid.setSpacing(16)

        presets = [
            ("1 минута", 60),
            ("3 минуты", 180),
            ("5 минут", 300),
            ("10 минут", 600),
        ]

        for i, (label, seconds) in enumerate(presets):
            card = TimerCard(label, seconds)
            self.grid.addWidget(card, i // 2, i % 2)

        self._card_count = len(presets)

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(36, 36)
        self.add_btn.clicked.connect(self._add_card)
        self.add_btn.setStyleSheet("""
            QPushButton { border-radius: 18px; background-color: #1D9E75; color: #ffffff; font-size: 20px; }
            QPushButton:hover { background-color: #17835f; }
        """)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        main_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _add_card(self):
        dialog = TimerDialog(self)
        if dialog.exec():  # вернёт True если нажали "Добавить"
            name, seconds = dialog.get_values()
            card = TimerCard(name, seconds)
            row = self._card_count // 2
            col = self._card_count % 2
            self.grid.addWidget(card, row, col)
            self._card_count += 1