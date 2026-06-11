from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF, Property, QPropertyAnimation, QEasingCurve

from config import (
    CIRCLE_TIMER_SIZE, CIRCLE_TIMER_THICKNESS,
    CIRCLE_TIMER_ANIM_MS, CIRCLE_TIMER_FONT_SIZE, CIRCLE_FONT_FAMILY,
    settings_manager,
)


class CircleTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(CIRCLE_TIMER_SIZE, CIRCLE_TIMER_SIZE)
        self._progress  = 1.0
        self._remaining = 0

        self._animation = QPropertyAnimation(self, b"progress")
        self._animation.setDuration(CIRCLE_TIMER_ANIM_MS)
        self._animation.setEasingCurve(QEasingCurve.Type.Linear)

    def set_progress(self, remaining: int, total: int) -> None:
        self._remaining = remaining
        new_value = remaining / total if total > 0 else 0.0
        self._set_progress_animated(new_value)

    def paintEvent(self, event) -> None:
        t = settings_manager.theme

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        th   = CIRCLE_TIMER_THICKNESS
        rect = QRectF(th, th, self.width() - th * 2, self.height() - th * 2)

        # Track ring
        painter.setPen(QPen(QColor(t.bg_surface), th))
        painter.drawEllipse(rect)

        # Progress arc
        if self._progress > 0:
            arc_pen = QPen(QColor(t.accent), th)
            arc_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(arc_pen)
            painter.drawArc(rect, 90 * 16, int(-self._progress * 360 * 16))

        # Time label
        h  = self._remaining // 3600
        m  = (self._remaining % 3600) // 60
        s  = self._remaining % 60
        painter.setPen(QColor(t.text_primary))
        painter.setFont(QFont(CIRCLE_FONT_FAMILY, CIRCLE_TIMER_FONT_SIZE, QFont.Weight.Bold))
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{h:02d}:{m:02d}:{s:02d}")

    # ── Animated property ─────────────────────────────────────

    def _get_progress(self) -> float:
        return self._progress

    def _set_progress(self, value: float) -> None:
        self._progress = value
        self.update()

    progress = Property(float, _get_progress, _set_progress)

    def _set_progress_animated(self, value: float) -> None:
        self._animation.stop()
        self._animation.setStartValue(self._progress)
        self._animation.setEndValue(value)
        self._animation.start()