from __future__ import annotations

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtGui import QColor, QIcon
from PySide6.QtWidgets import (
    QFrame, QGraphicsDropShadowEffect, QHBoxLayout, QLabel, QProgressBar,
    QPushButton, QVBoxLayout, QWidget,
)

from config import (
    ASSETS_DIR,
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


def _pill(text: str, fg: str, bg: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"color: {fg}; background: {bg}; border: none; border-radius: 10px;"
        " font-size: 12px; font-weight: 600; padding: 2px 10px;"
    )
    return lbl


class _IconPill(QWidget):
    def __init__(self, icon_svg: str, text: str, fg: str, bg: str, parent=None):
        super().__init__(parent)
        self._text_lbl = QLabel(text)
        icon_lbl = QLabel()
        icon_lbl.setPixmap(
            QIcon(str(ASSETS_DIR / icon_svg)).pixmap(12, 12)
        )
        icon_lbl.setFixedSize(12, 12)
        icon_lbl.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 2, 10, 2)
        layout.setSpacing(4)
        layout.addWidget(icon_lbl)
        self._text_lbl.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; background: transparent;"
        )
        layout.addWidget(self._text_lbl)
        self.setStyleSheet(
            f"background: {bg}; border: none; border-radius: 10px;"
        )

    def setText(self, text: str) -> None:
        self._text_lbl.setText(text)

    def recolor(self, fg: str, bg: str) -> None:
        self._text_lbl.setStyleSheet(
            f"color: {fg}; font-size: 12px; font-weight: 600; background: transparent;"
        )
        self.setStyleSheet(
            f"background: {bg}; border: none; border-radius: 10px;"
        )


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
        outer.setContentsMargins(16, 10, 16, 8)
        outer.setSpacing(6)

        # Top row
        row = QHBoxLayout()
        row.setSpacing(10)
        outer.addLayout(row)

        # Play / Pause button
        self._play_btn = QPushButton()
        self._play_btn.setIcon(QIcon(str(ASSETS_DIR / "pause.svg")))
        self._play_btn.setIconSize(QSize(20, 20))
        self._play_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._play_btn.setFixedSize(44, 44)
        self._play_btn.clicked.connect(self.sig_toggle_pause.emit)
        row.addWidget(self._play_btn, alignment=Qt.AlignmentFlag.AlignVCenter)

        # Project name above time
        info = QVBoxLayout()
        info.setSpacing(0)

        self._name_lbl = QLabel("Проект")
        self._name_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: 600;"
            " background: transparent;"
        )
        info.addWidget(self._name_lbl)

        self._time_lbl = QLabel("00:00")
        self._time_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 22px; font-weight: 700;"
            ' font-family: "Consolas", "Courier New", monospace;'
            " background: transparent;"
        )
        info.addWidget(self._time_lbl)

        row.addLayout(info)
        row.addStretch()

        # Status pills + stop button
        status_row = QHBoxLayout()
        status_row.setSpacing(8)
        status_row.addStretch()

        self._phase_pill = _IconPill("target.svg", "Фокус", "#ffffff", f"{COLOR_ACCENT}CC")
        self._cycle_pill = _IconPill("cycle.svg", "1/1", COLOR_TEXT_SECONDARY, f"{COLOR_BG_SURFACE}")
        self._breaks_pill = _IconPill("break.svg", "0/0", COLOR_TEXT_SECONDARY, f"{COLOR_BG_SURFACE}")
        self._afk_pill = _pill("👁 AFK", COLOR_ACCENT, f"{COLOR_ACCENT}18")
        self._afk_pill.setVisible(False)
        self._scripts_pill = _pill("⚡ 0", COLOR_TEXT_MUTED, "transparent")

        status_row.addWidget(self._phase_pill)
        status_row.addWidget(self._cycle_pill)
        status_row.addWidget(self._breaks_pill)
        status_row.addWidget(self._afk_pill)
        status_row.addWidget(self._scripts_pill)

        self._stop_btn = QPushButton()
        self._stop_btn.setIcon(QIcon(str(ASSETS_DIR / "reset.svg")))
        self._stop_btn.setIconSize(QSize(16, 16))
        self._stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._stop_btn.setFixedSize(32, 32)
        self._stop_btn.setStyleSheet(self._round_btn_style("#2e1a1a", "#c0392b", 16))
        self._stop_btn.setToolTip("Остановить таймер")
        self._stop_btn.clicked.connect(self.sig_stop.emit)
        status_row.addWidget(self._stop_btn)

        row.addLayout(status_row)

        # Progress bar
        self._progress = QProgressBar()
        self._progress.setRange(0, 1000)
        self._progress.setValue(0)
        self._progress.setTextVisible(False)
        self._progress.setFixedHeight(4)
        self._progress.setStyleSheet(f"""
            QProgressBar {{
                background: {COLOR_BG_SURFACE};
                border-radius: 2px;
            }}
            QProgressBar::chunk {{
                background: {COLOR_ACCENT};
                border-radius: 2px;
            }}
        """)
        outer.addWidget(self._progress)

        # Process activity log
        self._proc_log_widget = QWidget()
        self._proc_log_widget.setStyleSheet("background: transparent;")
        self._proc_log_layout = QHBoxLayout(self._proc_log_widget)
        self._proc_log_layout.setContentsMargins(0, 0, 0, 0)
        self._proc_log_layout.setSpacing(12)
        self._proc_log_widget.setVisible(False)
        outer.addWidget(self._proc_log_widget)

    # ── Helpers ──────────────────────────────────────────────
    def _round_btn_style(self, bg: str, hover: str, radius: int) -> str:
        return f"""
            QPushButton {{
                background: {bg};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: {radius}px;
                font-size: 12px;
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

    def _recolor_pill(self, pill: QLabel, fg: str, bg: str) -> None:
        pill.setStyleSheet(
            f"color: {fg}; background: {bg}; border: none; border-radius: 10px;"
            " font-size: 12px; font-weight: 600; padding: 2px 10px;"
        )

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

        # ── Phase pill ──
        if is_afk_paused:
            self._phase_pill.setText("AFK-пауза")
            self._phase_pill.recolor(_COLOR_AFK_PAUSE, f"{_COLOR_AFK_PAUSE}22")
        elif is_paused:
            self._phase_pill.setText("Пауза")
            self._phase_pill.recolor(COLOR_TEXT_MUTED, f"{COLOR_TEXT_MUTED}18")
        elif phase == "focus":
            self._phase_pill.setText("Фокус")
            self._phase_pill.recolor("#ffffff", f"{COLOR_ACCENT}CC")
        else:
            self._phase_pill.setText("Перерыв")
            self._phase_pill.recolor("#ffffff", f"{_COLOR_BREAK}CC")

        # ── Cycle / breaks pills ──
        cycle = state.get("cycle", 1)
        total_cycles = state.get("total_cycles", 1)
        self._cycle_pill.setText(f"{cycle}/{total_cycles}")

        breaks_done = state.get("breaks_done", 0)
        total_breaks = state.get("total_breaks", 0)
        self._breaks_pill.setText(f"{breaks_done}/{total_breaks}")

        # ── AFK pill ──
        afk_enabled = project.get("afk_tracking", False)
        if afk_enabled:
            self._afk_pill.setVisible(True)
            if is_afk_paused:
                self._afk_pill.setText("👁 нет активности")
                self._recolor_pill(self._afk_pill, _COLOR_AFK_PAUSE, f"{_COLOR_AFK_PAUSE}22")
            else:
                self._afk_pill.setText("👁 AFK")
                self._recolor_pill(self._afk_pill, COLOR_ACCENT, f"{COLOR_ACCENT}18")
        else:
            self._afk_pill.setVisible(False)

        # ── Scripts pill ──
        scripts = project.get("scripts", {})
        if isinstance(scripts, list):
            active_scripts = sum(1 for s in scripts if s.get("command", "").strip())
        else:
            active_scripts = sum(1 for v in scripts.values() if v.strip())
        self._scripts_pill.setText(f"⚡ {active_scripts}")
        if active_scripts:
            self._recolor_pill(self._scripts_pill, "#d4a017", f"#d4a01718")
        else:
            self._recolor_pill(self._scripts_pill, COLOR_TEXT_MUTED, "transparent")

        # ── Progress bar ──
        total = state.get("phase_total", 1) or 1
        progress = int(1000 * (1 - max(remaining, 0) / total))
        self._progress.setValue(max(0, min(1000, progress)))

    def _update_play_btn(self, phase: str, is_paused: bool, is_afk_paused: bool) -> None:
        pause_icon = QIcon(str(ASSETS_DIR / "pause.svg"))
        play_icon = QIcon(str(ASSETS_DIR / "play.svg"))

        if is_afk_paused:
            self._play_btn.setIcon(QIcon())
            self._play_btn.setText("💤")
            self._play_btn.setToolTip("Пауза по AFK — продолжится автоматически")
            self._play_btn.setEnabled(False)
            bg = COLOR_BG_SURFACE
            color = COLOR_TEXT_MUTED
        elif is_paused:
            self._play_btn.setIcon(play_icon)
            self._play_btn.setText("")
            self._play_btn.setToolTip("Продолжить")
            self._play_btn.setEnabled(True)
            bg = COLOR_BG_SURFACE
            color = COLOR_TEXT_PRIMARY
        elif phase == "break":
            self._play_btn.setIcon(pause_icon)
            self._play_btn.setText("")
            self._play_btn.setToolTip("Пауза")
            self._play_btn.setEnabled(True)
            bg = COLOR_BG_SURFACE
            color = _COLOR_BREAK
        else:  # focus, running
            self._play_btn.setIcon(pause_icon)
            self._play_btn.setText("")
            self._play_btn.setToolTip("Пауза")
            self._play_btn.setEnabled(True)
            bg = COLOR_BG_SURFACE
            color = COLOR_ACCENT

        self._play_btn.setIconSize(QSize(20, 20))
        self._play_btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {color};
                border: none;
                border-radius: 22px;
                font-size: 18px;
            }}
            QPushButton:hover {{ background: {COLOR_BG_SURFACE_HOVER}; }}
            QPushButton:disabled {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_MUTED};
            }}
        """)

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