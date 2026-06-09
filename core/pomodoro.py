import threading
import time
from config import POMODORO_WORK, POMODORO_BREAK


class PomodoroTimer:
    def __init__(self, on_work_end=None, on_break_end=None):
        self.on_work_end = on_work_end      # коллбэк — рабочий интервал кончился
        self.on_break_end = on_break_end    # коллбэк — перерыв кончился
        self.is_running = False
        self.is_break = False               # сейчас перерыв?
        self.remaining = POMODORO_WORK      # секунд осталось
        self._thread = None

    def start(self):
        self.is_running = True
        self.is_break = False
        self.remaining = POMODORO_WORK
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _loop(self):
        while self.is_running:
            time.sleep(1)
            self.remaining -= 1

            if self.remaining <= 0:
                if not self.is_break:
                    # рабочий интервал закончился
                    self.is_break = True
                    self.remaining = POMODORO_BREAK
                    if self.on_work_end:
                        self.on_work_end()
                else:
                    # перерыв закончился
                    self.is_break = False
                    self.remaining = POMODORO_WORK
                    if self.on_break_end:
                        self.on_break_end()

    @property
    def time_str(self) -> str:
        """Возвращает строку MM:SS для отображения в UI"""
        mins = self.remaining // 60
        secs = self.remaining % 60
        return f"{mins:02d}:{secs:02d}"