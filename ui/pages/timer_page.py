from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget, QLabel
from PySide6.QtCore import Qt
# Импортируйте ваши готовые классы TopBar и SidebarWidget
# from ui.widgets.topbar import TopBar
# from ui.widgets.sidebar import SidebarWidget

# Временные заглушки для демонстрации страниц контента
class TimerPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        label = QLabel("⏳ Экран Таймера")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        self.setStyleSheet("background-color: #1e1e24; color: #ffffff; font-size: 18px;")