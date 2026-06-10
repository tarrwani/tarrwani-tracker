from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF

class CircleTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self._value = 1.0  # прогресс от 1.0 до 0.0
        self._remaining = 0

    def set_progress(self, remaining, total):
        self._remaining = remaining
        self._value = remaining / total if total > 0 else 0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        thickness = 8
        rect = QRectF(thickness, thickness, self.width() - thickness*2, self.height() - thickness*2)

        bg_pen = QPen(QColor("#2d2d3a"), thickness)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        if self._value > 0:
            active_pen = QPen(QColor("#1D9E75"), thickness)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            start_angle = 90 * 16
            span_angle = int(-(self._value) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))

        hours = self._remaining // 3600
        minutes = (self._remaining % 3600) // 60
        seconds = self._remaining % 60
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{hours:02d}:{minutes:02d}:{seconds:02d}")