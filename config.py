import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 54321),
    "dbname": os.getenv("DB_NAME", "timetracker"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

POMODORO_WORK = 25 * 60
POMODORO_BREAK = 5 * 60
AFK_TIMEOUT = 3 * 60
