import os
from pathlib import Path
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QIcon
from config import (
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_BG_NAV, APP_NAME, ICON_PATH, ASSETS_DIR
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
        
        layout.setContentsMargins(10, 5, 12, 5) 
        layout.setSpacing(0)

        self._menu_icon = QIcon(str(ASSETS_DIR / "menu.svg"))

        self.menu_btn = QPushButton()
        self.menu_btn.setIcon(self._menu_icon)
        self.menu_btn.setFixedSize(48, 32)
        self.menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.menu_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLOR_TEXT_PRIMARY};
                font-size: 16px;
                border-radius: 6px;
            }}
            QPushButton:hover {{ background: {COLOR_BG_NAV}; }}
        """)

        self.menu_btn.clicked.connect(self.sig_menu_clicked.emit)

        self._icon_lbl = QLabel()
        self._icon_lbl.setStyleSheet("background: transparent;")
        
        pixmap = QPixmap(str(ICON_PATH))
        if not pixmap.isNull():
            self._icon_lbl.setFixedSize(24, 24)
            self._icon_lbl.setPixmap(
                pixmap.scaled(18, 18,
                              Qt.AspectRatioMode.KeepAspectRatio,
                              Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self._icon_lbl.setFixedSize(0, 0)
            
        self._icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._title_lbl = QLabel(APP_NAME)
        self._title_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 13px; background: transparent; padding: 0;"
        )

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

        layout.addWidget(self.menu_btn) 
        layout.addSpacing(23)
        layout.addWidget(self._icon_lbl)
        layout.addSpacing(10)
        layout.addWidget(self._title_lbl)
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
            # ИЗМЕНЕНИЕ: Обновили координату начала зоны перетаскивания под новый margin (14 отступ + 36 кнопка + 25 спейсинг = 75)
            if event.position().x() > 75:
                self._drag_pos = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
                event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_pos'):
            self.window().move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()