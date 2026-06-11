from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class UserSettings:
    """Runtime-editable behaviour settings. Serialised to/from JSON by SettingsManager."""

    pomodoro_work:         int = 25 * 60
    pomodoro_break:        int = 5 * 60
    afk_timeout:           int = 3 * 60
    default_timer_minutes: int = 5
    timer_presets: List[Tuple[str, int]] = field(default_factory=lambda: [
        ("1 минута",  60),
        ("3 минуты",  180),
        ("5 минут",   300),
        ("10 минут",  600),
    ])


# ── Default instance ──────────────────────────────────────────
_s = UserSettings()

# Flat re-exports — existing imports stay untouched
POMODORO_WORK          = _s.pomodoro_work
POMODORO_BREAK         = _s.pomodoro_break
AFK_TIMEOUT            = _s.afk_timeout
DEFAULT_TIMER_MINUTES  = _s.default_timer_minutes
TIMER_PRESETS          = _s.timer_presets