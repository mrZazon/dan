from __future__ import annotations

import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from .theme import Nord
from .window import MainWindow

STYLESHEET = f"""
QMainWindow, QDialog {{ background-color: {Nord.bg_0}; }}
QToolTip {{
    background: {Nord.bg_2}; color: {Nord.fg_0};
    border: 1px solid {Nord.border}; border-radius: 4px;
    padding: 6px 10px; font-size: 12px;
}}
QScrollBar:vertical {{
    background: transparent; width: 8px; margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {Nord.border}; min-height: 30px;
    border-radius: 4px; margin: 2px;
}}
QScrollBar::handle:vertical:hover {{
    background: {Nord.fg_3};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{ height: 0; }}
QMenuBar {{
    background: {Nord.bg_0}; border: none; padding: 2px 0;
}}
QMenuBar::item {{
    color: {Nord.fg_0}; padding: 4px 12px; border-radius: 4px;
}}
QMenuBar::item:selected {{ background: {Nord.bg_2}; }}
QMenu {{
    background: {Nord.bg_1}; border: 1px solid {Nord.border};
    border-radius: 6px; padding: 4px;
}}
QMenu::item {{
    color: {Nord.fg_0}; padding: 6px 24px; border-radius: 4px;
}}
QMenu::item:selected {{ background: {Nord.accent}; color: {Nord.fg_0}; }}
QMenu::separator {{
    height: 1px; background: {Nord.border}; margin: 4px 12px;
}}
QStatusBar {{
    background: {Nord.bg_1}; border-top: 1px solid {Nord.border};
    color: {Nord.fg_2}; font-size: 11px; padding: 2px 12px;
}}
QStatusBar::item {{ border: none; }}
QPushButton {{
    background: {Nord.accent}; color: {Nord.fg_0};
    border: none; border-radius: 6px;
    padding: 8px 20px; font-weight: 500; font-size: 13px;
}}
QPushButton:hover {{ background: {Nord.accent_light}; }}
QPushButton:pressed {{ background: {Nord.accent_dark}; }}
QPushButton:disabled {{ background: {Nord.border}; color: {Nord.fg_3}; }}
"""


def main() -> None:
    app = QApplication(sys.argv)

    font = QFont(Nord.ui_font, 13)
    font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    app.setFont(font)

    app.setStyle("Fusion")
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
