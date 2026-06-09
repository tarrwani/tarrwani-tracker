from db.queries import create_project, add_process, get_processes
from core.tracker import Tracker
import time

# Создаём тестовый проект
pid = create_project("Тест", "#4A90D9", afk_enabled=True)
add_process(pid, "code.exe")

project = {
    "id": pid,
    "name": "Тест",
    "afk_enabled": True,
    "processes": get_processes(pid)
}

print(f"Проект: {project}")

tracker = Tracker()
tracker.start(project)
print("Трекер запущен. Переключайся между окнами — смотри что происходит")

for i in range(15):
    time.sleep(1)
    status = "⏸ пауза" if tracker.is_paused else "▶ идёт"
    print(f"{i+1}s | {status} | активный процесс отслеживается")

tracker.stop()
print("Трекер остановлен")