import threading
import time
from pynput import mouse, keyboard
from config import AFK_TIMEOUT


class AFKDetector:
    def __init__(self, on_afk=None, on_return=None):
        self.on_afk = on_afk        # коллбэк — пользователь ушёл
        self.on_return = on_return  # коллбэк — пользователь вернулся
        self.is_afk = False
        self.is_running = False
        self._last_activity = time.time()
        self._thread = None

    def start(self):
        self.is_running = True
        self._last_activity = time.time()

        # слушаем мышь и клавиатуру
        self._mouse = mouse.Listener(on_move=self._on_activity,
                                     on_click=self._on_activity)
        self._keyboard = keyboard.Listener(on_press=self._on_activity)
        self._mouse.start()
        self._keyboard.start()

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.is_running = False
        self._mouse.stop()
        self._keyboard.stop()

    def _on_activity(self, *args):
        """Любая активность — обновляем время"""
        was_afk = self.is_afk
        self._last_activity = time.time()
        self.is_afk = False
        if was_afk and self.on_return:
            self.on_return()

    def _loop(self):
        while self.is_running:
            idle = time.time() - self._last_activity
            if idle >= AFK_TIMEOUT and not self.is_afk:
                self.is_afk = True
                if self.on_afk:
                    self.on_afk()
            time.sleep(1)