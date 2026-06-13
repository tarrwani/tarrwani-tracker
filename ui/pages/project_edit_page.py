"""Project edit / create form.

Emits:
  sig_save(dict)   – user confirmed save; payload is the project dict
  sig_cancel()     – user pressed Back without saving
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QPlainTextEdit, QScrollArea,
    QFrame, QComboBox, QCompleter,
)
from PySide6.QtCore import Qt, Signal, QStringListModel
from PySide6.QtGui import QFont

import psutil

from config import (
    COLOR_BG_PRIMARY, COLOR_BG_CARD, COLOR_BG_SURFACE, COLOR_BG_SURFACE_HOVER,
    COLOR_BG_BTN, COLOR_BG_BTN_HOVER,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_DISABLED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_TEXT_DISABLED,
    COLOR_SCROLLBAR_TRACK, COLOR_SCROLLBAR_THUMB, COLOR_SCROLLBAR_HOVER,
    DIALOG_PADDING, DIALOG_SPACING, DIALOG_INPUT_RADIUS, DIALOG_INPUT_FONT,
    GRID_SPACING,
)
from ui.widgets.time_input import TimeInputWidget
from ui.widgets.toggle_switch import ToggleSwitch


# ── Presets ────────────────────────────────────────────────────
_PRESETS = [
    ("25 / 5",  25, 5),
    ("52 / 17", 52, 17),
    ("90 / 30", 90, 30),
]

# ── Script trigger keys & labels ──────────────────────────────
_SCRIPT_TRIGGERS = [
    ("on_focus_end",      "По окончании фокуса"),
    ("on_break_end",      "По окончании перерыва"),
    ("on_timer_complete", "По завершении всего таймера"),
]


class ProjectEditPage(QWidget):
    sig_save   = Signal(dict)
    sig_cancel = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project: dict = {}
        self._setup_ui()

    # ── Public API ─────────────────────────────────────────────
    def load_project(self, project: dict | None) -> None:
        """Populate form from an existing project dict, or clear it for a new one."""
        self._project = dict(project) if project else {}

        self._name_edit.setText(self._project.get("name", ""))
        self._focus_input.set_value(self._project.get("focus_min", 25))
        self._break_input.set_value(self._project.get("break_min", 5))
        self._cycles_spin.setValue(self._project.get("cycles", 4))
        self._afk_toggle.setChecked(self._project.get("afk_tracking", False))

        tracked = self._project.get("tracked_processes", [])
        self._process_list.set_tracked(tracked)

        scripts = self._project.get("scripts", {})
        for key, editor in self._script_editors.items():
            editor.setPlainText(scripts.get(key, ""))

        is_new = "name" not in self._project
        self._title_lbl.setText("Новый проект" if is_new else "Редактировать проект")
        self._save_btn.setText("Создать" if is_new else "Сохранить")

        self._update_preset_highlight()
        self._name_edit.setFocus()

    # ── Build ──────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Top bar ──
        top_bar = self._build_top_bar()
        outer.addWidget(top_bar)

        # ── Scroll area ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(self._scroll_style())
        outer.addWidget(scroll, stretch=1)

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        scroll.setWidget(container)

        form = QVBoxLayout(container)
        form.setContentsMargins(DIALOG_PADDING, 20, DIALOG_PADDING, DIALOG_PADDING)
        form.setSpacing(DIALOG_SPACING + 4)

        form.addWidget(self._build_name_section())
        form.addWidget(self._section_divider())
        form.addWidget(self._build_time_section())
        form.addWidget(self._section_divider())
        form.addWidget(self._build_cycles_section())
        form.addWidget(self._section_divider())
        form.addWidget(self._build_afk_section())
        form.addWidget(self._section_divider())
        form.addWidget(self._build_process_section())
        form.addWidget(self._section_divider())
        form.addWidget(self._build_scripts_section())
        form.addStretch()

        # ── Bottom save bar ──
        outer.addWidget(self._build_save_bar())

    # ── Top bar ───────────────────────────────────────────────
    def _build_top_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(52)
        bar.setStyleSheet(f"background: {COLOR_BG_CARD};")

        row = QHBoxLayout(bar)
        row.setContentsMargins(16, 0, 16, 0)
        row.setSpacing(12)

        back_btn = QPushButton("← Назад")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {COLOR_TEXT_SECONDARY};
                font-size: 13px;
                padding: 4px 10px;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        back_btn.clicked.connect(self.sig_cancel.emit)
        row.addWidget(back_btn)

        self._title_lbl = QLabel("Новый проект")
        self._title_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 15px; font-weight: 600;"
            " background: transparent;"
        )
        row.addWidget(self._title_lbl, stretch=1)

        return bar

    # ── Name ──────────────────────────────────────────────────
    def _build_name_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self._section_label("Название проекта"))

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Например: Утренняя сессия")
        self._name_edit.setStyleSheet(self._input_style())
        self._name_edit.setFixedHeight(42)
        layout.addWidget(self._name_edit)

        return w

    # ── Time ──────────────────────────────────────────────────
    def _build_time_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        layout.addWidget(self._section_label("Время (минуты)"))

        # Preset buttons
        preset_row = QHBoxLayout()
        preset_row.setSpacing(8)
        self._preset_btns: list[QPushButton] = []
        for label, focus, brk in _PRESETS:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(36)
            btn.setStyleSheet(self._preset_btn_style(active=False))
            btn.clicked.connect(lambda _=None, f=focus, b=brk: self._apply_preset(f, b))
            preset_row.addWidget(btn)
            self._preset_btns.append(btn)

        preset_row.addStretch()
        layout.addLayout(preset_row)

        # Spinners row
        spin_row = QHBoxLayout()
        spin_row.setSpacing(GRID_SPACING * 2)

        self._focus_input = TimeInputWidget(label="Фокус", min_val=1, max_val=480, value=25)
        self._break_input = TimeInputWidget(label="Перерыв", min_val=1, max_val=120, value=5)

        self._focus_input.value_changed.connect(lambda _: self._update_preset_highlight())
        self._break_input.value_changed.connect(lambda _: self._update_preset_highlight())

        spin_row.addStretch()
        spin_row.addWidget(self._focus_input)
        spin_row.addWidget(self._break_input)
        spin_row.addStretch()

        layout.addLayout(spin_row)

        return w

    def _apply_preset(self, focus: int, brk: int) -> None:
        self._focus_input.set_value(focus)
        self._break_input.set_value(brk)
        self._update_preset_highlight()

    def _update_preset_highlight(self) -> None:
        f = self._focus_input.value()
        b = self._break_input.value()
        for btn, (_, pf, pb) in zip(self._preset_btns, _PRESETS):
            active = (f == pf and b == pb)
            btn.setChecked(active)
            btn.setStyleSheet(self._preset_btn_style(active=active))

    def _preset_btn_style(self, active: bool) -> str:
        if active:
            return f"""
                QPushButton {{
                    background: {COLOR_ACCENT};
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 600;
                    padding: 0 18px;
                }}
                QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
            """
        return f"""
            QPushButton {{
                background: {COLOR_BG_BTN};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background: {COLOR_BG_BTN_HOVER};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """

    # ── Cycles ────────────────────────────────────────────────
    def _build_cycles_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        layout.addWidget(self._section_label("Количество циклов"))

        hint = QLabel(
            "Цикл = один период фокуса + один перерыв. "
            "Последний цикл завершается без перерыва."
        )
        hint.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._cycles_spin = QSpinBox()
        self._cycles_spin.setMinimum(1)
        self._cycles_spin.setMaximum(99)
        self._cycles_spin.setValue(4)
        self._cycles_spin.setFixedSize(100, 42)
        self._cycles_spin.setStyleSheet(self._spinbox_style())
        layout.addWidget(self._cycles_spin)

        return w

    # ── AFK ───────────────────────────────────────────────────
    def _build_afk_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        row = QHBoxLayout(w)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(14)

        info = QVBoxLayout()
        info.setSpacing(4)

        lbl = QLabel("Отслеживание AFK")
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; background: transparent;"
        )
        info.addWidget(lbl)

        desc = QLabel("Автоматически ставит таймер на паузу при отсутствии активности.")
        desc.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        desc.setWordWrap(True)
        info.addWidget(desc)

        row.addLayout(info, stretch=1)

        self._afk_toggle = ToggleSwitch()
        row.addWidget(self._afk_toggle, alignment=Qt.AlignmentFlag.AlignVCenter)

        return w

    # ── Process tracking ──────────────────────────────────────
    def _build_process_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._section_label("Отслеживаемые процессы"))

        hint = QLabel(
            "Выберите процессы, активность которых будет записываться в БД во время работы таймера. "
            "Полезно для анализа в каких приложениях вы работали."
        )
        hint.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self._process_list = ProcessTagInput()
        layout.addWidget(self._process_list)

        return w

    # ── Scripts ───────────────────────────────────────────────
    def _build_scripts_section(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(w)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        layout.addWidget(self._section_label("Bash / Shell скрипты"))

        hint = QLabel(
            "Скрипты выполняются в системной оболочке при наступлении выбранного события. "
            "Доступны переменные: $PROJECT_NAME, $CYCLE, $ELAPSED_MIN."
        )
        hint.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Trigger selector
        self._trigger_combo = QComboBox()
        for _, label in _SCRIPT_TRIGGERS:
            self._trigger_combo.addItem(label)
        self._trigger_combo.setFixedHeight(38)
        self._trigger_combo.setStyleSheet(self._combo_style())
        self._trigger_combo.currentIndexChanged.connect(self._on_trigger_changed)
        layout.addWidget(self._trigger_combo)

        # One editor per trigger (only the active one shown)
        self._script_editors: dict[str, QPlainTextEdit] = {}
        self._editor_stack: list[QPlainTextEdit] = []

        for key, _ in _SCRIPT_TRIGGERS:
            editor = QPlainTextEdit()
            editor.setPlaceholderText(
                "# Введите команды bash/shell здесь\n"
                "# Пример:\n"
                "# notify-send \"Фокус завершён!\" && paplay /usr/share/sounds/freedesktop/stereo/complete.oga"
            )
            editor.setFixedHeight(130)
            editor.setStyleSheet(self._editor_style())
            editor.setVisible(False)
            self._script_editors[key] = editor
            self._editor_stack.append(editor)
            layout.addWidget(editor)

        # Show first editor
        self._editor_stack[0].setVisible(True)

        return w

    def _on_trigger_changed(self, index: int) -> None:
        for i, editor in enumerate(self._editor_stack):
            editor.setVisible(i == index)

    # ── Save bar ──────────────────────────────────────────────
    def _build_save_bar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"background: {COLOR_BG_CARD};")

        row = QHBoxLayout(bar)
        row.setContentsMargins(DIALOG_PADDING, 0, DIALOG_PADDING, 0)
        row.setSpacing(12)

        row.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setFixedHeight(40)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_BG_BTN};
                color: {COLOR_TEXT_SECONDARY};
                border: none;
                border-radius: 8px;
                font-size: 13px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background: {COLOR_BG_BTN_HOVER};
                color: {COLOR_TEXT_PRIMARY};
            }}
        """)
        cancel_btn.clicked.connect(self.sig_cancel.emit)
        row.addWidget(cancel_btn)

        self._save_btn = QPushButton("Создать")
        self._save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save_btn.setFixedHeight(40)
        self._save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 28px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
            QPushButton:disabled {{ background: {COLOR_ACCENT_DISABLED}; color: {COLOR_TEXT_DISABLED}; }}
        """)
        self._save_btn.clicked.connect(self._on_save)
        row.addWidget(self._save_btn)

        return bar

    # ── Save logic ────────────────────────────────────────────
    def _on_save(self) -> None:
        name = self._name_edit.text().strip()
        if not name:
            self._name_edit.setPlaceholderText("⚠️ Введите название проекта")
            self._name_edit.setFocus()
            return

        scripts = {key: ed.toPlainText() for key, ed in self._script_editors.items()}

        self._project.update({
            "name":              name,
            "focus_min":         self._focus_input.value(),
            "break_min":         self._break_input.value(),
            "cycles":            self._cycles_spin.value(),
            "afk_tracking":      self._afk_toggle.isChecked(),
            "tracked_processes": self._process_list.get_tracked(),
            "scripts":           scripts,
        })
        self.sig_save.emit(dict(self._project))

    # ── Helpers ───────────────────────────────────────────────
    def _section_label(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 11px; letter-spacing: 1px;"
            " background: transparent;"
        )
        return lbl

    def _section_divider(self) -> QFrame:
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(1)
        line.setStyleSheet(f"background: {COLOR_BG_SURFACE}; border: none;")
        return line

    # ── Styles ────────────────────────────────────────────────
    def _input_style(self) -> str:
        return f"""
            QLineEdit {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid transparent;
                border-radius: {DIALOG_INPUT_RADIUS}px;
                font-size: {DIALOG_INPUT_FONT}px;
                padding: 0 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {COLOR_ACCENT};
            }}
            QLineEdit::placeholder {{
                color: {COLOR_TEXT_MUTED};
            }}
        """

    def _spinbox_style(self) -> str:
        return f"""
            QSpinBox {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid transparent;
                border-radius: {DIALOG_INPUT_RADIUS}px;
                font-size: 16px;
                font-weight: bold;
                padding-left: 14px;
            }}
            QSpinBox:focus {{ border: 2px solid {COLOR_ACCENT}; }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 26px;
                border: none;
                background: {COLOR_BG_BTN};
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background: {COLOR_ACCENT};
            }}
            QSpinBox::up-arrow {{ image: none; }}
            QSpinBox::down-arrow {{ image: none; }}
        """

    def _combo_style(self) -> str:
        return f"""
            QComboBox {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid transparent;
                border-radius: {DIALOG_INPUT_RADIUS}px;
                font-size: 13px;
                padding-left: 12px;
            }}
            QComboBox:focus {{ border: 2px solid {COLOR_ACCENT}; }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 32px;
                border: none;
            }}
            QComboBox QAbstractItemView {{
                background: {COLOR_BG_CARD};
                color: {COLOR_TEXT_PRIMARY};
                border: 1px solid {COLOR_BG_SURFACE};
                selection-background-color: {COLOR_ACCENT};
                outline: none;
            }}
        """

    def _editor_style(self) -> str:
        return f"""
            QPlainTextEdit {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: 2px solid transparent;
                border-radius: {DIALOG_INPUT_RADIUS}px;
                font-family: "Consolas", "Courier New", monospace;
                font-size: 12px;
                padding: 8px;
                selection-background-color: {COLOR_ACCENT};
            }}
            QPlainTextEdit:focus {{ border: 2px solid {COLOR_ACCENT}; }}
        """

    def _scroll_style(self) -> str:
        return f"""
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
        """


class ProcessTagInput(QWidget):
    """Tag-based input for selecting process names (any, not just running)."""

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
        self._input.setPlaceholderText("Введите имя процесса (например: firefox.exe)...")
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

        add_btn = QPushButton("+ Добавить")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.setFixedHeight(36)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        add_btn.clicked.connect(self._add_current)
        input_row.addWidget(add_btn)

        layout.addLayout(input_row)

        self._tags_container = QWidget()
        self._tags_container.setStyleSheet("background: transparent;")
        self._tags_layout = QVBoxLayout(self._tags_container)
        self._tags_layout.setContentsMargins(0, 0, 0, 0)
        self._tags_layout.setSpacing(6)
        layout.addWidget(self._tags_container)

        self._setup_completer()

    def _setup_completer(self):
        from core.process_tracker import ProcessTracker
        names = ProcessTracker.get_unique_process_names()
        self._completer_model = QStringListModel(names, self)
        self._completer = QCompleter(self._completer_model, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.activated.connect(self._on_completer_activated)
        self._input.setCompleter(self._completer)

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
        lower_name = name.lower()
        match = next((n for n in self._selected if n.lower() == lower_name), None)
        if match:
            self._selected.remove(match)
            self._rebuild_tags()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                ProcessTagInput._clear_layout(item.layout())

    def _rebuild_tags(self):
        self._clear_layout(self._tags_layout)

        if not self._selected:
            hint = QLabel("Пока не выбрано ни одного процесса")
            hint.setStyleSheet(
                f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent; padding: 4px 0;"
            )
            self._tags_layout.addWidget(hint)
            return

        row = QHBoxLayout()
        row.setSpacing(6)
        row.setContentsMargins(0, 0, 0, 0)

        for name in self._selected:
            tag = QFrame()
            tag.setStyleSheet(f"""
                QFrame {{
                    background: {COLOR_BG_SURFACE};
                    border-radius: 6px;
                }}
            """)
            tag_layout = QHBoxLayout(tag)
            tag_layout.setContentsMargins(10, 4, 4, 4)
            tag_layout.setSpacing(6)

            lbl = QLabel(name)
            lbl.setStyleSheet(
                f"color: {COLOR_TEXT_PRIMARY}; font-size: 12px; background: transparent;"
            )
            tag_layout.addWidget(lbl)

            rm_btn = QPushButton("✕")
            rm_btn.setFixedSize(18, 18)
            rm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            rm_btn.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    color: {COLOR_TEXT_MUTED};
                    font-size: 11px;
                    border-radius: 9px;
                }}
                QPushButton:hover {{
                    background: #c0392b;
                    color: #ffffff;
                }}
            """)
            rm_btn.clicked.connect(lambda _=None, n=name: self._remove_tag(n))
            tag_layout.addWidget(rm_btn)

            row.addWidget(tag)

        row.addStretch()
        self._tags_layout.addLayout(row)

    def set_tracked(self, names: list[str]):
        seen: set[str] = set()
        deduped: list[str] = []
        for n in names:
            if n.lower() not in seen:
                seen.add(n.lower())
                deduped.append(n)
        self._selected = deduped
        self._rebuild_tags()

    def get_tracked(self) -> list[str]:
        return list(self._selected)