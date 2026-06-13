"""Wide horizontal card shown above the project grid while a focus timer is
running.

Layout:

    [⏸/▶]   Project name              [Фокус][Цикл 2/4][☕1/3]   [⏹]
             MM:SS  (big)                    [👁 AFK][⚡ 2 скрипта]
    [――――――――――――――――――――― progress bar ―――――――――――――――――――――]

- The left icon/button doubles as pause/resume: its color reflects the
  current phase (focus/break), its glyph (⏸/▶) reflects the action it
  performs. During an AFK auto-pause it's disabled and shows 💤.
- The stop/reset button lives separately, top-right of the card.
- All informational tags are grouped on the right into two pill-shaped
  groups: live status (phase / cycle / breaks) and project settings
  (AFK / scripts), so it's clear at a glance what belongs together.
"""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QVBoxLayout, QWidget,
)

from config import (
    CARD_BORDER_R, COLOR_ACCENT, COLOR_BG_CARD, COLOR_BG_SURFACE,
    COLOR_BG_SURFACE_HOVER, COLOR_TEXT_MUTED, COLOR_TEXT_PRIMARY,
    COLOR_TEXT_SECONDARY, SHADOW_ALPHA_NORMAL, SHADOW_BLUR_NORMAL,
    SHADOW_OFFSET_NORMAL,
)

_COLOR_BREAK = "#3a9bdc"
_COLOR_AFK_PAUSE = "#e0a020"


def _pluralize_scripts(n: int) -> str:
    if n == 1:
        return "скрипт"
    if 2 <= n <= 4:
        return "скрипта"
    return "скриптов"


class ActiveTimerCard(QWidget):
    """Shows the live state of the currently-running TimerEngine."""

    sig_toggle_pause = Signal()
    sig_stop = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("ActiveTimerCard")
        self.setStyleSheet(f"""
            #ActiveTimerCard {{
                background-color: {COLOR_BG_CARD};
                border-radius: {CARD_BORDER_R}px;
                border: 1px solid {COLOR_ACCENT}55;
            }}
        """)
        self._setup_ui()
        self._setup_shadow()

    # ── Build ────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 14)
        outer.setSpacing(12)

        row = QHBoxLayout()
        row.setSpacing(18)
        outer.addLayout(row)

        # ── Play / Pause button (also indicates phase via color) ──
        self._play_btn = QPushButton("⏸")
        self._play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_btn.setFixedSize(56, 56)
        self._play_btn.clicked.connect(self.sig_toggle_pause.emit)
        row.addWidget(self._play_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # ── Name + big time ──
        info = QVBoxLayout()
        info.setSpacing(0)

        self._name_lbl = QLabel("Проект")
        self._name_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: 600;"
            " background: transparent;"
        )
        info.addWidget(self._name_lbl)

        self._time_lbl = QLabel("00:00")
        self._time_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 36px; font-weight: 700;"
            ' font-family: "Consolas", "Courier New", monospace;'
            " background: transparent;"
        )
        info.addWidget(self._time_lbl)

        row.addLayout(info)
        row.addStretch()

        # ── Right side: tag groups (top) + stop button ──
        right = QVBoxLayout()
        right.setSpacing(8)
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        row.addLayout(right)

        # Row 1: live status group + stop button
        status_row = QHBoxLayout()
        status_row.setSpacing(10)
        status_row.addStretch()

        self._status_group = QWidget()
        self._status_group.setStyleSheet(
            f"background: {COLOR_BG_SURFACE}; border-radius: 10px;"
        )
        status_layout = QHBoxLayout(self._status_group)
        status_layout.setContentsMargins(12, 6, 12, 6)
        status_layout.setSpacing(10)

        self._phase_lbl = self._tag_label("🎯 Фокус", COLOR_ACCENT)
        self._cycle_lbl = self._tag_label("🔁 Цикл 1/1", COLOR_TEXT_SECONDARY)
        self._breaks_lbl = self._tag_label("☕ 0/0", COLOR_TEXT_SECONDARY)

        status_layout.addWidget(self._phase_lbl)
        status_layout.addWidget(self._divider())
        status_layout.addWidget(self._cycle_lbl)
        status_layout.addWidget(self._divider())
        status_layout.addWidget(self._breaks_lbl)

        status_row.addWidget(self._status_group)

        self._stop_btn = QPushButton("⏹")
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.setFixedSize(36, 36)
        self._stop_btn.setStyleSheet(self._round_btn_style("#2e1a1a", "#c0392b", 18))
        self._stop_btn.setToolTip("Остановить таймер")
        self._stop_btn.clicked.connect(self.sig_stop.emit)
        status_row.addWidget(self._stop_btn)

        right.addLayout(status_row)

        # Row 2: project settings group (AFK / scripts)
        settings_row = QHBoxLayout()
        settings_row.setSpacing(10)
        settings_row.addStretch()

        self._config_group = QWidget()
        self._config_group.setStyleSheet(
            f"background: transparent; border: 1px solid {COLOR_BG_SURFACE};"
            " border-radius: 10px;"
        )
        config_layout = QHBoxLayout(self._config_group)
        config_layout.setContentsMargins(12, 5, 12, 5)
        config_layout.setSpacing(10)

        self._afk_lbl = self._tag_label("👁 AFK включён", COLOR_ACCENT)
        self._afk_divider = self._divider()
        self._scripts_lbl = self._tag_label("⚡ 0 скриптов", COLOR_TEXT_MUTED)

        config_layout.addWidget(self._afk_lbl)
        config_layout.addWidget(self._afk_divider)
        config_layout.addWidget(self._scripts_lbl)

        settings_row.addWidget(self._config_group)
        right.addLayout(settings_row)

        # ── Progress bar ──
        self._progress = QProgressBar()
        self._progress.setRange(0, 1000)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(6)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background: {COLOR_BG_SURFACE};
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background: {COLOR_ACCENT};
                border-radius: 3px;
            }}
        """)
        outer.addWidget(self._progress)

        # ── Process activity log ──
        self._proc_log_widget = QWidget()
        self._proc_log_widget.setStyleSheet("background: transparent;")
        self._proc_log_layout = QHBoxLayout(self._proc_log_widget)
        self._proc_log_layout.setContentsMargins(0, 0, 0, 0)
        self._proc_log_layout.setSpacing(12)
        self._proc_log_widget.setVisible(False)
        outer.addWidget(self._proc_log_widget)

    # ── Helpers ──────────────────────────────────────────────
    def _tag_label(self, text: str, color: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600;"
            " background: transparent;"
        )
        return lbl

    def _divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.VLine)
        line.setFixedSize(1, 14)
        line.setStyleSheet(f"background: {COLOR_TEXT_MUTED}44; border: none;")
        return line

    def _round_btn_style(self, bg: str, hover: str, radius: int) -> str:
        return f"""
            QPushButton {{
                background: {bg};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: {radius}px;
                font-size: 14px;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:disabled {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_MUTED};
            }}
        """

    def _setup_shadow(self) -> None:
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        shadow.setOffset(0, SHADOW_OFFSET_NORMAL)
        shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_NORMAL))
        self.setGraphicsEffect(shadow)

    # ── State updates ────────────────────────────────────────
    def update_state(self, state: dict) -> None:
        project = state.get("project") or {}

        self._name_lbl.setText(project.get("name", "Проект"))

        remaining = state.get("phase_remaining", 0)
        mins, secs = divmod(max(remaining, 0), 60)
        self._time_lbl.setText(f"{mins:02d}:{secs:02d}")

        phase = state.get("phase", "focus")
        is_paused = state.get("is_paused", False)
        is_afk_paused = state.get("is_afk_paused", False)

        # ── Play / pause button ──
        self._update_play_btn(phase, is_paused, is_afk_paused)

        # ── Phase tag ──
        if is_afk_paused:
            self._phase_lbl.setText("💤 AFK-пауза")
            self._set_tag_color(self._phase_lbl, _COLOR_AFK_PAUSE)
        elif is_paused:
            self._phase_lbl.setText("⏸ Пауза")
            self._set_tag_color(self._phase_lbl, COLOR_TEXT_MUTED)
        elif phase == "focus":
            self._phase_lbl.setText("🎯 Фокус")
            self._set_tag_color(self._phase_lbl, COLOR_ACCENT)
        else:
            self._phase_lbl.setText("☕ Перерыв")
            self._set_tag_color(self._phase_lbl, _COLOR_BREAK)

        # ── Cycle / breaks tags ──
        cycle = state.get("cycle", 1)
        total_cycles = state.get("total_cycles", 1)
        self._cycle_lbl.setText(f"🔁 Цикл {cycle}/{total_cycles}")

        breaks_done = state.get("breaks_done", 0)
        total_breaks = state.get("total_breaks", 0)
        self._breaks_lbl.setText(f"☕ {breaks_done}/{total_breaks}")

        # ── Settings group: AFK ──
        afk_enabled = project.get("afk_tracking", False)
        self._afk_lbl.setVisible(afk_enabled)
        self._afk_divider.setVisible(afk_enabled)
        if afk_enabled:
            if is_afk_paused:
                self._afk_lbl.setText("👁 AFK: нет активности")
                self._set_tag_color(self._afk_lbl, _COLOR_AFK_PAUSE)
            else:
                self._afk_lbl.setText("👁 AFK включён")
                self._set_tag_color(self._afk_lbl, COLOR_ACCENT)

        # ── Settings group: scripts ──
        scripts = project.get("scripts", {})
        active_scripts = sum(1 for v in scripts.values() if v.strip())
        self._scripts_lbl.setText(
            f"⚡ {active_scripts} {_pluralize_scripts(active_scripts)}"
        )
        self._set_tag_color(
            self._scripts_lbl,
            "#d4a017" if active_scripts else COLOR_TEXT_MUTED,
        )

        # ── Progress bar ──
        total = state.get("phase_total", 1) or 1
        progress = int(1000 * (1 - max(remaining, 0) / total))
        self._progress.setValue(max(0, min(1000, progress)))

    def _update_play_btn(self, phase: str, is_paused: bool, is_afk_paused: bool) -> None:
        if is_afk_paused:
            self._play_btn.setText("💤")
            self._play_btn.setToolTip("Пауза по AFK — продолжится автоматически")
            self._play_btn.setEnabled(False)
            bg = f"{COLOR_TEXT_MUTED}22"
            color = COLOR_TEXT_MUTED
        elif is_paused:
            self._play_btn.setText("▶")
            self._play_btn.setToolTip("Продолжить")
            self._play_btn.setEnabled(True)
            bg = f"{COLOR_TEXT_MUTED}22"
            color = COLOR_TEXT_PRIMARY
        elif phase == "break":
            self._play_btn.setText("⏸")
            self._play_btn.setToolTip("Пауза")
            self._play_btn.setEnabled(True)
            bg = f"{_COLOR_BREAK}22"
            color = _COLOR_BREAK
        else:  # focus, running
            self._play_btn.setText("⏸")
            self._play_btn.setToolTip("Пауза")
            self._play_btn.setEnabled(True)
            bg = f"{COLOR_ACCENT}22"
            color = COLOR_ACCENT

        self._play_btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {color};
                border: none;
                border-radius: 28px;
                font-size: 20px;
            }}
            QPushButton:hover {{ background: {COLOR_BG_SURFACE_HOVER}; }}
            QPushButton:disabled {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_MUTED};
            }}
        """)

    def _set_tag_color(self, lbl: QLabel, color: str) -> None:
        lbl.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600;"
            " background: transparent;"
        )

    def update_process_log(self, log: dict[str, int]) -> None:
        for i in reversed(range(self._proc_log_layout.count())):
            item = self._proc_log_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        if not log:
            self._proc_log_widget.setVisible(False)
            return

        self._proc_log_widget.setVisible(True)
        sorted_items = sorted(log.items(), key=lambda x: -x[1])
        for name, secs in sorted_items:
            mins, secs_rem = divmod(secs, 60)
            if mins > 0:
                text = f"🟢 {name}  {mins}м {secs_rem}с"
            else:
                text = f"🟢 {name}  {secs_rem}с"
            lbl = QLabel(text)
            lbl.setStyleSheet(
                f"color: {COLOR_TEXT_MUTED}; font-size: 11px; background: transparent;"
            )
            self._proc_log_layout.addWidget(lbl)

        self._proc_log_layout.addStretch()