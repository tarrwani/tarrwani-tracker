import time

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy, QMessageBox,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from config import (
    COLOR_BG_PRIMARY, COLOR_BG_CARD, COLOR_BG_SURFACE,
    COLOR_ACCENT, COLOR_ACCENT_HOVER,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED,
    COLOR_SCROLLBAR_TRACK, COLOR_SCROLLBAR_THUMB, COLOR_SCROLLBAR_HOVER,
    GRID_SPACING, ASSETS_DIR,
)
from core.timer_engine import TimerEngine
from core.process_tracker import ProcessTracker
from ui.widgets.project_card import ProjectCard
from ui.widgets.active_timer_card import ActiveTimerCard
from ui.pages.project_edit_page import ProjectEditPage


class FocusPage(QWidget):
    """Top-level 'Focus Periods' page with an internal stacked layout."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects: list[dict] = []
        self._edit_index: int | None = None   # None → new project
        self._running_index: int | None = None  # index of project whose timer is running

        self._engine = TimerEngine(self)
        self._engine.sig_tick.connect(self._on_engine_tick)
        self._engine.sig_finished.connect(self._on_engine_finished)

        self._proc_tracker: ProcessTracker | None = None
        self._session_accumulator: dict[str, int] = {}

        self._setup_ui()

    @property
    def projects(self) -> list[dict]:
        return self._projects

    # ── Build ──────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Two "sub-pages" shown/hidden manually (simpler than QStackedWidget
        # because we want the edit page to always fill the full content area)
        self._list_view = self._build_list_view()
        self._edit_view = ProjectEditPage()
        self._edit_view.sig_save.connect(self._on_project_saved)
        self._edit_view.sig_cancel.connect(self._show_list)
        self._edit_view.hide()

        root.addWidget(self._list_view)
        root.addWidget(self._edit_view)

    # ── List view ──────────────────────────────────────────────
    def _build_list_view(self) -> QWidget:
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_header())

        # ── Active timer card (hidden until a timer is started) ──
        self._active_card_wrap = QWidget()
        self._active_card_wrap.setStyleSheet("background: transparent;")
        active_wrap_layout = QVBoxLayout(self._active_card_wrap)
        active_wrap_layout.setContentsMargins(24, 20, 24, 0)
        active_wrap_layout.setSpacing(0)

        self._active_card = ActiveTimerCard()
        self._active_card.sig_toggle_pause.connect(self._engine.toggle_pause)
        self._active_card.sig_stop.connect(self._on_stop_active)
        active_wrap_layout.addWidget(self._active_card)

        self._active_card_wrap.setVisible(False)
        layout.addWidget(self._active_card_wrap)

        # Scrollable card area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(self._scroll_style())

        self._cards_host = QWidget()
        self._cards_host.setStyleSheet("background: transparent;")
        
        # ЗАМЕНА: Используем вертикальный слой вместо QGridLayout
        self._cards_layout = QVBoxLayout(self._cards_host)
        self._cards_layout.setContentsMargins(24, 20, 24, 24)
        self._cards_layout.setSpacing(GRID_SPACING)
        self._cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # Не дает карточкам растягиваться по высоте

        # Empty-state label (shown when no projects)
        self._empty_lbl = self._build_empty_state()
        self._empty_lbl.setVisible(True)
        self._cards_layout.addWidget(self._empty_lbl)

        scroll.setWidget(self._cards_host)
        layout.addWidget(scroll, stretch=1)

        return container

    def _build_header(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(60)
        bar.setStyleSheet(f"background: {COLOR_BG_CARD};")

        row = QHBoxLayout(bar)
        row.setContentsMargins(24, 0, 24, 0)
        row.setSpacing(12)

        title = QLabel("Периоды фокусировки")
        title.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 17px; font-weight: 600;"
            " background: transparent;"
        )
        row.addWidget(title)
        row.addStretch()

        add_btn = QPushButton("+ Новый проект")
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
                padding: 0 18px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        add_btn.clicked.connect(self._open_create)
        row.addWidget(add_btn)

        return bar

    def _build_empty_state(self) -> QWidget:
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        w.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QVBoxLayout(w)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel("⏳")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px; background: transparent;")
        layout.addWidget(icon_lbl)

        title = QLabel("Нет проектов")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 16px; font-weight: 600;"
            " background: transparent;"
        )
        layout.addWidget(title)

        desc = QLabel(
            "Создайте первый проект, чтобы начать отслеживать\n"
            "периоды концентрации и перерывы."
        )
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 13px; background: transparent;"
        )
        layout.addWidget(desc)

        cta = QPushButton("Создать проект")
        cta.setCursor(Qt.CursorShape.PointingHandCursor)
        cta.setFixedSize(160, 40)
        cta.setStyleSheet(f"""
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        cta.clicked.connect(self._open_create)
        layout.addWidget(cta, alignment=Qt.AlignmentFlag.AlignHCenter)

        return w

    # ── Card list ─────────────────────────────────────────────
    def _rebuild_cards(self) -> None:
        """Clear and rebuild the card list from self._projects."""
        # Remove old cards (skip empty-state widget)
        while self._cards_layout.count():
            item = self._cards_layout.takeAt(0)
            if item.widget() and item.widget() is not self._empty_lbl:
                item.widget().deleteLater()

        has_projects = bool(self._projects)
        self._empty_lbl.setVisible(not has_projects)

        if not has_projects:
            self._cards_layout.addWidget(self._empty_lbl)
            return

        # ЗАМЕНА: Больше никаких колонок. Добавляем карточки просто друг за другом
        for i, project in enumerate(self._projects):
            card = ProjectCard(project, i)
            card.sig_edit.connect(self._open_edit)
            card.sig_delete.connect(self._confirm_delete)
            card.sig_start.connect(self._on_start)
            card.set_locked(self._engine.is_running and i != self._running_index)
            self._cards_layout.addWidget(card)

    # ── Navigation ────────────────────────────────────────────
    def _show_list(self) -> None:
        self._edit_view.hide()
        self._list_view.show()

    def _show_edit(self) -> None:
        self._list_view.hide()
        self._edit_view.show()

    def _open_create(self) -> None:
        self._edit_index = None
        self._edit_view.load_project(None)
        self._show_edit()

    def _open_edit(self, index: int) -> None:
        self._edit_index = index
        self._edit_view.load_project(self._projects[index])
        self._show_edit()

    # ── Project CRUD ──────────────────────────────────────────
    def _on_project_saved(self, project: dict) -> None:
        if self._edit_index is None:
            self._projects.append(project)
        else:
            self._projects[self._edit_index] = project
        self._rebuild_cards()
        self._show_list()

    def _confirm_delete(self, index: int) -> None:
        name = self._projects[index].get("name", "проект")
        box = QMessageBox(self)
        box.setWindowTitle("Удалить проект")
        box.setText(f"Удалить «{name}»?")
        box.setInformativeText("Это действие нельзя отменить.")
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        box.setDefaultButton(QMessageBox.StandardButton.Cancel)
        box.setStyleSheet(f"""
            QMessageBox {{
                background: {COLOR_BG_CARD};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLabel {{ color: {COLOR_TEXT_PRIMARY}; background: transparent; }}
            QPushButton {{
                background: {COLOR_BG_SURFACE};
                color: {COLOR_TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT}; color: white; }}
        """)
        if box.exec() == QMessageBox.StandardButton.Yes:
            if self._running_index == index:
                # Don't allow deleting the project whose timer is running.
                return
            self._projects.pop(index)
            if self._running_index is not None and self._running_index > index:
                self._running_index -= 1
            self._rebuild_cards()

    # ── Timer engine integration ───────────────────────────────
    def _on_start(self, index: int) -> None:
        if self._engine.is_running:
            return  # a timer is already running; start buttons should be locked anyway

        self._running_index = index
        project = self._projects[index]

        self._active_card.update_state({
            "running": True,
            "project": project,
            "phase": "focus",
            "cycle": 1,
            "total_cycles": max(1, int(project.get("cycles", 1))),
            "breaks_done": 0,
            "total_breaks": max(0, int(project.get("cycles", 1)) - 1),
            "phase_total": max(1, int(project.get("focus_min", 25))) * 60,
            "phase_remaining": max(1, int(project.get("focus_min", 25))) * 60,
            "is_paused": False,
            "is_afk_paused": False,
        })
        self._active_card_wrap.setVisible(True)

        self._lock_other_cards(index)
        self._engine.start(project)
        self._start_process_tracking(project)

    def _start_process_tracking(self, project: dict) -> None:
        tracked = project.get("tracked_processes", [])
        if not tracked:
            return
        self._proc_tracker = ProcessTracker(tracked, self)
        self._proc_tracker.sig_tick.connect(self._on_proc_tracker_tick)
        self._proc_tracker.start()

    def _on_proc_tracker_tick(self, log: dict) -> None:
        merged = dict(self._session_accumulator)
        for name, secs in log.items():
            merged[name] = merged.get(name, 0) + secs
        self._active_card.update_process_log(merged)

    def _stop_process_tracking(self, save_to_project: bool = True) -> dict:
        if self._proc_tracker is not None:
            partial = self._proc_tracker.stop()
            self._proc_tracker.deleteLater()
            self._proc_tracker = None
            for name, secs in partial.items():
                self._session_accumulator[name] = self._session_accumulator.get(name, 0) + secs
        log = dict(self._session_accumulator)
        if save_to_project and self._running_index is not None:
            project = self._projects[self._running_index]
            sessions = project.setdefault("sessions", [])
            planned_secs = (
                int(project.get("focus_min", 25)) * 60
                * int(project.get("cycles", 1))
            )
            sessions.append({
                "process_log": log,
                "timestamp": time.time(),
                "project_name": project.get("name", ""),
                "planned_secs": planned_secs,
            })
        self._session_accumulator.clear()
        return log

    def _on_stop_active(self) -> None:
        self._engine.stop()
        self._stop_process_tracking()
        self._active_card_wrap.setVisible(False)
        self._running_index = None
        self._unlock_all_cards()

    def _on_engine_tick(self, state: dict) -> None:
        if not state.get("running", False):
            return
        self._active_card.update_state(state)
        if self._proc_tracker:
            paused = state.get("is_paused", False) or state.get("is_afk_paused", False)
            if paused:
                self._proc_tracker.pause()
            else:
                self._proc_tracker.resume()

    def _on_engine_finished(self) -> None:
        project = self._projects[self._running_index] if self._running_index is not None else {}
        name = project.get("name", "проект")

        self._stop_process_tracking()
        self._active_card_wrap.setVisible(False)
        self._running_index = None
        self._unlock_all_cards()

        box = QMessageBox(self)
        box.setWindowTitle("Таймер завершён")
        box.setText(f"«{name}» — все циклы завершены! 🎉")
        box.setStandardButtons(QMessageBox.StandardButton.Ok)
        box.setStyleSheet(f"""
            QMessageBox {{
                background: {COLOR_BG_CARD};
                color: {COLOR_TEXT_PRIMARY};
            }}
            QLabel {{ color: {COLOR_TEXT_PRIMARY}; background: transparent; }}
            QPushButton {{
                background: {COLOR_ACCENT};
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 6px 18px;
                font-size: 13px;
            }}
            QPushButton:hover {{ background: {COLOR_ACCENT_HOVER}; }}
        """)
        box.exec()

    # ── Card locking ────────────────────────────────────────────
    def _lock_other_cards(self, running_index: int) -> None:
        for i in range(self._cards_layout.count()):
            widget = self._cards_layout.itemAt(i).widget()
            if isinstance(widget, ProjectCard):
                widget.set_locked(widget._index != running_index)

    def _unlock_all_cards(self) -> None:
        for i in range(self._cards_layout.count()):
            widget = self._cards_layout.itemAt(i).widget()
            if isinstance(widget, ProjectCard):
                widget.set_locked(False)

    # ── Window state ────────────────────────────────────────────
    def _on_window_minimized(self, minimized: bool) -> None:
        if not self._engine.is_running:
            return
        if minimized:
            self._stop_process_tracking(save_to_project=False)
            self._active_card_wrap.setVisible(False)
        else:
            project = self._projects[self._running_index] if self._running_index is not None else {}
            if project:
                self._start_process_tracking(project)
                self._active_card_wrap.setVisible(True)

    # ── Styles ────────────────────────────────────────────────
    def _scroll_style(self) -> str:
        return f"""
            QScrollArea {{ background: transparent; border: none; }}
            QScrollBar:vertical {{
                background: {COLOR_SCROLLBAR_TRACK};
                width: 6px;
                border-radius: 3px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {COLOR_SCROLLBAR_THUMB};
                border-radius: 3px;
                min-height: 24px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {COLOR_SCROLLBAR_HOVER}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """