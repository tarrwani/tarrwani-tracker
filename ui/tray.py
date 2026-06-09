import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QTimer
from config import ICON_PATH


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app: QApplication, on_open=None, on_quit=None):
        super().__init__()
        self.app = app
        self.on_open = on_open
        self.on_quit = on_quit

        self.setIcon(QIcon(str(ICON_PATH)))
        self.setToolTip("Tarrwani Tracker")
        self._build_menu()
        self.activated.connect(self._on_click)

    def _build_menu(self):
        menu = QMenu()

        self.action_open = QAction("Открыть")
        self.action_open.triggered.connect(lambda: self.on_open() if self.on_open else None)

        self.action_status = QAction("⏹ Не запущен")
        self.action_status.setEnabled(False)

        action_quit = QAction("Выход")
        action_quit.triggered.connect(lambda: self.on_quit() if self.on_quit else None)

        menu.addAction(self.action_open)
        menu.addSeparator()
        menu.addAction(self.action_status)
        menu.addSeparator()
        menu.addAction(action_quit)

        self.setContextMenu(menu)

    def _on_click(self, reason):
        """Двойной клик — открыть главное окно"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            if self.on_open:
                self.on_open()

    def set_status(self, text: str):
        """Обновить статус в меню трея"""
        self.action_status.setText(text)