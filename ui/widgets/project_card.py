from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsDropShadowEffect,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor

from config import (
    COLOR_BG_CARD, COLOR_BG_SURFACE, COLOR_BG_SURFACE_HOVER,
    COLOR_ACCENT, COLOR_ACCENT_HOVER, COLOR_ACCENT_DISABLED,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_TEXT_MUTED, COLOR_TEXT_DISABLED,
    CARD_BORDER_R,
    SHADOW_BLUR_NORMAL, SHADOW_OFFSET_NORMAL, SHADOW_ALPHA_NORMAL,
    SHADOW_BLUR_HOVER,  SHADOW_OFFSET_HOVER,  SHADOW_ALPHA_HOVER,
)


class ProjectCard(QWidget):
    """Компактный элемент вертикального списка проектов (занимает ~95% ширины)."""

    sig_edit   = Signal(int)
    sig_delete = Signal(int)
    sig_start  = Signal(int)

    def __init__(self, project: dict, index: int, parent=None):
        super().__init__(parent)
        self._project = project
        self._index   = index
        self._locked  = False
        
        # Фиксируем небольшую высоту для строчного элемента списка
        self.setFixedHeight(82)
        
        self._setup_ui()
        self._setup_shadow()

    # ── Build ──────────────────────────────────────────────────
    def _setup_ui(self) -> None:
        # Делаем корневой виджет прозрачным, чтобы видеть отступы
        self.setStyleSheet("background: transparent;")
        
        # Главный контейнер задает отступы по краям (создает эффект 95% ширины в списке)
        # и небольшие отступы сверху/снизу между соседними карточками
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(24, 4, 24, 4)
        main_layout.setSpacing(0)

        # Внутренняя панель — сама визуальная карточка с фоном и скруглением
        self.card_frame = QFrame(self)
        self.card_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLOR_BG_CARD};
                border-radius: {CARD_BORDER_R}px;
            }}
        """)
        
        # Горизонтальный слой внутри карточки для разделения на логические зоны
        card_layout = QHBoxLayout(self.card_frame)
        card_layout.setContentsMargins(16, 0, 16, 0)
        card_layout.setSpacing(20)

        # ── Группа 1: Основная информация (Название + Баджи) ──
        info_zone = QVBoxLayout()
        info_zone.setSpacing(6)
        info_zone.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        name_lbl = QLabel(self._project.get("name", "Без названия"))
        name_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_PRIMARY}; font-size: 14px; font-weight: 600;"
            " background: transparent;"
        )
        name_lbl.setWordWrap(False)  # В строчном режиме лучше держать в одну строку
        info_zone.addWidget(name_lbl)

        # Строка баджей
        badges = QHBoxLayout()
        badges.setSpacing(6)
        badges.setContentsMargins(0, 0, 0, 0)

        if self._project.get("afk_tracking", False):
            badges.addWidget(self._badge("AFK", COLOR_ACCENT))

        scripts = self._project.get("scripts", {})
        active  = sum(1 for v in scripts.values() if v.strip())
        if active:
            badges.addWidget(self._badge(f"⚡ {active} скр.", "#5a4a20"))
        
        badges.addStretch()
        info_zone.addLayout(badges)

        # ── Группа 2: Тайминги и циклы (Метрики посередине) ──
        metrics_zone = QVBoxLayout()
        metrics_zone.setSpacing(4)
        metrics_zone.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        focus_min = self._project.get("focus_min", 25)
        break_min = self._project.get("break_min", 5)
        cycles    = self._project.get("cycles", 4)

        time_lbl = QLabel(f"🎯 {focus_min}м  ·  ☕ {break_min}м")
        time_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_SECONDARY}; font-size: 12px; background: transparent;"
        )
        metrics_zone.addWidget(time_lbl)

        c_word = "цикл" if cycles == 1 else ("цикла" if 2 <= cycles <= 4 else "циклов")
        cycles_lbl = QLabel(f"🔁 {cycles} {c_word}")
        cycles_lbl.setStyleSheet(
            f"color: {COLOR_TEXT_MUTED}; font-size: 12px; background: transparent;"
        )
        metrics_zone.addWidget(cycles_lbl)

        # ── Группа 3: Действия (Кнопки управления справа) ──
        btn_zone = QHBoxLayout()
        btn_zone.setSpacing(8)
        btn_zone.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        edit_btn = self._make_btn(
            "Изменить",
            bg=COLOR_BG_SURFACE,
            hover=COLOR_BG_SURFACE_HOVER,
            slot=lambda: self.sig_edit.emit(self._index),
        )
        del_btn = self._make_btn(
            "✕",
            bg="#2e1a1a",
            hover="#c0392b",
            text_color="#e57373",
            fixed_w=36,
            slot=lambda: self.sig_delete.emit(self._index),
        )
        self._start_btn = self._make_btn(
            "▶  Старт",
            bg=COLOR_ACCENT,
            hover=COLOR_ACCENT_HOVER,
            text_color="#ffffff",
            slot=lambda: self.sig_start.emit(self._index),
        )

        btn_zone.addWidget(edit_btn)
        btn_zone.addWidget(del_btn)
        btn_zone.addWidget(self._start_btn)

        # Распределяем зоны внутри карточки по пропорциям (Инфо : Метрики : Кнопки)
        card_layout.addLayout(info_zone, stretch=4)
        card_layout.addLayout(metrics_zone, stretch=3)
        card_layout.addLayout(btn_zone, stretch=0)

        # Добавляем готовую карточку в главный упаковочный слой виджета
        main_layout.addWidget(self.card_frame)

    def _badge(self, text: str, bg: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            f"background: {bg}22; color: {bg}; border-radius: 4px;"
            " font-size: 10px; padding: 1px 6px; font-weight: 500;"
        )
        return lbl

    def _make_btn(
        self, text: str, bg: str, hover: str,
        text_color: str = None,
        fixed_w: int = None,
        slot=None,
    ) -> QPushButton:
        tc = text_color or COLOR_TEXT_PRIMARY
        btn = QPushButton(text)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg};
                color: {tc};
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background: {hover}; }}
            QPushButton:disabled {{
                background: {COLOR_ACCENT_DISABLED};
                color: {COLOR_TEXT_DISABLED};
            }}
        """)
        if fixed_w:
            btn.setFixedWidth(fixed_w)
        if slot:
            btn.clicked.connect(slot)
        return btn

    # ── Lock state ─────────────────────────────────────────────
    def set_locked(self, locked: bool) -> None:
        if self._locked == locked:
            return
        self._locked = locked
        self._start_btn.setDisabled(locked)
        self._start_btn.setText("⏳ Занято" if locked else "Старт")
        self._start_btn.setCursor(
            Qt.CursorShape.ForbiddenCursor if locked else Qt.CursorShape.PointingHandCursor
        )

    # ── Shadow & Hover ─────────────────────────────────────────
    def _setup_shadow(self) -> None:
        # Применяем эффект тени непосредственно к внутренней панели QFrame, а не ко всему виджету
        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        self._shadow.setOffset(0, SHADOW_OFFSET_NORMAL)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_NORMAL))
        self.card_frame.setGraphicsEffect(self._shadow)

    def enterEvent(self, event) -> None:
        self._shadow.setBlurRadius(SHADOW_BLUR_HOVER)
        self._shadow.setOffset(0, SHADOW_OFFSET_HOVER)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_HOVER))
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._shadow.setBlurRadius(SHADOW_BLUR_NORMAL)
        self._shadow.setOffset(0, SHADOW_OFFSET_NORMAL)
        self._shadow.setColor(QColor(0, 0, 0, SHADOW_ALPHA_NORMAL))
        super().leaveEvent(event)