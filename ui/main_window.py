from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QStackedWidget
from PySide6.QtGui import QPainter, QColor, QBrush, QPen
from PySide6.QtCore import Qt, QPoint, QEvent, Signal

from ui.widgets.sidebar import SidebarWidget
from ui.widgets.topbar import TopBar
from ui.pages.focus_page import FocusPage
from ui.pages.stats_page import StatsPage
from ui.pages.marathon_page import MarathonPage
from ui.widgets.sidegrip import SideGrip
from config import APP_BORDER_RADIUS, COLOR_BG_PRIMARY, SIDEBAR_COLLAPSED


class MainWindow(QWidget):
    sig_window_minimized = Signal(bool)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(600, 400)
        self.resize(800, 600)
        self._setup_ui()

    def _setup_ui(self):
        # root = QHBoxLayout(self)
        # root.setContentsMargins(0, 0, 0, 0)
        # root.setSpacing(0)

        # self.sidebar = SidebarWidget()
        # self.sidebar.view_changed.connect(self._on_view_changed)
        # root.addWidget(self.sidebar)

        # self.content = QWidget()
        # self.content.setContentsMargins(0, 36, 0, 0)

        # content_layout = QVBoxLayout(self.content)
        # content_layout.setContentsMargins(0, 0, 0, 0)
        # content_layout.setSpacing(0)

        # self.pages = QStackedWidget()
        # content_layout.addWidget(self.pages)

        # self.focus_page = FocusPage()   # 0
        # self.stats_page = StatsPage()   # 1

        # self.pages.addWidget(self.focus_page)
        # self.pages.addWidget(self.stats_page)

        # root.addWidget(self.content, stretch=1)

        # self.topbar = TopBar(self)
        # self.topbar.sig_close.connect(self.close)
        # self.topbar.sig_minimize.connect(self.showMinimized)
        # self.topbar.sig_fullscreen.connect(self._toggle_fullscreen)
        # self.topbar.sig_menu_clicked.connect(self.sidebar.toggle)

        # self.sidebar.raise_()
        # self.topbar.raise_()

        # self._setup_resizers()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 2. Добавляем ТОПБАР на самый верх. Он займет ровно столько, 
        # сколько ему нужно по высоте (например, 42px)
        self.topbar = TopBar(self)
        main_layout.addWidget(self.topbar)

        # 3. Создаем ГОРИЗОНТАЛЬНЫЙ контейнер для нижней части (Сайдбар + Контент)
        workspace_layout = QHBoxLayout()
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)
        main_layout.addLayout(workspace_layout)

        # 4. Добавляем Сайдбар в рабочий контейнер
        self.sidebar = SidebarWidget()
        self.sidebar.view_changed.connect(self._on_view_changed)
        workspace_layout.addWidget(self.sidebar)

        # 5. Создаем Контентную зону (Центральная часть)
        self.pages = QStackedWidget()
        self.focus_page = FocusPage()
        self.stats_page = StatsPage()
        self.marathon_page = MarathonPage()
        self.pages.addWidget(self.focus_page)
        self.pages.addWidget(self.stats_page)
        self.pages.addWidget(self.marathon_page)
        
        # Добавляем страницы в рабочую область и заставляем их растягиваться (stretch=1)
        workspace_layout.addWidget(self.pages, stretch=1)

        # Связываем сигналы топбара
        self.topbar.sig_close.connect(self.close)
        self.topbar.sig_minimize.connect(self.showMinimized)
        self.topbar.sig_fullscreen.connect(self._toggle_fullscreen)
        self.topbar.sig_menu_clicked.connect(self.sidebar.toggle)

        # Инициализируем грипы ресайза
        self._setup_resizers()

        self.sig_window_minimized.connect(self.focus_page._on_window_minimized)
        self.sig_window_minimized.connect(self.marathon_page._on_window_minimized)

    def _setup_resizers(self):
        self._grips = {}
        grip_configs = [
            ('T',  Qt.CursorShape.SizeVerCursor),
            ('B',  Qt.CursorShape.SizeVerCursor),
            ('L',  Qt.CursorShape.SizeHorCursor),
            ('R',  Qt.CursorShape.SizeHorCursor),
            ('TL', Qt.CursorShape.SizeFDiagCursor),
            ('TR', Qt.CursorShape.SizeBDiagCursor),
            ('BL', Qt.CursorShape.SizeBDiagCursor),
            ('BR', Qt.CursorShape.SizeFDiagCursor),
        ]
        for pos, cursor in grip_configs:
            grip = SideGrip(self, pos, cursor)
            self._grips[pos] = grip
            grip.raise_()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        #if hasattr(self, 'topbar'):
            #self.topbar.setGeometry(0, 0, self.width(), 42)
        #if hasattr(self, 'sidebar'):
            #self.sidebar.setGeometry(0, 0, self.sidebar.width(), self.height())
        if hasattr(self, '_grips'):
            is_fs = self.isFullScreen()
            t = 6
            w, h = self.width(), self.height()

            for grip in self._grips.values():
                grip.setVisible(not is_fs)

            if not is_fs:
                self._grips['T'].setGeometry(t, 0, w - 2*t, t)
                self._grips['B'].setGeometry(t, h - t, w - 2*t, t)
                self._grips['L'].setGeometry(0, t, t, h - 2*t)
                self._grips['R'].setGeometry(w - t, t, t, h - 2*t)
                self._grips['TL'].setGeometry(0, 0, t, t)
                self._grips['TR'].setGeometry(w - t, 0, t, t)
                self._grips['BL'].setGeometry(0, h - t, t, t)
                self._grips['BR'].setGeometry(w - t, h - t, t, t)

    def _start_resize(self, position: str, global_press_pos: QPoint):
        self._resize_pos = position
        self._resize_start_geom = self.geometry()
        self._resize_start_global = global_press_pos

    def _drag_resize(self, global_current_pos: QPoint):
        if self.isFullScreen() or not hasattr(self, '_resize_pos'):
            return

        geom = self._resize_start_geom
        x, y, w, h = geom.x(), geom.y(), geom.width(), geom.height()
        min_w, min_h = self.minimumSize().width(), self.minimumSize().height()

        delta = global_current_pos - self._resize_start_global
        dx, dy = delta.x(), delta.y()

        position = self._resize_pos

        if 'L' in position:
            max_dx = w - min_w
            actual_dx = min(dx, max_dx)
            x += actual_dx
            w -= actual_dx
        elif 'R' in position:
            w = max(min_w, w + dx)

        if 'T' in position:
            max_dy = h - min_h
            actual_dy = min(dy, max_dy)
            y += actual_dy
            h -= actual_dy
        elif 'B' in position:
            h = max(min_h, h + dy)

        self.setGeometry(x, y, w, h)

    def _on_view_changed(self, index: int):
        self.pages.setCurrentIndex(index)

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            minimized = self.windowState() & Qt.WindowState.WindowMinimized
            self.sig_window_minimized.emit(bool(minimized))
        super().changeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QBrush(QColor(COLOR_BG_PRIMARY)))
        painter.setPen(QPen(Qt.PenStyle.NoPen))
        painter.drawRoundedRect(
            self.rect().adjusted(0, 0, -1, -1),
            APP_BORDER_RADIUS, APP_BORDER_RADIUS
        )