from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

class StatView(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)

        self.some_label = QLabel()
        self.some_label.setText("It's Stats page")

        self.some_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.some_label, alignment=Qt.AlignmentFlag.AlignCenter)
        