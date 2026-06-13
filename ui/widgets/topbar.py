from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QIcon
from config import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_BG_NAV, ASSETS_DIR
)

class TopBar(QWidget):
    sig_close      = Signal()
    sig_minimize   = Signal()
    sig_fullscreen = Signal()
    sig_menu_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(42)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._is_fullscreen = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 12, 5)
        layout.setSpacing(0)

        btn_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLOR_TEXT_SECONDARY};
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: {COLOR_BG_NAV}; color: {COLOR_TEXT_PRIMARY}; }}
        """
        close_style = f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLOR_TEXT_SECONDARY};
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: #c0392b; color: #ffffff; }}
        """

        self._minimize_btn   = self._make_icon_btn("minimize.svg", btn_style,   self.sig_minimize)
        self._fullscreen_btn = self._make_icon_btn("fullscreen.svg", btn_style,   self._on_fullscreen)
        self._close_btn      = self._make_icon_btn("close.svg", close_style, self.sig_close)

        layout.addStretch()
        layout.addWidget(self._minimize_btn)
        layout.addSpacing(3)
        layout.addWidget(self._fullscreen_btn)
        layout.addSpacing(3)
        layout.addWidget(self._close_btn)

    def _make_icon_btn(self, icon_name: str, style: str, slot) -> QPushButton:
        btn = QPushButton()
        btn.setIcon(QIcon(str(ASSETS_DIR / icon_name)))
        btn.setIconSize(QSize(16, 16))
        btn.setFixedSize(32, 28)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(style)
        btn.clicked.connect(slot)
        return btn

    def _on_fullscreen(self):
        self._is_fullscreen = not self._is_fullscreen
        if self._is_fullscreen:
            self._fullscreen_btn.setIcon(QIcon(str(ASSETS_DIR / "fullscreen_exit.svg")))
        else:
            self._fullscreen_btn.setIcon(QIcon(str(ASSETS_DIR / "fullscreen.svg")))
            
        self.sig_fullscreen.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()