import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
# Paths
BASE_DIR = Path(__file__).resolve().parent
INTERFACE_DIR = BASE_DIR / "ui"

# Database
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 54321),
    "dbname": os.getenv("DB_NAME", "timetracker"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

# Pomodoro
POMODORO_WORK = 25 * 60
POMODORO_BREAK = 5 * 60

# AFK
AFK_TIMEOUT = 3 * 60

# App
APP_NAME = "Tarrwani Tracker"
APP_VERSION = "0.1.1"
ICON_PATH = BASE_DIR / "assets" / "icon.png"