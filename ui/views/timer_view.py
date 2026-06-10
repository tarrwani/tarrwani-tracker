from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QScrollArea, QPushButton
)
from PySide6.QtCore import Qt
from ui.widgets.timer_card import TimerCard
from ui.widgets.timer_dialog import TimerDialog

class TimerView(QWidget):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        self._scroll = scroll
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1e1e24;
                width: 7px;
                margin: 0px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical {
                border: none;
                background: #444454;
                min-height: 20px;
                border-radius: 0px;
            }
            QScrollBar::handle:vertical:hover { background: #575770; }
            QScrollBar::sub-page:vertical { background: #252530; }
            QScrollBar::add-page:vertical  { background: #252530; }
            QScrollBar::sub-line:vertical  { height: 0px; background: none; }
            QScrollBar::add-line:vertical  { height: 0px; background: none; }
        """)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._container.setAcceptDrops(True)
        self.grid = QGridLayout(self._container)
        self.grid.setSpacing(16)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self._columns = 2

        self._cards: list[TimerCard] = []

        presets = [
            ("1 минута",  60),
            ("3 минуты",  180),
            ("5 минут",   300),
            ("10 минут",  600),
        ]
        for label, seconds in presets:
            self._add_card_widget(TimerCard(label, seconds))

        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(36, 36)
        self.add_btn.clicked.connect(self._on_add_clicked)
        self.add_btn.setStyleSheet("""
            QPushButton { border-radius: 18px; background-color: #1D9E75; color: #ffffff; font-size: 20px; }
            QPushButton:hover { background-color: #17835f; }
        """)

        scroll.setWidget(self._container)
        main_layout.addWidget(scroll)
        main_layout.addWidget(self.add_btn, alignment=Qt.AlignmentFlag.AlignRight)

    # ── Вспомогательные методы ─────────────────────────────────
    def _add_card_widget(self, card: TimerCard):
        """Регистрирует карточку и перестраивает сетку."""
        card.favoriteChanged.connect(self._on_favorite_changed)
        self._cards.append(card)
        self._rebuild_grid()

    def _rebuild_grid(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().setParent(None)

        favorites = [c for c in self._cards if c.is_favorite()]
        others    = [c for c in self._cards if not c.is_favorite()]
        ordered   = favorites + others

        for idx, card in enumerate(ordered):
            row, col = divmod(idx, self._columns)
            col_span = 1
            # Если карточка последняя и одна в строке — растянуть
            if col == 0 and idx == len(ordered) - 1:
                col_span = self._columns
            card.setParent(self._container)
            self.grid.addWidget(card, row, col, 1, col_span)
            card.show()

    def _on_favorite_changed(self, card: TimerCard):
        self._rebuild_grid()

    def _on_add_clicked(self):
        dialog = TimerDialog(self)
        if dialog.exec():
            name, seconds = dialog.get_values()
            self._add_card_widget(TimerCard(name, seconds))

    # Drag & Drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text() == "timer_card":
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()
        pos = event.position().toPoint()
        viewport_h = self._scroll.viewport().height()
        bar = self._scroll.verticalScrollBar()
        margin = 40
        if pos.y() < margin:
            bar.setValue(bar.value() - 12)
        elif pos.y() > viewport_h - margin:
            bar.setValue(bar.value() + 12)

    def dropEvent(self, event):
        source_card: TimerCard = event.source()
        if source_card not in self._cards:
            event.ignore()
            return

        # Находим карточку под курсором
        drop_pos = self._container.mapFromGlobal(
            self.mapToGlobal(event.position().toPoint())
        )
        target_card = self._card_at(drop_pos)

        if target_card is None or target_card is source_card:
            event.ignore()
            return

        # Меняем местами в списке
        si = self._cards.index(source_card)
        ti = self._cards.index(target_card)
        self._cards[si], self._cards[ti] = self._cards[ti], self._cards[si]

        self._rebuild_grid()
        event.acceptProposedAction()

    def _card_at(self, pos) -> "TimerCard | None":
        """Возвращает карточку, чей прямоугольник содержит pos (в координатах контейнера)."""
        for card in self._cards:
            if card.geometry().contains(pos):
                return card
        return None
    
    def _columns_for_width(self, width: int) -> int:
            if width < 220 * 2 + 16 + 32:
                return 1
            elif width < 220 * 3 + 16 * 2 + 32:
                return 2
            elif width < 220 * 4 + 16 * 3 + 32:
                return 3
            else:
                return 4

    def resizeEvent(self, event):
        super().resizeEvent(event)
        new_cols = self._columns_for_width(self.width())
        if new_cols != self._columns:
            self._columns = new_cols
            self._rebuild_grid()