from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QCompleter,
)
from PySide6.QtCore import Qt, QStringListModel

from config import (
    COLOR_BG_PRIMARY, COLOR_BG_CARD, COLOR_BG_SURFACE, COLOR_BG_SURFACE_HOVER,
    COLOR_BG_BTN, COLOR_BG_BTN_HOVER,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_DISABLED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_TEXT_DISABLED,
    COLOR_SCROLLBAR_TRACK, COLOR_SCROLLBAR_THUMB, COLOR_SCROLLBAR_HOVER,
    DIALOG_PADDING, DIALOG_INPUT_RADIUS, DIALOG_INPUT_FONT,
)
from core.marathon_engine import MarathonEngine
from core.process_tracker import ProcessTracker


class MarathonPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._engine = MarathonEngine(self)
        self._engine.sig_tick.connect(self._on_tick)

        self._tracker: ProcessTracker | None = None
        self._session_accumulator: dict[str, int] = {}

        self._setup_ui()

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
        layout.setContentsMargins(DIALOG_PADDING, 32, DIALOG_PADDING, DIALOG_PADDING)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._build_header(), alignment=Qt.AlignmentFlag.AlignHCenter)

        self._time_card = self._build_time_card()
        layout.addWidget(self._time_card, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._build_controls(), alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addWidget(self._build_process_section())

        self._proc_log_card = self._build_proc_log_card()
        layout.addWidget(self._proc_log_card)

        layout.addStretch()

    def _build_header(self) -> QLabel:
        lbl = QLabel("Марафон")
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 22px; font-weight: 700;"
            " background: transparent;"
        )
        return lbl

    def _build_time_card(self) -> QFrame:
        card = QFrame()
        card.setFixedSize(360, 200)
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border-radius: 20px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_lbl = QLabel("Готов к старту")
        status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        status_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        layout.addWidget(status_lbl)
        self._status_lbl = status_lbl

        self._time_lbl = QLabel("00:00:00")
        self._time_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._time_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 56px; font-weight: 700;"
            ' font-family: "Consolas", "Courier New", monospace;'
            " background: transparent; letter-spacing: 4px;"
        )
        layout.addWidget(self._time_lbl)

        return card

    def _build_controls(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(20)
        row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._toggle_btn = QPushButton("▶ Старт")
        self._toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._toggle_btn.setFixedSize(160, 52)
        self._toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 26px;
                font-size: 17px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        self._toggle_btn.clicked.connect(self._on_toggle)
        row.addWidget(self._toggle_btn)

        self._reset_btn = QPushButton("⏹ Сброс")
        self._reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._reset_btn.setFixedSize(160, 52)
        self._reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 26px;
                font-size: 17px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLOR_BG_SURFACE_HOVER}; color: {COLOR_TEXT_PRIMARY}; }}
            QPushButton:disabled {{
                background: {COLOR_BG_BTN};
                color: {COLOR_TEXT_DISABLED};
            }}
        """)
        self._reset_btn.setEnabled(False)
        self._reset_btn.clicked.connect(self._on_reset)
        row.addWidget(self._reset_btn)

        return w

    def _build_process_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        lbl = QLabel("ОТСЛЕЖИВАЕМЫЕ ПРОЦЕССЫ")
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 11px; letter-spacing: 1px;"
            " background: transparent;"
        )
        layout.addWidget(lbl)

        hint = QLabel(
            "Введите имя любого приложения (например: figma.exe, chrome.exe, notepad.exe). "
            "Будет засчитываться время, пока окно этого приложения активно."
        )
        hint.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._process_input = _ProcessTagInputInline()
        layout.addWidget(self._process_input)

        return w

    def _build_proc_log_card(self) -> QFrame:
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {COLOR_BG_CARD};
                border-radius: 16px;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        header = QLabel("Активность приложений")
        header.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: 600;"
            " background: transparent;"
        )
        layout.addWidget(header)

        self._log_container = QWidget()
        self._log_container.setStyleSheet("background: transparent;")
        self._log_layout = QVBoxLayout(self._log_container)
        self._log_layout.setContentsMargins(0, 0, 0, 0)
        self._log_layout.setSpacing(6)

        empty = QLabel("Пока нет данных об активности")
        empty.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        self._log_layout.addWidget(empty)
        self._log_empty = empty

        layout.addWidget(self._log_container)

        return card

    # ── Controls ──────────────────────────────────────────

    def _on_toggle(self):
        if not self._engine.is_running:
            self._engine.start()
            tracked = self._process_input.get_tracked()
            if tracked:
                self._session_accumulator = {n: 0 for n in tracked}
                self._tracker = ProcessTracker(tracked, self)
                self._tracker.sig_tick.connect(self._on_tracker_tick)
                self._tracker.start()
        else:
            self._engine.toggle_pause()
            if self._tracker:
                if self._engine.is_paused:
                    self._tracker.pause()
                else:
                    self._tracker.resume()
        self._update_ui()

    def _on_reset(self):
        self._engine.stop()
        if self._tracker is not None:
            partial = self._tracker.stop()
            self._tracker.deleteLater()
            self._tracker = None
            for name, secs in partial.items():
                self._session_accumulator[name] = self._session_accumulator.get(name, 0) + secs
        self._session_accumulator.clear()
        self._update_time_display(0)
        self._update_status("Готов к старту", COLOR_TEXT_MUTED)
        self._update_process_log({})
        self._update_ui()

    # ── Tick handlers ─────────────────────────────────────

    def _on_tick(self, state: dict):
        self._update_time_display(state.get("elapsed", 0))
        running = state.get("running", False)
        paused = state.get("paused", False)
        if running and not paused:
            self._update_status("🟢 Идёт запись...", COLOR_ACCENT)
        elif paused:
            self._update_status("⏸ На паузе", COLOR_TEXT_MUTED)

    def _on_tracker_tick(self, tracker_log: dict):
        merged = dict(self._session_accumulator)
        for name, secs in tracker_log.items():
            merged[name] = merged.get(name, 0) + secs
        self._update_process_log(merged)

    # ── UI updates ────────────────────────────────────────

    def _update_time_display(self, total_secs: int):
        h, rem = divmod(total_secs, 3600)
        m, s = divmod(rem, 60)
        self._time_lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")

    def _update_status(self, text: str, color: str):
        self._status_lbl.setText(text)
        self._status_lbl.setStyleSheet(
            f"color: {color}; font-size: 13px; background: transparent;"
        )

    def _update_ui(self):
        running = self._engine.is_running
        paused = self._engine.is_paused

        if not running:
            self._toggle_btn.setText("▶ Старт")
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_ACCENT};
                    color: #ffffff;
                    border: none;
                    border-radius: 26px;
                    font-size: 17px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
            """)
            self._reset_btn.setEnabled(False)
        elif paused:
            self._toggle_btn.setText("▶ Продолжить")
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_BG_SURFACE};
                    color: {COLOR_ACCENT};
                    border: 2px solid {COLOR_ACCENT};
                    border-radius: 26px;
                    font-size: 17px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background: {COLOR_BG_SURFACE_HOVER}; }}
            """)
            self._reset_btn.setEnabled(True)
        else:
            self._toggle_btn.setText("⏸ Пауза")
            self._toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background: {COLOR_ACCENT};
                    color: #ffffff;
                    border: none;
                    border-radius: 26px;
                    font-size: 17px;
                    font-weight: 600;
                }}
                QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
            """)
            self._reset_btn.setEnabled(True)

        self._process_input.setEnabled(not running)

    def _on_window_minimized(self, minimized: bool):
        if not self._engine.is_running:
            return
        if minimized and not self._engine.is_paused:
            self._on_toggle()
            self._update_status("⏸ Приложение свёрнуто", COLOR_TEXT_MUTED)

    def _update_process_log(self, log: dict[str, int]):
        self._log_empty.setVisible(not log)
        for i in reversed(range(self._log_layout.count())):
            item = self._log_layout.itemAt(i)
            if item.widget() and item.widget() is not self._log_empty:
                item.widget().deleteLater()

        if not log:
            return

        sorted_items = sorted(log.items(), key=lambda x: -x[1])
        for name, secs in sorted_items:
            h, rem = divmod(secs, 3600)
            m, s = divmod(rem, 60)
            parts = []
            if h:
                parts.append(f"{h}ч")
            if m:
                parts.append(f"{m}м")
            parts.append(f"{s}с")
            time_str = " ".join(parts)

            row = QWidget()
            row.setStyleSheet("background: transparent;")
            row.setFixedHeight(36)
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.setSpacing(12)

            dot = QLabel("🟢")
            dot.setStyleSheet("font-size: 10px; background: transparent;")
            rl.addWidget(dot)

            name_lbl = QLabel(name)
            name_lbl.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-size: 13px; font-weight: 500;"
                " background: transparent;"
            )
            rl.addWidget(name_lbl, stretch=1)

            time_lbl = QLabel(time_str)
            time_lbl.setStyleSheet(
                f"color: {COLOR_ACCENT}; font-size: 13px; font-weight: 600;"
                ' font-family: "Consolas", "Courier New", monospace;'
                " background: transparent;"
            )
            rl.addWidget(time_lbl)

            self._log_layout.addWidget(row)


class _ProcessTagInputInline(QWidget):
    """Tag input: accepts any process name, not just running ones."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected: list[str] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        input_row = QHBoxLayout()
        input_row.setSpacing(8)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Введите имя процесса...")
        self._input.setFixedHeight(36)
        self._input.setStyleSheet(f"""
            QLineEdit {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid transparent;
                border-radius: {DIALOG_INPUT_RADIUS}px;
                font-size: {DIALOG_INPUT_FONT}px;
                padding: 0 14px;
            }}
            QLineEdit:focus {{ border: 2px solid {COLOR_ACCENT}; }}
            QLineEdit::placeholder {{ color: {COLOR_TEXT_MUTED}; }}
        """)
        self._input.returnPressed.connect(self._add_current)
        input_row.addWidget(self._input, stretch=1)

        add_btn = QPushButton("+")
        add_btn.setFixedSize(36, 36)
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 18px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        add_btn.clicked.connect(self._add_current)
        input_row.addWidget(add_btn)

        layout.addLayout(input_row)

        self._tags = QWidget()
        self._tags.setStyleSheet("background: transparent;")
        self._tags_layout = QHBoxLayout(self._tags)
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(6)
        layout.addWidget(self._tags)

        self._setup_completer()

    def _setup_completer(self):
        from core.process_tracker import ProcessTracker
        names = ProcessTracker.get_unique_process_names()
        model = QStringListModel(names, self)
        completer = QCompleter(model, self)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.activated.connect(self._on_completer_activated)
        self._input.setCompleter(completer)

    def _on_completer_activated(self, text: str):
        self._input.setText(text)
        self._add_current()

    def _add_current(self):
        name = self._input.text().strip()
        if not name:
            return
        if name.lower() not in {n.lower() for n in self._selected}:
            self._selected.append(name)
            self._rebuild_tags()
        self._input.clear()

    def _remove_tag(self, name: str):
        lower = name.lower()
        match = next((n for n in self._selected if n.lower() == lower), None)
        if match:
            self._selected.remove(match)
            self._rebuild_tags()

    def _rebuild_tags(self):
        while self._tags_layout.count():
            item = self._tags_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for name in self._selected:
            tag = QFrame()
            tag.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_BG_SURFACE};
                    border-radius: 6px;
                }}
            """)
            tl = QHBoxLayout(tag)
            tl.setContentsMargins(10, 4, 4, 4)
            tl.setSpacing(6)

            lbl = QLabel(name)
            lbl.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px; background: transparent;"
            )
            tl.addWidget(lbl)

            rm_btn = QPushButton("✕")
            rm_btn.setFixedSize(18, 18)
            rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            rm_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent; border: none;
                    color: {COLOR_TEXT_MUTED}; font-size: 11px; border-radius: 9px;
                }}
                QPushButton:hover {{ background: #c0392b; color: #ffffff; }}
            """)
            rm_btn.clicked.connect(lambda _=None, n=name: self._remove_tag(n))
            tl.addWidget(rm_btn)

            self._tags_layout.addWidget(tag)

        self._tags_layout.addStretch()

    def setEnabled(self, enabled: bool):
        super().setEnabled(enabled)
        self._input.setEnabled(enabled)

    def get_tracked(self) -> list[str]:
        return list(self._selected)

    def set_tracked(self, names: list[str]):
        seen: set[str] = set()
        deduped: list[str] = []
        for n in names:
            if n.lower() not in seen:
                seen.add(n.lower())
                deduped.append(n)
        self._selected = deduped
        self._rebuild_tags()
