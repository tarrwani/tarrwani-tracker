from __future__ import annotations

import sys

import psutil
from PySide6.QtCore import QObject, QTimer, Signal


if sys.platform == "win32":
    import ctypes
    import ctypes.wintypes

    def _active_window_process_name() -> str | None:
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not hwnd:
                return None
            pid = ctypes.wintypes.DWORD()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            handle = ctypes.windll.kernel32.OpenProcess(
                0x0400 | 0x0010, False, pid.value
            )
            if not handle:
                return None
            try:
                exe = ctypes.create_unicode_buffer(260)
                if ctypes.windll.psapi.GetModuleBaseNameW(
                    handle, None, exe, ctypes.sizeof(exe)
                ):
                    return exe.value
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            return None
        return None
else:
    def _active_window_process_name() -> str | None:
        return None


class ProcessTracker(QObject):
    sig_tick = Signal(dict)

    def __init__(self, process_names: list[str], parent=None):
        super().__init__(parent)
        self._names = list(process_names)
        self._log: dict[str, int] = {n: 0 for n in self._names}
        self._paused = False
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    def start(self):
        self._paused = False
        self._timer.start()

    def stop(self) -> dict[str, int]:
        self._timer.stop()
        return dict(self._log)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def reset(self, names: list[str] | None = None):
        if names is not None:
            self._names = list(names)
        self._log = {n: 0 for n in self._names}

    def _tick(self):
        if not self._paused:
            active_name = _active_window_process_name()
            if active_name:
                active_lower = active_name.lower()
                for original in self._names:
                    if original.lower() == active_lower:
                        self._log[original] += 1
                        break
        self.sig_tick.emit(dict(self._log))

    @staticmethod
    def get_unique_process_names() -> list[str]:
        names: set[str] = set()
        for proc in psutil.process_iter(["name"]):
            try:
                name = proc.info["name"]
                if name:
                    names.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return sorted(names, key=str.lower)
