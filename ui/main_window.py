from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PySide6.QtCore import Qt, QVariantAnimation, QEasingCurve
from ui.views.timer_view import TimerView
from ui.views.stat_view  import StatView
from config import (
    COLOR_BG_PRIMARY, COLOR_BG_NAV, COLOR_BG_NAV_HOVER,
    COLOR_BG_NAV_ACTIVE, COLOR_BG_NAV_PRESSED,
    COLOR_TEXT_SECONDARY, COLOR_TEXT_PRIMARY,
    SIDEBAR_EXPANDED, SIDEBAR_COLLAPSED,
    SIDEBAR_ANIM_MS, SIDEBAR_TEXT_THRESHOLD,
    CARD_MIN_WIDTH,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarrwani Tracker")
        self.resize(700, 550)
        self.setMinimumSize(CARD_MIN_WIDTH + 96, 320 + 80)
        self._sidebar_expanded = True
        self._animating = False

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Sidebar 
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(SIDEBAR_EXPANDED)
        self.sidebar.setStyleSheet(f"background-color: {COLOR_BG_PRIMARY};")

        self.toggle_btn = QPushButton("◀")
        self.toggle_btn.setFixedSize(44, 44)
        self.toggle_btn.setMinimumWidth(44)
        self.toggle_btn.setMaximumWidth(160)
        self.toggle_btn.setToolTip("Свернуть/развернуть панель")
        self.toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_btn.clicked.connect(self._toggle_sidebar)
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                padding: 0 12px;
                background: {COLOR_BG_NAV};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 10px;
                text-align: left;
                font-size: 16px;
            }}
            QPushButton:hover   {{ background: {COLOR_BG_NAV_HOVER};    color: {COLOR_TEXT_PRIMARY}; }}
            QPushButton:pressed {{ background: {COLOR_BG_NAV_PRESSED};  }}
        """)

        nav_btn_style = f"""
            QPushButton {{
                text-align: left;
                padding: 8px 10px;
                background: transparent;
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                font-size: 14px;
            }}
            QPushButton:hover   {{ background: {COLOR_BG_NAV};        color: {COLOR_TEXT_PRIMARY}; }}
            QPushButton:checked {{ background: {COLOR_BG_NAV_ACTIVE}; color: {COLOR_TEXT_PRIMARY}; }}
        """

        self.timer_btn = QPushButton("🕒  Таймер")
        self.timer_btn.setCheckable(True)
        self.timer_btn.setChecked(True)
        self.timer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.timer_btn.setStyleSheet(nav_btn_style)
        self.timer_btn.clicked.connect(lambda: self.switch_view(0, self.timer_btn))

        self.stat_btn = QPushButton("📊  Статистика")
        self.stat_btn.setCheckable(True)
        self.stat_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stat_btn.setStyleSheet(nav_btn_style)
        self.stat_btn.clicked.connect(lambda: self.switch_view(1, self.stat_btn))

        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(10, 10, 10, 10)
        sidebar_layout.setSpacing(4)
        sidebar_layout.addWidget(self.toggle_btn, alignment=Qt.AlignmentFlag.AlignLeft)
        sidebar_layout.addSpacing(8)
        sidebar_layout.addWidget(self.timer_btn)
        sidebar_layout.addWidget(self.stat_btn)
        sidebar_layout.addStretch()
        self.sidebar.setLayout(sidebar_layout)

        # Content
        self.content = QStackedWidget()
        self.timer_view = TimerView()
        self.stat_view  = StatView()
        self.content.addWidget(self.timer_view)
        self.content.addWidget(self.stat_view)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content)

        # Animation
        self._anim = QVariantAnimation()
        self._anim.setDuration(SIDEBAR_ANIM_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.valueChanged.connect(self._on_anim_value)
        self._anim.finished.connect(self._on_anim_finished)

    def _on_anim_value(self, value):
        w = int(value)
        self.sidebar.setFixedWidth(w)
        if w >= SIDEBAR_TEXT_THRESHOLD:
            self.timer_btn.setText("🕒  Таймер")
            self.stat_btn.setText("📊  Статистика")
            self.toggle_btn.setText("◀  Свернуть")
        else:
            self.timer_btn.setText("🕒")
            self.stat_btn.setText("📊")
            self.toggle_btn.setText("▶")

    def _toggle_sidebar(self):
        if self._animating:
            return
        self._animating = True
        self._sidebar_expanded = not self._sidebar_expanded
        start = self.sidebar.width()
        end   = SIDEBAR_EXPANDED if self._sidebar_expanded else SIDEBAR_COLLAPSED
        self._anim.setStartValue(float(start))
        self._anim.setEndValue(float(end))
        self._anim.start()

    def _on_anim_finished(self):
        self._animating = False

    def switch_view(self, index: int, active_btn: QPushButton):
        self.timer_btn.setChecked(False)
        self.stat_btn.setChecked(False)
        active_btn.setChecked(True)
        self.content.setCurrentIndex(index)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.sidebar.setVisible(self.width() >= 400)