from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .theme.palette import ThemeManager
from .theme.typography import Font
from .window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)

    app.setFont(Font.mono(13))
    app.setStyle("Fusion")

    theme = ThemeManager()
    app.setStyleSheet(theme.stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
