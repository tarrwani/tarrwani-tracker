from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt

from config import (
    COLOR_BG_PRIMARY, COLOR_BG_CARD, COLOR_BG_SURFACE, COLOR_BG_SURFACE_HOVER,
    COLOR_BG_BTN, COLOR_BG_BTN_HOVER,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_DISABLED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_TEXT_DISABLED,
    COLOR_SCROLLBAR_TRACK, COLOR_SCROLLBAR_THUMB, COLOR_SCROLLBAR_HOVER,
    DIALOG_PADDING,
)

_PERIOD_LABELS = ["День", "Неделя", "Месяц", "Всё время"]
_PERIOD_SECS = [86400, 604800, 2592000, None]


def _fmt_duration(secs: int) -> str:
    h, rem = divmod(int(secs), 3600)
    m, s = divmod(rem, 60)
    parts = []
    if h:
        parts.append(f"{h}ч")
    if m:
        parts.append(f"{m}м")
    if s or not parts:
        parts.append(f"{s}с")
    return " ".join(parts)


def _collect_sessions(projects: list[dict], period_idx: int) -> list[dict]:
    now = time.time()
    limit = _PERIOD_SECS[period_idx]
    sessions = []
    for p in projects:
        for s in p.get("sessions", []):
            ts = s.get("timestamp", 0)
            if limit is None or (now - ts) <= limit:
                sessions.append(s)
    return sessions


def _format_timestamp(ts: float) -> str:
    dt = datetime.fromtimestamp(ts)
    today = datetime.now()
    if dt.date() == today.date():
        return "Сегодня " + dt.strftime("%H:%M")
    if (today - dt).days == 1:
        return "Вчера " + dt.strftime("%H:%M")
    return dt.strftime("%d.%m.%Y %H:%M")


class StatsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects: list[dict] = []
        self._period_idx = 3
        self._setup_ui()

    def set_projects(self, projects: list[dict]) -> None:
        self._projects = projects
        self._refresh()

    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {COLOR_SCROLLBAR_TRACK};
                width: 6px;
                border-radius: 3px;
            }}
            QScrollBar::handle:vertical {{
                background: {COLOR_SCROLLBAR_THUMB};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {COLOR_SCROLLBAR_HOVER}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        root.addWidget(scroll, stretch=1)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(DIALOG_PADDING, 28, DIALOG_PADDING, DIALOG_PADDING)
        layout.setSpacing(20)

        layout.addWidget(self._build_header(), alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self._build_period_bar())
        self._summary_row = self._build_summary_row()
        layout.addWidget(self._summary_row)
        self._projects_section = self._build_section("Проекты")
        layout.addWidget(self._projects_section)
        self._apps_section = self._build_section("Приложения")
        layout.addWidget(self._apps_section)
        self._history_section = self._build_history_section()
        layout.addWidget(self._history_section)
        layout.addStretch()

    def _build_header(self) -> QLabel:
        lbl = QLabel("Статистика")
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 22px; font-weight: 700;"
            " background: transparent;"
        )
        return lbl

    def _build_period_bar(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self._period_btns: list[QPushButton] = []
        for i, label in enumerate(_PERIOD_LABELS):
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setChecked(i == self._period_idx)
            btn.clicked.connect(lambda _=None, idx=i: self._set_period(idx))
            self._period_btns.append(btn)
            row.addWidget(btn)

        self._update_period_style()
        return w

    def _update_period_style(self):
        for i, btn in enumerate(self._period_btns):
            active = i == self._period_idx
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_ACCENT if active else COLOR_BG_BTN};
                    color: {"#ffffff" if active else COLOR_TEXT_SECONDARY};
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: {600 if active else 500};
                    padding: 0 18px;
                }}
                QPushButton:hover {{
                    background: {COLOR_ACCENT_HOVER if active else COLOR_BG_BTN_HOVER};
                    color: {"#ffffff" if active else COLOR_TEXT_PRIMARY};
                }}
            """)

    def _set_period(self, idx: int):
        self._period_idx = idx
        self._update_period_style()
        self._refresh()

    # ── Summary row ──────────────────────────────────────

    def _build_summary_row(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(16)
        self._summary_cards: list[QFrame] = []
        for _ in range(3):
            card = self._summary_card("—", "—")
            self._summary_cards.append(card)
            row.addWidget(card)
        return w

    def _summary_card(self, value: str, label: str) -> QFrame:
        card = QFrame()
        card.setFixedHeight(90)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border-radius: 14px;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(4)

        val = QLabel(value)
        val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        val.setStyleSheet(
            f"color: {COLOR_ACCENT}; font-size: 26px; font-weight: 700;"
            " background: transparent;"
        )
        layout.addWidget(val)
        self._summary_vals = getattr(self, "_summary_vals", [])
        self._summary_vals.append(val)

        lbl = QLabel(label)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        layout.addWidget(lbl)

        return card

    # ── Generic section ──────────────────────────────────

    def _build_section(self, title: str) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel(title.upper())
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 11px; letter-spacing: 1px;"
            " background: transparent;"
        )
        layout.addWidget(lbl)

        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border-radius: 14px;
            }}
        """)
        self._section_cards = getattr(self, "_section_cards", [])
        self._section_cards.append(card)
        layout.addWidget(card)

        return w

    # ── History section ──────────────────────────────────

    def _build_history_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel("ИСТОРИЯ СЕССИЙ")
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 11px; letter-spacing: 1px;"
            " background: transparent;"
        )
        layout.addWidget(lbl)

        self._history_card = QFrame()
        self._history_card.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border-radius: 14px;
            }}
        """)
        self._history_layout = QVBoxLayout(self._history_card)
        self._history_layout.setContentsMargins(20, 16, 20, 16)
        self._history_layout.setSpacing(6)
        layout.addWidget(self._history_card)

        self._history_empty = QLabel("Нет завершённых сессий")
        self._history_empty.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        self._history_layout.addWidget(self._history_empty)

        return w

    # ── Refresh ──────────────────────────────────────────

    def _refresh(self):
        sessions = _collect_sessions(self._projects, self._period_idx)

        total_secs = 0
        proc_totals: dict[str, int] = defaultdict(int)
        project_secs: dict[str, int] = defaultdict(int)

        for s in sessions:
            total_secs += s.get("planned_secs", 0)
            pname = s.get("project_name", "Без проекта")
            project_secs[pname] += s.get("planned_secs", 0)
            for app, secs in s.get("process_log", {}).items():
                proc_totals[app] += secs
            total_secs += s.get("duration_correction", 0)

        n_sessions = len(sessions)
        n_projects = len(self._projects)

        self._summary_vals[0].setText(_fmt_duration(total_secs) if total_secs else "—")
        self._summary_vals[1].setText(str(n_sessions))
        self._summary_vals[2].setText(str(n_projects))

        self._refresh_bar_section(self._section_cards[0], project_secs, "Нет данных по проектам")
        self._refresh_bar_section(self._section_cards[1], proc_totals, "Нет данных по приложениям")
        self._refresh_history(sessions)

    def _refresh_bar_section(self, card: QFrame, data: dict[str, int], empty_text: str):
        for i in reversed(range(card.layout().count() if card.layout() else 0)):
            item = card.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        old = card.layout()
        if old:
            QWidget().setLayout(old)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        if not data:
            lbl = QLabel(empty_text)
            lbl.setStyleSheet(
                f"color: {COLOR_TEXT_MUTED}; font-size: 13px; background: transparent;"
            )
            layout.addWidget(lbl)
            return

        max_val = max(data.values())
        sorted_items = sorted(data.items(), key=lambda x: -x[1])

        for name, val in sorted_items:
            frac = val / max_val if max_val else 0

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(12)

            n_lbl = QLabel(name)
            n_lbl.setFixedWidth(160)
            n_lbl.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: 500;"
                " background: transparent;"
            )
            rl.addWidget(n_lbl)

            bar_bg = QFrame()
            bar_bg.setFixedHeight(16)
            bar_bg.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_BG_SURFACE};
                    border-radius: 8px;
                }}
            """)
            bar_bg_layout = QHBoxLayout(bar_bg)
            bar_bg_layout.setContentsMargins(0, 0, 0, 0)

            bar_fill = QFrame()
            bar_fill.setFixedHeight(16)
            bar_fill.setFixedWidth(int(frac * 200))
            bar_fill.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_ACCENT};
                    border-radius: 8px;
                }}
            """)
            bar_bg_layout.addWidget(bar_fill)
            bar_bg_layout.addStretch()

            rl.addWidget(bar_bg, stretch=1)

            v_lbl = QLabel(_fmt_duration(val))
            v_lbl.setFixedWidth(80)
            v_lbl.setStyleSheet(
                f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; font-weight: 600;"
                " background: transparent;"
            )
            rl.addWidget(v_lbl)

            layout.addWidget(row)

    def _refresh_history(self, sessions: list[dict]):
        for i in reversed(range(self._history_layout.count())):
            item = self._history_layout.itemAt(i)
            if item.widget() and item.widget() is not self._history_empty:
                item.widget().deleteLater()

        if not sessions:
            self._history_empty.setVisible(True)
            return

        self._history_empty.setVisible(False)
        sorted_sessions = sorted(sessions, key=lambda s: s.get("timestamp", 0), reverse=True)
        for s in sorted_sessions[:50]:
            ts = s.get("timestamp", 0)
            pname = s.get("project_name", "—")
            dur = s.get("planned_secs", 0)
            apps = s.get("process_log", {})
            app_str = ", ".join(
                f"{n} {_fmt_duration(v)}" for n, v in sorted(apps.items(), key=lambda x: -x[1])[:3]
            )

            row = QWidget()
            row.setFixedHeight(40)
            row.setStyleSheet("background: transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(16)

            t_lbl = QLabel(_format_timestamp(ts) if ts else "—")
            t_lbl.setFixedWidth(130)
            t_lbl.setStyleSheet(
                f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
            )
            rl.addWidget(t_lbl)

            n_lbl = QLabel(pname)
            n_lbl.setFixedWidth(140)
            n_lbl.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: 600;"
                " background: transparent;"
            )
            rl.addWidget(n_lbl)

            d_lbl = QLabel(_fmt_duration(dur))
            d_lbl.setFixedWidth(60)
            d_lbl.setStyleSheet(
                f"color: {COLOR_ACCENT}; font-size: 13px; font-weight: 600;"
                " background: transparent;"
            )
            rl.addWidget(d_lbl)

            if app_str:
                a_lbl = QLabel(app_str)
                a_lbl.setStyleSheet(
                    f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
                )
                rl.addWidget(a_lbl, stretch=1)

            self._history_layout.addWidget(row)
