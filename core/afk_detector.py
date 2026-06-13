"""Cross-platform idle-time detection used for AFK tracking.

Prefers a real system-wide idle API:
  - Windows: GetLastInputInfo
  - macOS:   ioreg HIDIdleTime
  - Linux:   xprintidle (if installed)

If none of those are available (e.g. Linux without xprintidle), falls back
to tracking input events inside this application only — AFK detection then
only works while the app window has focus.
"""

from __future__ import annotations

import subprocess
import sys
import time

from PySide6.QtCore import QEvent, QObject
from PySide6.QtWidgets import QApplication


def _system_idle_seconds() -> float | None:
    """Return seconds since the last system-wide input event, or None if
    no supported API is available on this platform."""
    try:
        if sys.platform == "win32":
            import ctypes

            class LASTINPUTINFO(ctypes.Structure):
                _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

            lii = LASTINPUTINFO()
            lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
            if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
                millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
                return millis / 1000.0
            return None

        elif sys.platform == "darwin":
            out = subprocess.check_output(
                ["ioreg", "-c", "IOHIDSystem"], text=True, stderr=subprocess.DEVNULL
            )
            for line in out.splitlines():
                if "HIDIdleTime" in line:
                    nanoseconds = int(line.rsplit("=", 1)[-1].strip())
                    return nanoseconds / 1_000_000_000.0
            return None

        else:  # Linux / other X11 systems
            out = subprocess.check_output(
                ["xprintidle"], text=True, stderr=subprocess.DEVNULL
            )
            return int(out.strip()) / 1000.0

    except Exception:
        return None


class _ActivityFilter(QObject):
    """Records the timestamp of the last mouse/keyboard event seen by the
    application. Used as a fallback idle source."""

    _TRACKED_EVENTS = {
        QEvent.Type.MouseMove,
        QEvent.Type.MouseButtonPress,
        QEvent.Type.MouseButtonRelease,
        QEvent.Type.KeyPress,
        QEvent.Type.KeyRelease,
        QEvent.Type.Wheel,
    }

    def __init__(self) -> None:
        super().__init__()
        self.last_activity = time.monotonic()

    def eventFilter(self, obj, event) -> bool:  # noqa: N802 (Qt override)
        if event.type() in self._TRACKED_EVENTS:
            self.last_activity = time.monotonic()
        return False


class AFKMonitor:
    """Reports how long (in seconds) the user has been idle.

    Usage:
        monitor = AFKMonitor()
        monitor.start()
        ...
        idle = monitor.idle_seconds()
        ...
        monitor.stop()
    """

    def __init__(self) -> None:
        self._filter = _ActivityFilter()
        self._active = False
        # Detect once whether a real system-wide idle source exists.
        self._use_system = _system_idle_seconds() is not None

    def start(self) -> None:
        if self._active:
            return
        self._active = True
        self._filter.last_activity = time.monotonic()
        if not self._use_system:
            app = QApplication.instance()
            if app is not None:
                app.installEventFilter(self._filter)

    def stop(self) -> None:
        if not self._active:
            return
        self._active = False
        if not self._use_system:
            app = QApplication.instance()
            if app is not None:
                app.removeEventFilter(self._filter)

    def idle_seconds(self) -> float:
        if self._use_system:
            secs = _system_idle_seconds()
            if secs is not None:
                return secs
        return time.monotonic() - self._filter.last_activity