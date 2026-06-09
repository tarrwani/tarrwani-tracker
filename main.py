import sys
from PyQt6.QtWidgets import QApplication
from ui.tray import TrayIcon


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # не закрываться когда окно закрыто

    def on_open():
        print("Открыть главное окно")  # потом заменим на реальное окно

    def on_quit():
        app.quit()

    tray = TrayIcon(app, on_open=on_open, on_quit=on_quit)
    tray.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()