"""Entry point: build QApplication, apply global theme, show main window."""

import sys

from PyQt5.QtWidgets import QApplication

from src.main_window import MainWindow
from src.theme import build_app_icon, build_stylesheet


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("CodeDex Pro")
    app.setOrganizationName("NYTEMODE")
    app.setWindowIcon(build_app_icon())
    app.setStyleSheet(build_stylesheet())

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
