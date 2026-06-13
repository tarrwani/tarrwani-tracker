import time
import threading
import win32gui
import win32process
import psutil
from database.queries import start_session, stop_session, log_afk_start, log_afk_end
from config import AFK_TIMEOUT

class Tracker:
    def __init__(self):
        self.active_project = None      # текущий проект (dict)
        self.session_id = None          # id текущей сессии в БД
        self.is_running = False         # трекер запущен?
        self.is_paused = False          # на паузе?
        self.afk_id = None              # id текущего afk события
        self._thread = None             # фоновый поток

    def start(self, project: dict):
        """Запускаем трекинг проекта"""
        self.active_project = project
        self.session_id = start_session(project["id"])
        self.is_running = True
        self.is_paused = False
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Останавливаем трекинг"""
        self.is_running = False
        if self.session_id:
            stop_session(self.session_id)
        self.session_id = None
        self.active_project = None

    def _get_active_process(self) -> str:
        """Возвращает имя процесса активного окна"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name().lower()
        except Exception:
            return ""

    def _loop(self):
        """Основной цикл — крутится в фоне пока трекер запущен"""
        while self.is_running:
            active_process = self._get_active_process()
            processes = [p.lower() for p in self.active_project.get("processes", [])]
            process_match = active_process in processes

            if process_match and self.is_paused:
                # вернулись к нужному процессу — снимаем паузу
                self._resume()
            elif not process_match and not self.is_paused:
                # ушли с нужного процесса — пауза
                self._pause()

            time.sleep(1)

    def _pause(self):
        self.is_paused = True
        if self.active_project.get("afk_enabled") and self.session_id:
            self.afk_id = log_afk_start(self.session_id)

    def _resume(self):
        self.is_paused = False
        if self.afk_id:
            log_afk_end(self.afk_id)
            self.afk_id = None