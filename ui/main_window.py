from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget, QLabel
from PySide6.QtCore import Qt
from ui.views.timer_view import TimerView
from ui.views.stat_view import StatView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tarrwani Tracker")
        self.resize(700, 550)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        # Sidebar
        sidebar = QWidget()
        sidebar.setMinimumWidth(100)
        sidebar.setMaximumWidth(300)
        # Sidebar buttons
        self.timer_btn = QPushButton("🕒")
        self.timer_btn.clicked.connect(lambda: self.switch_view(0, self.timer_btn))

        self.stat_btn = QPushButton("📊")
        self.stat_btn.clicked.connect(lambda: self.switch_view(1, self.stat_btn))
        # Sidebar layout
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.timer_btn)
        sidebar_layout.addWidget(self.stat_btn)
        sidebar.setLayout(sidebar_layout)

        # Content container
        self.content = QStackedWidget()
        self.timer_view = TimerView()
        self.stat_view = StatView()

        self.content.addWidget(self.timer_view) # 0
        self.content.addWidget(self.stat_view) # 1

        layout = QHBoxLayout()
        layout.addWidget(sidebar)
        layout.addStretch()
        layout.addWidget(self.content)
        central_widget.setLayout(layout)

    def switch_view(self, index, active_btn):
        self.timer_btn.setChecked(False)
        self.stat_btn.setChecked(False)
        active_btn.setChecked(True)
        self.content.setCurrentIndex(index)