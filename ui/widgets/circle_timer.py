from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve

class CircleTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self._progress = 1.0
        self._remaining = 0

        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(1000) # ms
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)

    def set_progress(self, remaining, total):
        self._remaining = remaining
        new_value = remaining / total if total > 0 else 0
        self.set_progress_animated(new_value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        thickness = 8
        rect = QRectF(thickness, thickness, self.width() - thickness*2, self.height() - thickness*2)

        bg_pen = QPen(QColor("#2d2d3a"), thickness)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect)

        if self._progress > 0:
            active_pen = QPen(QColor("#1D9E75"), thickness)
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(active_pen)
            start_angle = 90 * 16
            span_angle = int(-(self._progress) * 360 * 16)
            painter.drawArc(rect, start_angle, span_angle)

        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))

        hours = self._remaining // 3600
        minutes = (self._remaining % 3600) // 60
        seconds = self._remaining % 60
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def get_progress(self):
        return self._progress

    def set_progress_animated(self, value):
        self._animation.stop()
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(value)
        self._animation.start()

    progress = Property(float, get_progress, lambda self, v: setattr(self, '_progress', v) or self.update())