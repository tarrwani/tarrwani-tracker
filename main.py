import sys
from PyQt6.QtWidgets import QApplication
from ui.tray import TrayIcon
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()

    def on_open():
        window.show()
        window.activateWindow()

    def on_quit():
        app.quit()

    tray = TrayIcon(app, on_open=on_open, on_quit=on_quit)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()