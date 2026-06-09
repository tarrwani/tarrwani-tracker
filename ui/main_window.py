from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QTabWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from config import ICON_PATH


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarrwani Tracker")
        self.setMinimumSize(600, 500)
        self.setWindowIcon(QIcon(str(ICON_PATH)))

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # вкладки — пока пустые
        self.tabs.addTab(QWidget(), "▶  Трекер")
        self.tabs.addTab(QWidget(), "📁  Проекты")
        self.tabs.addTab(QWidget(), "📊  Статистика")
        self.tabs.addTab(QWidget(), "⚙  Настройки")

    def closeEvent(self, event):
        """Закрытие окна — скрываем в трей, не выходим"""
        event.ignore()
        self.hide()