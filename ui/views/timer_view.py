from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout,
    QScrollArea, QPushButton,
)
from PySide6.QtCore import Qt

from ui.widgets.timer_card import TimerCard
from ui.widgets.timer_dialog import TimerDialog
from config import (
    ADD_BTN_SIZE, ADD_BTN_RADIUS,
    CARD_MIN_WIDTH, GRID_SPACING,
    settings_manager,
)


class TimerView(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # ── Scroll area ───────────────────────────────────────
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setAcceptDrops(True)

        self.grid = QGridLayout(self._container)
        self.grid.setSpacing(GRID_SPACING)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self._columns: int = 2
        self._cards: list[TimerCard] = []

        # Populate from live user settings (not the frozen flat constant)
        for label, seconds in settings_manager.settings.timer_presets:
            self._add_card(TimerCard(label, seconds))

        # ── Add button ────────────────────────────────────────
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(ADD_BTN_SIZE, ADD_BTN_SIZE)
        self.add_btn.clicked.connect(self._on_add_clicked)

        self._scroll.setWidget(self._container)
        main_layout.addWidget(self._scroll)
        main_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignRight)

        self._apply_styles()

    # ── Theming ───────────────────────────────────────────────

    def _apply_styles(self) -> None:
        t = settings_manager.theme

        self._scroll.setStyleSheet(f"""
            QScrollArea {{
                border: none;
                background: transparent;
            }}
            QScrollBar:vertical {{
                border: none;
                background: {t.scrollbar_bg};
                width: 7px;
                margin: 0px;
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical {{
                border: none;
                background: {t.scrollbar_thumb};
                min-height: 20px;
                border-radius: 0px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {t.scrollbar_hover}; }}
            QScrollBar::sub-page:vertical     {{ background: {t.scrollbar_track}; }}
            QScrollBar::add-page:vertical     {{ background: {t.scrollbar_track}; }}
            QScrollBar::sub-line:vertical     {{ height: 0px; background: none; }}
            QScrollBar::add-line:vertical     {{ height: 0px; background: none; }}
        """)

        self.add_btn.setStyleSheet(f"""
            QPushButton {{
                border-radius: {ADD_BTN_RADIUS}px;
                background-color: {t.accent};
                color: {t.text_primary};
                font-size: 20px;
            }}
            QPushButton:hover {{ background-color: {t.accent_hover}; }}
        """)

    def refresh_theme(self) -> None:
        """Hot-reload colours on all cards and self."""
        self._apply_styles()
        for card in self._cards:
            card.refresh_theme()

    # ── Card management ───────────────────────────────────────

    def _add_card(self, card: TimerCard) -> None:
        card.favoriteChanged.connect(self._on_favorite_changed)
        self._cards.append(card)
        self._rebuild_grid()

    def _rebuild_grid(self) -> None:
        # Detach all widgets without destroying them
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        ordered = (
            [c for c in self._cards if c.is_favorite()]
            + [c for c in self._cards if not c.is_favorite()]
        )
        for idx, card in enumerate(ordered):
            row, col = divmod(idx, self._columns)
            card.setParent(self._container)
            self.grid.addWidget(card, row, col)
            card.show()

    def _on_favorite_changed(self, card: TimerCard) -> None:
        self._rebuild_grid()

    def _on_add_clicked(self) -> None:
        dialog = TimerDialog(self)
        if dialog.exec():
            name, seconds = dialog.get_values()
            self._add_card(TimerCard(name, seconds))

    # ── Drag & Drop ───────────────────────────────────────────

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasText() and event.mimeData().text() == "timer_card":
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        event.acceptProposedAction()
        pos        = event.position().toPoint()
        bar        = self._scroll.verticalScrollBar()
        margin     = 40
        viewport_h = self._scroll.viewport().height()
        if pos.y() < margin:
            bar.setValue(bar.value() - 12)
        elif pos.y() > viewport_h - margin:
            bar.setValue(bar.value() + 12)

    def dropEvent(self, event) -> None:
        source: TimerCard = event.source()
        if source not in self._cards:
            event.ignore()
            return

        drop_pos    = self._container.mapFromGlobal(
            self.mapToGlobal(event.position().toPoint())
        )
        target = self._card_at(drop_pos)
        if target is None or target is source:
            event.ignore()
            return

        si, ti = self._cards.index(source), self._cards.index(target)
        self._cards[si], self._cards[ti] = self._cards[ti], self._cards[si]
        self._rebuild_grid()
        event.acceptProposedAction()

    def _card_at(self, pos) -> "TimerCard | None":
        for card in self._cards:
            if card.geometry().contains(pos):
                return card
        return None

    # ── Responsive columns ────────────────────────────────────

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        new_cols = self._columns_for_width(self.width())
        if new_cols != self._columns:
            self._columns = new_cols
            self._rebuild_grid()

    def _columns_for_width(self, width: int) -> int:
        pad = 32
        for cols in range(4, 0, -1):
            needed = CARD_MIN_WIDTH * cols + GRID_SPACING * (cols - 1) + pad
            if width >= needed:
                return cols
        return 1