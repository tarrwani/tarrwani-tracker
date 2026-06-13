from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Signal


class MarathonEngine(QObject):
    sig_tick = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._elapsed = 0
        self._running = False
        self._paused = False
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def is_paused(self) -> bool:
        return self._paused

    def start(self):
        self._elapsed = 0
        self._running = True
        self._paused = False
        self._timer.start()
        self._emit()

    def toggle_pause(self):
        if not self._running:
            return
        self._paused = not self._paused
        if self._paused:
            self._timer.stop()
        else:
            self._timer.start()
        self._emit()

    def stop(self):
        self._running = False
        self._paused = False
        self._timer.stop()
        elapsed = self._elapsed
        self._elapsed = 0
        self._emit()
        return elapsed

    def _tick(self):
        if self._running and not self._paused:
            self._elapsed += 1
        self._emit()

    def state(self) -> dict:
        return {
            "elapsed": self._elapsed,
            "running": self._running,
            "paused": self._paused,
        }

    def _emit(self):
        self.sig_tick.emit(self.state())
