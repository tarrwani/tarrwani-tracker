from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGraphicsDropShadowEffect
from PySide6.QtCore import Qt, QTimer, Signal, QMimeData, QPoint, QRect,  QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QDrag, QPixmap, QPainter, QColor
from ui.widgets.circle_timer import CircleTimer


class TimerCard(QWidget):
    favoriteChanged = Signal(object)  # emits self

    def __init__(self, label, seconds, parent=None):
        super().__init__(parent)
        self.setFixedHeight(320)
        self.setMinimumWidth(220)
        self._offset_y = 0

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(12)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self._shadow)

        self._anim = QPropertyAnimation(self, b"offsetY")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._total = seconds
        self._remaining = seconds
        self._is_favorite = False
        self._drag_start_pos = QPoint()

        self._timer = QTimer()
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Верхняя панель: название + звёздочка
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(8, 0, 8, 0)

        self.title = QLabel(label)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet("color: #aaaaaa; font-size: 14px;")

        self.fav_btn = QPushButton("☆")
        self.fav_btn.setFixedSize(28, 28)
        self.fav_btn.setToolTip("Добавить в избранное")
        self.fav_btn.clicked.connect(self._toggle_favorite)
        self.fav_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #555566;
                font-size: 18px;
                padding: 0;
            }
            QPushButton:hover { color: #f0c040; }
        """)

        top_layout.addWidget(self.title, stretch=1)
        top_layout.addWidget(self.fav_btn)

        # Круг
        self.circle = CircleTimer()
        self.circle.set_progress(self._remaining, self._total)

        # Кнопки
        btn_layout = QHBoxLayout()

        self.start_btn = QPushButton("▶")
        self.start_btn.setFixedSize(36, 36)
        self.start_btn.clicked.connect(self._toggle)
        self.start_btn.setStyleSheet("""
            QPushButton { border-radius: 18px; background-color: #2d2d3a; color: #ffffff; font-size: 12px; }
            QPushButton:hover { background-color: #3d3d4a; }
        """)

        self.reset_btn = QPushButton("↺")
        self.reset_btn.setFixedSize(36, 36)
        self.reset_btn.clicked.connect(self._reset)
        self.reset_btn.setStyleSheet("""
            QPushButton { border-radius: 18px; background-color: #2d2d3a; color: #ffffff; font-size: 16px; }
            QPushButton:hover { background-color: #3d3d4a; }
        """)

        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.reset_btn)

        layout.addLayout(top_layout)
        layout.addWidget(self.circle, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(btn_layout)

        self._apply_card_style()

    # ── Избранное ──────────────────────────────────────────────
    def _toggle_favorite(self):
        self._is_favorite = not self._is_favorite
        self.fav_btn.setText("★" if self._is_favorite else "☆")
        self.fav_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background: transparent;
                color: {"#f0c040" if self._is_favorite else "#555566"};
                font-size: 18px;
                padding: 0;
            }}
            QPushButton:hover {{ color: #f0c040; }}
        """)
        self._apply_card_style()
        self.favoriteChanged.emit(self)

    def is_favorite(self):
        return self._is_favorite

    def _apply_card_style(self):
        border = "1px solid #f0c04066" if self._is_favorite else "1px solid #2a2a38"
        self.setStyleSheet(f"""
            TimerCard {{
                background-color: #1e1e2e;
                border-radius: 16px;
                border: {border};
            }}
        """)

    # Drag & Drop
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.position().toPoint()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        delta = (event.position().toPoint() - self._drag_start_pos).manhattanLength()
        if delta < 12:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setText("timer_card")
        drag.setMimeData(mime)

        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        self.render(pixmap, QPoint(), self.rect())   # render(QPaintDevice, targetOffset, sourceRegion)
        faded = QPixmap(pixmap.size())
        faded.fill(Qt.GlobalColor.transparent)
        p2 = QPainter(faded)
        p2.setOpacity(0.75)
        p2.drawPixmap(QPoint(), pixmap)
        p2.end()
        drag.setPixmap(faded)
        drag.setHotSpot(self._drag_start_pos)

        drag.exec(Qt.DropAction.MoveAction)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
    
    @Property(int)
    def offsetY(self):
        return self._offset_y

    @offsetY.setter
    def offsetY(self, value):
        self._offset_y = value
        self.setContentsMargins(0, max(0, -value), 0, max(0, value))

    def enterEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._offset_y)
        self._anim.setEndValue(-6)
        self._shadow.setBlurRadius(28)
        self._shadow.setOffset(0, 10)
        self._shadow.setColor(QColor(0, 0, 0, 140))
        self._anim.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._anim.stop()
        self._anim.setStartValue(self._offset_y)
        self._anim.setEndValue(0)
        self._shadow.setBlurRadius(12)
        self._shadow.setOffset(0, 4)
        self._shadow.setColor(QColor(0, 0, 0, 80))
        self._anim.start()
        super().leaveEvent(event)

    # Timer
    def _toggle(self):
        if self._timer.isActive():
            self._timer.stop()
            self.start_btn.setText("▶")
        else:
            self._tick()
            self._timer.start()
            self.start_btn.setText("⏸")

    def _reset(self):
        self._timer.stop()
        self.start_btn.setText("▶")
        self._remaining = self._total
        self.circle.set_progress(self._remaining, self._total)

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._remaining = 0
            self._timer.stop()
            self.start_btn.setText("▶")
        self.circle.set_progress(self._remaining, self._total)