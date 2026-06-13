from PySide6.QtWidgets import QAbstractButton
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, Property
from PySide6.QtGui import QPainter, QColor, QBrush, QPen


class ToggleSwitch(QAbstractButton):
    """Animated iOS-style toggle switch."""

    _TRACK_W  = 48
    _TRACK_H  = 26
    _THUMB_D  = 20
    _THUMB_PAD = 3

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(self._TRACK_W, self._TRACK_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._thumb_x: float = float(self._THUMB_PAD)

        self._anim = QPropertyAnimation(self, b"thumb_x", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.toggled.connect(self._on_toggled)

    # ── Qt property for animation ──────────────────────────────
    def _get_thumb_x(self) -> float:
        return self._thumb_x

    def _set_thumb_x(self, x: float) -> None:
        self._thumb_x = x
        self.update()

    thumb_x = Property(float, _get_thumb_x, _set_thumb_x)

    # ── Internal ───────────────────────────────────────────────
    def _on_toggled(self, checked: bool) -> None:
        target = float(self._TRACK_W - self._THUMB_D - self._THUMB_PAD) if checked else float(self._THUMB_PAD)
        self._anim.setStartValue(self._thumb_x)
        self._anim.setEndValue(target)
        self._anim.start()

    # ── Paint ──────────────────────────────────────────────────
    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(Qt.PenStyle.NoPen))

        # Track
        track_color = QColor("#1D9E75") if self.isChecked() else QColor("#3a3a4a")
        p.setBrush(QBrush(track_color))
        r = self._TRACK_H // 2
        p.drawRoundedRect(0, 0, self._TRACK_W, self._TRACK_H, r, r)

        # Thumb
        p.setBrush(QBrush(QColor("#ffffff")))
        tx = int(self._thumb_x)
        ty = (self._TRACK_H - self._THUMB_D) // 2
        p.drawEllipse(tx, ty, self._THUMB_D, self._THUMB_D)
        p.end()

    def sizeHint(self):
        from PySide6.QtCore import QSize
        return QSize(self._TRACK_W, self._TRACK_H)