import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QSlider, QMainWindow
from PySide6.QtGui import QPainter, QPen, QColor, QFont
from PySide6.QtCore import Qt, QRectF

class CircularProgressBar(QWidget):
    def __init__(self):
        super().__init__()
        self._value = 100  # Текущий процент заполнения (от 0 до 100)
        self.setFixedSize(200, 200) # Задаем фиксированный размер окна под круг

    def set_value(self, value):
        # Ограничиваем значение в пределах 0-100
        self._value = max(0, min(100, value))
        # Метод update() принудительно заставляет Qt вызвать paintEvent и перерисовать круг
        self.update()

    def paintEvent(self, event):
        """Этот метод вызывается автоматически каждый раз, когда нужно перерисовать виджет"""
        painter = QPainter(self)
        
        # Включаем сглаживание, чтобы края круга не были пиксельными («лесенкой»)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Вычисляем квадрат, внутри которого будет рисоваться круг (с учетом отступов для толщины линии)
        thickness = 8
        rect = QRectF(thickness, thickness, self.width() - thickness*2, self.height() - thickness*2)

        # 1. РИСУЕМ ЗАДНИЙ ФОН КРУГА (серый пустой трек) — аналог stroke="#888780"
        bg_pen = QPen(QColor("#2d2d3a"), thickness)
        painter.setPen(bg_pen)
        painter.drawEllipse(rect) # Рисуем ровный фоновый круг

        # 2. РИСУЕМ АКТИВНУЮ ПОЛОСУ (зеленая заполняющая дуга) — аналог вашего stroke="#1D9E75"
        if self._value > 0:
            active_pen = QPen(QColor("#1D9E75"), thickness)
            # stroke-linecap="round" превращается в:
            active_pen.setCapStyle(Qt.PenCapStyle.RoundCap) 
            painter.setPen(active_pen)

            # Переводим проценты в углы Qt:
            # Стартуем сверху (90 градусов * 16)
            start_angle = 90 * 16 
            
            # Считаем угол заполнения. Знак минус пускает анимацию ПО часовой стрелке.
            # Формула: (процент / 100) * 360 градусов * 16 логарифмических долей
            span_angle = int(-(self._value / 100.0) * 360 * 16)

            # Рисуем дугу поверх серого круга
            painter.drawArc(rect, start_angle, span_angle)

        # 3. РИСУЕМ ТЕКСТ ВНУТРИ КРУГА (например, проценты или секунды)
        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        # Выводим текст ровно по центру нашего квадрата
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, f"{int(self._value)}%")


# --- Пример использования в окне ---
class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1c1c24;")
        self.resize(300, 350)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Создаем наш круглый прогресс-бар
        self.progress = CircularProgressBar()
        layout.addWidget(self.progress)

        # Создаем ползунок (слайдер), чтобы вы могли мышкой потестировать заполнение
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(100)
        # При движении ползунка меняем значение круга
        self.slider.valueChanged.connect(self.progress.set_value)
        
        layout.addWidget(self.slider)
        self.setCentralWidget(central_widget)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec())