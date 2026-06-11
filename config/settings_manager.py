import json
from dataclasses import asdict
from pathlib import Path

from .theme import ThemeConfig
from .user_settings import UserSettings

SETTINGS_PATH = Path.home() / ".tarrwani" / "settings.json"


class SettingsManager:
    """
    Singleton that owns the live ThemeConfig and UserSettings instances.

    Usage
    -----
    from config import settings_manager

    # Read
    color = settings_manager.theme.accent

    # Write & persist
    settings_manager.apply_theme(accent="#ff0000")
    settings_manager.apply_settings(afk_timeout=120)
    """

    _instance: "SettingsManager | None" = None

    def __new__(cls) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialised:
            return
        self._theme    = ThemeConfig()
        self._settings = UserSettings()
        self._load()
        self._initialised = True

    # ── Public properties ─────────────────────────────────────

    @property
    def theme(self) -> ThemeConfig:
        return self._theme

    @property
    def settings(self) -> UserSettings:
        return self._settings

    # ── Mutation helpers ──────────────────────────────────────

    def apply_theme(self, **kwargs) -> None:
        """Patch theme fields by name and persist to disk."""
        for key, value in kwargs.items():
            if hasattr(self._theme, key):
                setattr(self._theme, key, value)
            else:
                raise AttributeError(f"ThemeConfig has no field '{key}'")
        self._save()

    def apply_settings(self, **kwargs) -> None:
        """Patch settings fields by name and persist to disk."""
        for key, value in kwargs.items():
            if hasattr(self._settings, key):
                setattr(self._settings, key, value)
            else:
                raise AttributeError(f"UserSettings has no field '{key}'")
        self._save()

    def reset_theme(self) -> None:
        """Restore default theme and persist."""
        self._theme = ThemeConfig()
        self._save()

    def reset_settings(self) -> None:
        """Restore default user settings and persist."""
        self._settings = UserSettings()
        self._save()

    # ── Persistence ───────────────────────────────────────────

    def _load(self) -> None:
        if not SETTINGS_PATH.exists():
            return
        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))

            if theme_data := data.get("theme"):
                valid = {k: v for k, v in theme_data.items()
                         if k in ThemeConfig.__dataclass_fields__}
                self._theme = ThemeConfig(**valid)

            if user_data := data.get("settings"):
                # JSON stores lists of lists; convert back to list[tuple]
                if "timer_presets" in user_data:
                    user_data["timer_presets"] = [
                        tuple(p) for p in user_data["timer_presets"]
                    ]
                valid = {k: v for k, v in user_data.items()
                         if k in UserSettings.__dataclass_fields__}
                self._settings = UserSettings(**valid)

        except Exception as exc:
            print(f"[SettingsManager] load failed — using defaults ({exc})")

    def _save(self) -> None:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "theme":    asdict(self._theme),
            "settings": asdict(self._settings),
        }
        try:
            SETTINGS_PATH.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as exc:
            print(f"[SettingsManager] save failed ({exc})")


# Module-level singleton — import this everywhere
settings_manager = SettingsManager()