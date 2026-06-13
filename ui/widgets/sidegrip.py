
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

class SideGrip(QWidget):
    """Специальный невидимый виджет-перехватчик для изменения размера окна за края"""
    def __init__(self, parent, position: str, cursor_shape: Qt.CursorShape):
        super().__init__(parent)
        self.position = position
        self.setCursor(cursor_shape)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # Передаем в главное окно команду на старт ресайза и точку клика
            self.window()._start_resize(self.position, event.globalPosition().toPoint())
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.window()._drag_resize(event.globalPosition().toPoint())
            event.accept()